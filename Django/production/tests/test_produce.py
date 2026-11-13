"""POST /api/products/{id}/produce/ — a regra de negócio central do sistema.

Produzir N unidades debita as matérias-primas da ficha técnica, credita o
estoque do produto e grava um registro no histórico de produção.

O arquivo tem duas partes:

1. o comportamento atual que deve ser preservado;
2. bugs conhecidos, cada um com um teste marcado como falha esperada
   (`xfail`). O teste descreve o comportamento *correto*; quando o bug for
   corrigido ele passa, e como `xfail_strict` está ligado a suíte quebra até
   a marcação ser removida.
"""

from decimal import Decimal

import pytest

from production.models import Product, ProductionLog


def url(product):
    return f"/api/products/{product.id}/produce/"


def produce(client, product, quantity):
    return client.post(url(product), {"quantity": quantity}, format="json")


@pytest.fixture
def cadeira(make_product, make_raw_material, make_bom):
    """Cadeira: 4 de aço (R$ 2,50) + R$ 1,00 de fabricação e 0,5 de tecido (R$ 4,00).

    Custo unitário: 4 × 2,50 + 1,00 + 0,5 × 4,00 = R$ 13,00.
    """
    product = make_product(name="Cadeira", price="150.00", stock=0)
    aco = make_raw_material(name="Aço", stock=100, price="2.50")
    tecido = make_raw_material(name="Tecido", stock=10, price="4.00")
    make_bom(product, aco, quantity=4, manufacturing_price="1.00")
    make_bom(product, tecido, quantity=0.5)
    product.aco = aco
    product.tecido = tecido
    return product


# ─── Comportamento atual ────────────────────────────────────────────────────


class TestProducaoComSucesso:
    def test_resposta(self, client, cadeira):
        response = produce(client, cadeira, 3)

        assert response.status_code == 200
        assert response.data == {"success": True}

    def test_debita_cada_materia_prima_da_ficha_tecnica(self, client, cadeira):
        produce(client, cadeira, 3)

        cadeira.aco.refresh_from_db()
        cadeira.tecido.refresh_from_db()
        assert cadeira.aco.stock == 88  # 100 − 3 × 4
        assert cadeira.tecido.stock == 8.5  # 10 − 3 × 0,5

    def test_credita_o_estoque_do_produto(self, client, cadeira):
        produce(client, cadeira, 3)
        produce(client, cadeira, 2)

        cadeira.refresh_from_db()
        assert cadeira.stock == 5

    def test_registra_a_producao_com_custo_unitario_e_total(self, client, cadeira):
        produce(client, cadeira, 3)

        log = ProductionLog.objects.get()
        assert log.product == cadeira
        assert log.quantity == 3
        assert log.unit_price == Decimal("13.00")
        assert log.total_price == Decimal("39.00")

    def test_custo_ignora_o_preco_de_venda_do_produto(self, client, cadeira):
        Product.objects.filter(id=cadeira.id).update(price="9999.00")

        produce(client, cadeira, 1)

        assert ProductionLog.objects.get().unit_price == Decimal("13.00")

    def test_materia_prima_sem_preco_entra_com_custo_zero(
        self, client, make_product, make_raw_material, make_bom
    ):
        product = make_product()
        make_bom(product, make_raw_material(price=None), quantity=2)

        response = produce(client, product, 1)

        assert response.status_code == 200
        assert ProductionLog.objects.get().unit_price == Decimal("0.00")

    def test_quantidade_padrao_e_uma_unidade(self, client, cadeira):
        response = client.post(url(cadeira))

        assert response.status_code == 200
        cadeira.refresh_from_db()
        assert cadeira.stock == 1
        assert ProductionLog.objects.get().quantity == 1

    def test_aceita_quantidade_como_texto_numerico(self, client, cadeira):
        response = produce(client, cadeira, "2")

        assert response.status_code == 200
        cadeira.refresh_from_db()
        assert cadeira.stock == 2

    def test_pode_consumir_todo_o_estoque(self, client, cadeira):
        response = produce(client, cadeira, 20)  # tecido: 20 × 0,5 = 10

        assert response.status_code == 200
        cadeira.tecido.refresh_from_db()
        assert cadeira.tecido.stock == 0

    def test_nao_afeta_materias_primas_de_outros_produtos(
        self, client, cadeira, make_raw_material
    ):
        madeira = make_raw_material(name="Madeira", stock=7)

        produce(client, cadeira, 1)

        madeira.refresh_from_db()
        assert madeira.stock == 7


class TestEstoqueInsuficiente:
    def test_resposta_informa_a_materia_prima_em_falta(self, client, cadeira):
        response = produce(client, cadeira, 21)  # tecido: 21 × 0,5 = 10,5 > 10

        assert response.status_code == 400
        assert response.data == {"success": False, "raw_material": "Tecido"}

    def test_nada_e_alterado(self, client, cadeira):
        """O aço seria suficiente, mas nem ele pode ser debitado."""
        produce(client, cadeira, 21)

        cadeira.refresh_from_db()
        cadeira.aco.refresh_from_db()
        cadeira.tecido.refresh_from_db()
        assert cadeira.stock == 0
        assert cadeira.aco.stock == 100
        assert cadeira.tecido.stock == 10
        assert ProductionLog.objects.count() == 0

    def test_producoes_em_sequencia_param_quando_o_estoque_acaba(self, client, cadeira):
        primeira = produce(client, cadeira, 15)
        segunda = produce(client, cadeira, 15)

        assert primeira.status_code == 200
        assert segunda.status_code == 400
        cadeira.refresh_from_db()
        assert cadeira.stock == 15


