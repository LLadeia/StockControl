"""CRUD de matérias-primas (/api/raw-materials/)."""

from production.models import RawMaterial

URL = "/api/raw-materials/"


def detail(pk):
    return f"{URL}{pk}/"


class TestListarEDetalhar:
    def test_lista_vazia(self, client):
        response = client.get(URL)

        assert response.status_code == 200
        assert response.data == []

    def test_lista_sem_paginacao(self, client, make_raw_material):
        make_raw_material(name="Aço")
        make_raw_material(name="Madeira")

        response = client.get(URL)

        # O front-end espera um array simples, não um objeto paginado.
        assert isinstance(response.data, list)
        assert {item["name"] for item in response.data} == {"Aço", "Madeira"}

    def test_detalhe_expoe_os_campos_do_contrato(self, client, make_raw_material):
        material = make_raw_material(name="Aço", stock=12.5, price="2.50")

        response = client.get(detail(material.id))

        assert response.status_code == 200
        assert response.data == {
            "id": material.id,
            "name": "Aço",
            "stock": 12.5,
            "price": "2.50",
            "image": None,
        }

    def test_detalhe_inexistente_retorna_404(self, client):
        assert client.get(detail(999)).status_code == 404


class TestCriar:
    def test_cria_materia_prima(self, client):
        response = client.post(
            URL, {"name": "Aço", "stock": 40, "price": "3.20"}, format="json"
        )

        assert response.status_code == 201
        material = RawMaterial.objects.get(id=response.data["id"])
        assert material.name == "Aço"
        assert material.stock == 40
        assert str(material.price) == "3.20"

    def test_preco_e_opcional(self, client):
        response = client.post(URL, {"name": "Cola", "stock": 5}, format="json")

        assert response.status_code == 201
        assert response.data["price"] is None

    def test_nome_e_estoque_sao_obrigatorios(self, client):
        response = client.post(URL, {}, format="json")

        assert response.status_code == 400
        assert set(response.data) == {"name", "stock"}

    def test_estoque_nao_numerico_retorna_400(self, client):
        response = client.post(URL, {"name": "Aço", "stock": "muito"}, format="json")

        assert response.status_code == 400
        assert "stock" in response.data

    def test_preco_com_mais_de_duas_casas_retorna_400(self, client):
        response = client.post(
            URL, {"name": "Aço", "stock": 1, "price": "1.234"}, format="json"
        )

        assert response.status_code == 400
        assert "price" in response.data

    def test_estoque_negativo_e_aceito_hoje(self, client):
        """Comportamento atual: a API não valida estoque >= 0.

        Registrado aqui para que uma eventual validação seja uma decisão
        consciente (muda o contrato), não um efeito colateral.
        """
        response = client.post(URL, {"name": "Aço", "stock": -5}, format="json")

        assert response.status_code == 201
        assert response.data["stock"] == -5


class TestAtualizarERemover:
    def test_patch_atualiza_somente_o_campo_enviado(self, client, make_raw_material):
        material = make_raw_material(name="Aço", stock=10, price="2.50")

        response = client.patch(detail(material.id), {"stock": 7.5}, format="json")

        assert response.status_code == 200
        material.refresh_from_db()
        assert material.stock == 7.5
        assert material.name == "Aço"
        assert str(material.price) == "2.50"

    def test_put_substitui_o_registro(self, client, make_raw_material):
        material = make_raw_material(name="Aço", stock=10, price="2.50")

        response = client.put(
            detail(material.id),
            {"name": "Aço inox", "stock": 3, "price": "9.90"},
            format="json",
        )

        assert response.status_code == 200
        material.refresh_from_db()
        assert (material.name, material.stock, str(material.price)) == (
            "Aço inox",
            3,
            "9.90",
        )

    def test_put_sem_campo_obrigatorio_retorna_400(self, client, make_raw_material):
        material = make_raw_material()

        response = client.put(detail(material.id), {"name": "Aço"}, format="json")

        assert response.status_code == 400
        assert "stock" in response.data

    def test_delete_remove_o_registro(self, client, make_raw_material):
        material = make_raw_material()

        response = client.delete(detail(material.id))

        assert response.status_code == 204
        assert not RawMaterial.objects.filter(id=material.id).exists()

    def test_delete_remove_as_linhas_de_ficha_tecnica(
        self, client, make_raw_material, make_product, make_bom
    ):
        material = make_raw_material()
        product = make_product()
        make_bom(product, material, quantity=2)

        client.delete(detail(material.id))

        assert product.productrawmaterial_set.count() == 0
