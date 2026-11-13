"""CRUD de produtos (/api/products/), incluindo upload de imagem."""

import io

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from production.models import Product, ProductionLog

URL = "/api/products/"


def detail(pk):
    return f"{URL}{pk}/"


def png(name="foto.png"):
    buffer = io.BytesIO()
    Image.new("RGB", (2, 2), "red").save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


class TestListarEDetalhar:
    def test_lista_sem_paginacao(self, client, make_product):
        make_product(name="Cadeira")
        make_product(name="Mesa")

        response = client.get(URL)

        assert response.status_code == 200
        assert isinstance(response.data, list)
        assert {item["name"] for item in response.data} == {"Cadeira", "Mesa"}

    def test_detalhe_expoe_os_campos_do_contrato(self, client, make_product):
        product = make_product(name="Cadeira", price="150.00", stock=4)

        response = client.get(detail(product.id))

        assert response.status_code == 200
        assert response.data == {
            "id": product.id,
            "name": "Cadeira",
            "price": "150.00",
            "stock": 4.0,
            "image": None,
        }

    def test_detalhe_inexistente_retorna_404(self, client):
        assert client.get(detail(999)).status_code == 404


class TestCriar:
    def test_cria_produto_com_estoque_zero_por_padrao(self, client):
        response = client.post(URL, {"name": "Mesa", "price": "300.00"}, format="json")

        assert response.status_code == 201
        product = Product.objects.get(id=response.data["id"])
        assert product.name == "Mesa"
        assert str(product.price) == "300.00"
        assert product.stock == 0

    def test_nome_e_obrigatorio(self, client):
        response = client.post(URL, {"price": "10.00"}, format="json")

        assert response.status_code == 400
        assert set(response.data) == {"name"}

    def test_preco_invalido_retorna_400(self, client):
        response = client.post(URL, {"name": "Mesa", "price": "caro"}, format="json")

        assert response.status_code == 400
        assert "price" in response.data

    def test_cria_produto_com_imagem(self, client, settings):
        response = client.post(
            URL, {"name": "Mesa", "price": "300.00", "image": png()}, format="multipart"
        )

        assert response.status_code == 201
        product = Product.objects.get(id=response.data["id"])
        assert product.image.name.startswith("products/")
        assert (settings.MEDIA_ROOT / product.image.name).exists()
        # A API devolve a URL absoluta da imagem.
        assert response.data["image"].startswith("http://testserver/media/products/")

    def test_arquivo_que_nao_e_imagem_retorna_400(self, client):
        arquivo = SimpleUploadedFile("foto.png", b"nao sou png", content_type="image/png")

        response = client.post(
            URL, {"name": "Mesa", "image": arquivo}, format="multipart"
        )

        assert response.status_code == 400
        assert "image" in response.data


class TestAtualizarERemover:
    def test_patch_atualiza_somente_o_campo_enviado(self, client, make_product):
        product = make_product(name="Cadeira", price="150.00")

        response = client.patch(detail(product.id), {"price": "175.50"}, format="json")

        assert response.status_code == 200
        product.refresh_from_db()
        assert str(product.price) == "175.50"
        assert product.name == "Cadeira"

    def test_put_substitui_o_registro(self, client, make_product):
        product = make_product(name="Cadeira", price="150.00", stock=2)

        response = client.put(
            detail(product.id),
            {"name": "Cadeira gamer", "price": "900.00", "stock": 1},
            format="json",
        )

        assert response.status_code == 200
        product.refresh_from_db()
        assert (product.name, str(product.price), product.stock) == (
            "Cadeira gamer",
            "900.00",
            1,
        )

    def test_delete_remove_o_registro(self, client, make_product):
        product = make_product()

        response = client.delete(detail(product.id))

        assert response.status_code == 204
        assert not Product.objects.filter(id=product.id).exists()

    def test_delete_remove_ficha_tecnica_e_historico_de_producao(
        self, client, make_product, make_raw_material, make_bom
    ):
        product = make_product()
        material = make_raw_material()
        make_bom(product, material, quantity=1)
        ProductionLog.objects.create(product=product, quantity=1)

        client.delete(detail(product.id))

        assert material.productrawmaterial_set.count() == 0
        assert ProductionLog.objects.count() == 0