class TestRota:
    def test_produto_inexistente_retorna_404(self, client):
        assert client.post("/api/products/999/produce/").status_code == 404

    def test_aceita_somente_post(self, client, cadeira):
        assert client.get(url(cadeira)).status_code == 405


class TestComportamentoAtualQuestionavel:
    """Não são bugs evidentes, mas decisões que valem uma revisão na etapa 5."""

    def test_produto_sem_ficha_tecnica_e_produzido_sem_consumir_nada(
        self, client, make_product
    ):
        product = make_product(stock=0)

        response = produce(client, product, 5)

        assert response.status_code == 200
        product.refresh_from_db()
        assert product.stock == 5
        assert ProductionLog.objects.get().total_price == Decimal("0.00")

    def test_quantidade_fracionaria_e_truncada(self, client, cadeira):
        """`int(2.9)` vira 2: a API produz menos do que foi pedido, sem avisar."""
        response = produce(client, cadeira, 2.9)

        assert response.status_code == 200
        cadeira.refresh_from_db()
        assert cadeira.stock == 2


# ─── Bugs conhecidos (falha esperada) ───────────────────────────────────────


@pytest.mark.xfail(reason="int() sem tratamento: quantidade inválida gera erro 500")
@pytest.mark.parametrize(
    "quantity",
    ["abc", "2.5", "", None, [1], {"n": 1}],
    ids=["texto", "texto-decimal", "vazio", "null", "lista", "objeto"],
)
def test_quantidade_invalida_retorna_400(client, cadeira, quantity):
    response = produce(client, cadeira, quantity)

    assert response.status_code == 400


@pytest.mark.xfail(reason="quantidade zero é aceita e grava um registro de produção vazio")
def test_quantidade_zero_retorna_400(client, cadeira):
    response = produce(client, cadeira, 0)

    assert response.status_code == 400
    assert ProductionLog.objects.count() == 0


@pytest.mark.xfail(
    reason="quantidade negativa é aceita: devolve matéria-prima e negativa o produto"
)
def test_quantidade_negativa_retorna_400(client, cadeira):
    response = produce(client, cadeira, -2)

    assert response.status_code == 400
    cadeira.refresh_from_db()
    cadeira.aco.refresh_from_db()
    assert cadeira.stock == 0
    assert cadeira.aco.stock == 100
    assert ProductionLog.objects.count() == 0


@pytest.mark.xfail(
    reason="FloatField: 3 × 0.1 = 0.30000000000000004 > 0.3, produção recusada por arredondamento"
)
def test_estoque_exato_com_quantidades_decimais(
    client, make_product, make_raw_material, make_bom
):
    product = make_product()
    material = make_raw_material(stock=0.3)
    make_bom(product, material, quantity=0.1)

    response = produce(client, product, 3)

    assert response.status_code == 200
    material.refresh_from_db()
    assert material.stock == 0


class TestMateriaPrimaRepetidaNaFichaTecnica:
    """Nada impede duas linhas da ficha técnica com a mesma matéria-prima.

    A view checa e debita linha a linha, cada uma com sua própria cópia do
    registro em memória, então a última gravação sobrescreve as anteriores.
    """

    @pytest.fixture
    def banco(self, make_product, make_raw_material, make_bom):
        product = make_product(name="Banco")
        product.madeira = make_raw_material(name="Madeira", stock=10)
        make_bom(product, product.madeira, quantity=3)  # assento
        make_bom(product, product.madeira, quantity=2)  # pés
        return product

    @pytest.mark.xfail(reason="atualização perdida: só o débito da última linha é gravado")
    def test_debita_a_soma_das_linhas(self, client, banco):
        produce(client, banco, 1)

        banco.madeira.refresh_from_db()
        assert banco.madeira.stock == 5  # 10 − (3 + 2)

    @pytest.mark.xfail(reason="a checagem de estoque não soma as linhas da mesma matéria-prima")
    def test_recusa_quando_a_soma_das_linhas_excede_o_estoque(self, client, banco):
        banco.madeira.stock = 4  # cada linha cabe sozinha; as duas juntas (5), não
        banco.madeira.save()

        response = produce(client, banco, 1)

        assert response.status_code == 400


@pytest.mark.xfail(reason="try/except: pass engole a falha ao creditar o estoque do produto")
def test_falha_ao_creditar_o_produto_desfaz_a_producao(client, cadeira, monkeypatch):
    def save_que_falha(self, *args, **kwargs):
        raise RuntimeError("falha ao salvar o produto")

    monkeypatch.setattr(Product, "save", save_que_falha)

    response = produce(client, cadeira, 1)

    # A produção não pode ser dada como concluída...
    assert response.status_code == 500
    # ...e o débito das matérias-primas tem de ser desfeito junto.
    cadeira.aco.refresh_from_db()
    assert cadeira.aco.stock == 100
    assert ProductionLog.objects.count() == 0
