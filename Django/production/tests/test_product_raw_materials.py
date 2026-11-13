"""CRUD da ficha técnica produto × matéria-prima (/api/product-raw-materials/)."""

from production.models import ProductRawMaterial

URL = "/api/product-raw-materials/"


def detail(pk):
    return f"{URL}{pk}/"


class TestListarEDetalhar:
    def test_detalhe_expoe_os_campos_do_contrato(
        self, client, make_product, make_raw_material, make_bom
    ):
        product = make_product(name="Cadeira", price="150.00")
        material = make_raw_material(name="Aço", price="2.50")
        line = make_bom(product, material, quantity=4, manufacturing_price="1.00")

        response = client.get(detail(line.id))

        assert response.status_code == 200
        assert response.data == {
            "id": line.id,
            "product": product.id,
            "product_name": "Cadeira",
            "product_price": "150.00",
            "raw_material": material.id,
            "raw_material_name": "Aço",
            "raw_material_price": "2.50",
            "quantity": 4.0,
            "price": None,
            "manufacturing_price": "1.00",
            "cost": 11.0,  # 4 × 2,50 + 1,00
        }

    def test_lista_sem_paginacao(self, client, make_product, make_raw_material, make_bom):
        product = make_product()
        make_bom(product, make_raw_material(name="Aço"), quantity=1)
        make_bom(product, make_raw_material(name="Madeira"), quantity=2)

        response = client.get(URL)

        assert response.status_code == 200
        assert isinstance(response.data, list)
        assert {item["raw_material_name"] for item in response.data} == {"Aço", "Madeira"}

    def test_custo_trata_precos_ausentes_como_zero(
        self, client, make_product, make_raw_material, make_bom
    ):
        line = make_bom(make_product(), make_raw_material(price=None), quantity=3)

        response = client.get(detail(line.id))

        assert response.data["raw_material_price"] is None
        assert response.data["manufacturing_price"] is None
        assert response.data["cost"] == 0


class TestCriar:
    def test_cria_linha_da_ficha_tecnica(self, client, make_product, make_raw_material):
        product = make_product()
        material = make_raw_material()

        response = client.post(
            URL,
            {
                "product": product.id,
                "raw_material": material.id,
                "quantity": 2.5,
                "manufacturing_price": "0.75",
            },
            format="json",
        )

        assert response.status_code == 201
        line = ProductRawMaterial.objects.get(id=response.data["id"])
        assert (line.product, line.raw_material, line.quantity) == (product, material, 2.5)
        assert str(line.manufacturing_price) == "0.75"

    def test_produto_materia_prima_e_quantidade_sao_obrigatorios(self, client):
        response = client.post(URL, {}, format="json")

        assert response.status_code == 400
        assert set(response.data) == {"product", "raw_material", "quantity"}

    def test_produto_inexistente_retorna_400(self, client, make_raw_material):
        response = client.post(
            URL,
            {"product": 999, "raw_material": make_raw_material().id, "quantity": 1},
            format="json",
        )

        assert response.status_code == 400
        assert "product" in response.data

    def test_campos_derivados_sao_somente_leitura(
        self, client, make_product, make_raw_material
    ):
        product = make_product(name="Cadeira")

        response = client.post(
            URL,
            {
                "product": product.id,
                "raw_material": make_raw_material().id,
                "quantity": 1,
                "product_name": "Outro nome",
                "cost": 999,
            },
            format="json",
        )

        assert response.status_code == 201
        assert response.data["product_name"] == "Cadeira"
        assert response.data["cost"] == 2.5

    def test_criar_linha_nao_altera_o_estoque_da_materia_prima(
        self, client, make_product, make_raw_material
    ):
        """A API só registra a ficha técnica; quem debita estoque é `produce`."""
        material = make_raw_material(stock=10)

        client.post(
            URL,
            {"product": make_product().id, "raw_material": material.id, "quantity": 4},
            format="json",
        )

        material.refresh_from_db()
        assert material.stock == 10


class TestAtualizarERemover:
    def test_patch_altera_a_quantidade(
        self, client, make_product, make_raw_material, make_bom
    ):
        line = make_bom(make_product(), make_raw_material(), quantity=1)

        response = client.patch(detail(line.id), {"quantity": 6}, format="json")

        assert response.status_code == 200
        line.refresh_from_db()
        assert line.quantity == 6

    def test_delete_remove_a_linha_e_preserva_produto_e_materia_prima(
        self, client, make_product, make_raw_material, make_bom
    ):
        product = make_product()
        material = make_raw_material()
        line = make_bom(product, material, quantity=1)

        response = client.delete(detail(line.id))

        assert response.status_code == 204
        assert not ProductRawMaterial.objects.filter(id=line.id).exists()
        product.refresh_from_db()
        material.refresh_from_db()
