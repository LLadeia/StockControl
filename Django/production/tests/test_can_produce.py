"""GET /api/products/{id}/can_produce/ — há estoque para produzir uma unidade?"""

from production.models import ProductionLog


def url(product):
    return f"/api/products/{product.id}/can_produce/"


def test_estoque_suficiente(client, make_product, make_raw_material, make_bom):
    product = make_product()
    make_bom(product, make_raw_material(name="Aço", stock=10), quantity=4)
    make_bom(product, make_raw_material(name="Madeira", stock=3), quantity=2)

    response = client.get(url(product))

    assert response.status_code == 200
    assert response.data == {"can_produce": True}


def test_estoque_exatamente_igual_ao_necessario(
    client, make_product, make_raw_material, make_bom
):
    product = make_product()
    make_bom(product, make_raw_material(stock=4), quantity=4)

    response = client.get(url(product))

    assert response.data == {"can_produce": True}


def test_estoque_insuficiente_informa_a_materia_prima_limitante(
    client, make_product, make_raw_material, make_bom
):
    product = make_product()
    make_bom(product, make_raw_material(name="Aço", stock=10), quantity=4)
    make_bom(product, make_raw_material(name="Madeira", stock=1.5), quantity=2)

    response = client.get(url(product))

    # Falta de estoque não é erro: a resposta continua sendo 200.
    assert response.status_code == 200
    assert response.data == {
        "can_produce": False,
        "limiting_raw_material": "Madeira",
        "required": 2.0,
        "available": 1.5,
    }


def test_avalia_somente_uma_unidade(client, make_product, make_raw_material, make_bom):
    """A rota não recebe quantidade: responde sobre produzir 1 unidade."""
    product = make_product()
    make_bom(product, make_raw_material(stock=4), quantity=4)

    response = client.get(url(product), {"quantity": 2})

    assert response.data == {"can_produce": True}


def test_produto_sem_ficha_tecnica_pode_ser_produzido_hoje(client, make_product):
    """Comportamento atual: sem matérias-primas associadas, nada limita a produção."""
    response = client.get(url(make_product()))

    assert response.status_code == 200
    assert response.data == {"can_produce": True}


def test_consulta_nao_altera_estoque_nem_gera_historico(
    client, make_product, make_raw_material, make_bom
):
    product = make_product(stock=0)
    material = make_raw_material(stock=10)
    make_bom(product, material, quantity=4)

    client.get(url(product))

    product.refresh_from_db()
    material.refresh_from_db()
    assert (product.stock, material.stock) == (0, 10)
    assert ProductionLog.objects.count() == 0


def test_produto_inexistente_retorna_404(client):
    assert client.get("/api/products/999/can_produce/").status_code == 404


def test_aceita_somente_get(client, make_product):
    assert client.post(url(make_product())).status_code == 405
