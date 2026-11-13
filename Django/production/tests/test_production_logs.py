"""Histórico de produção (/api/production-logs/) e auditoria (by_model)."""

from datetime import timedelta

import pytest
from django.utils import timezone

from production.models import ProductionLog

URL = "/api/production-logs/"
BY_MODEL_URL = f"{URL}by_model/"


class TestHistoricoDeProducao:
    def test_registro_expoe_os_campos_do_contrato(self, client, make_product):
        product = make_product(name="Cadeira")
        log = ProductionLog.objects.create(
            product=product, quantity=3, unit_price="8.00", total_price="24.00"
        )

        response = client.get(f"{URL}{log.id}/")

        assert response.status_code == 200
        assert set(response.data) == {
            "id",
            "product",
            "product_name",
            "quantity",
            "unit_price",
            "total_price",
            "created_at",
        }
        assert response.data["product"] == product.id
        assert response.data["product_name"] == "Cadeira"
        assert response.data["quantity"] == 3.0
        assert response.data["unit_price"] == "8.00"
        assert response.data["total_price"] == "24.00"

    def test_lista_do_mais_recente_para_o_mais_antigo(self, client, make_product):
        product = make_product()
        antigo = ProductionLog.objects.create(product=product, quantity=1)
        recente = ProductionLog.objects.create(product=product, quantity=2)
        ProductionLog.objects.filter(id=antigo.id).update(
            created_at=timezone.now() - timedelta(days=1)
        )

        response = client.get(URL)

        assert response.status_code == 200
        assert [item["id"] for item in response.data] == [recente.id, antigo.id]

    def test_historico_pode_ser_escrito_direto_pela_api_hoje(self, client, make_product):
        """Comportamento atual: o ViewSet é um ModelViewSet completo.

        Qualquer usuário autenticado consegue criar (e apagar) registros de
        produção sem passar por `produce`, ou seja, sem debitar estoque.
        """
        product = make_product()

        created = client.post(URL, {"product": product.id, "quantity": 99}, format="json")
        deleted = client.delete(f"{URL}{created.data['id']}/")

        assert created.status_code == 201
        assert deleted.status_code == 204


class TestAuditoriaPorModelo:
    def test_lista_alteracoes_do_modelo_da_mais_recente_para_a_mais_antiga(
        self, client, make_product
    ):
        product = make_product(name="Cadeira")
        product.name = "Cadeira nova"
        product.save()

        response = client.get(BY_MODEL_URL, {"model": "Product"})

        assert response.status_code == 200
        assert [item["change_reason"] for item in response.data] == ["Changed", "Created"]
        assert set(response.data[0]) == {
            "id",
            "object_str",
            "changed_by",
            "changed_at",
            "change_reason",
        }
        assert response.data[0]["id"] == product.id

    @pytest.mark.parametrize("model", ["Product", "RawMaterial", "ProductRawMaterial"])
    def test_aceita_os_tres_modelos_auditados(self, client, model):
        response = client.get(BY_MODEL_URL, {"model": model})

        assert response.status_code == 200
        assert response.data == []

    def test_mostra_somente_o_modelo_pedido(self, client, make_product, make_raw_material):
        make_product()
        make_raw_material()
        make_raw_material(name="Madeira")

        response = client.get(BY_MODEL_URL, {"model": "RawMaterial"})

        assert len(response.data) == 2

    @pytest.mark.parametrize("params", [{}, {"model": "ProductionLog"}, {"model": "x"}])
    def test_modelo_ausente_ou_desconhecido_retorna_400(self, client, params):
        response = client.get(BY_MODEL_URL, params)

        assert response.status_code == 400
        assert response.data == {"error": "Model não especificado"}

    def test_alteracao_feita_pela_api_aparece_como_sistema_hoje(self, client):
        """Comportamento atual: o autor da alteração nunca é registrado.

        O HistoryRequestMiddleware do django-simple-history não está instalado,
        então `history_user` fica vazio e a API responde sempre "Sistema",
        mesmo quando a alteração veio de um usuário autenticado.
        """
        client.post("/api/products/", {"name": "Mesa"}, format="json")

        response = client.get(BY_MODEL_URL, {"model": "Product"})

        assert [item["changed_by"] for item in response.data] == ["Sistema"]
