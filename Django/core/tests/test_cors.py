"""CORS: só as origens configuradas podem chamar a API pelo navegador."""

import pytest
from rest_framework.test import APIClient

ALLOWED = "http://localhost:5173"
OTHER = "https://site-malicioso.example"


@pytest.fixture
def api():
    return APIClient()


def preflight(api, origin):
    return api.options(
        "/api/products/",
        HTTP_ORIGIN=origin,
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS="authorization",
    )


def test_preflight_de_origem_autorizada(api, settings):
    settings.CORS_ALLOWED_ORIGINS = [ALLOWED]

    response = preflight(api, ALLOWED)

    assert response.status_code == 200
    assert response["Access-Control-Allow-Origin"] == ALLOWED
    assert "authorization" in response["Access-Control-Allow-Headers"]


def test_preflight_de_origem_nao_autorizada(api, settings):
    settings.CORS_ALLOWED_ORIGINS = [ALLOWED]

    response = preflight(api, OTHER)

    assert "Access-Control-Allow-Origin" not in response


def test_resposta_normal_leva_o_cabecalho_para_origem_autorizada(api, settings):
    settings.CORS_ALLOWED_ORIGINS = [ALLOWED]

    # 401 (sem token), mas o navegador só consegue ler o erro se o cabeçalho vier.
    response = api.get("/api/products/", HTTP_ORIGIN=ALLOWED)

    assert response.status_code == 401
    assert response["Access-Control-Allow-Origin"] == ALLOWED


def test_redirecionamento_tambem_leva_o_cabecalho(api, settings):
    """APPEND_SLASH responde no CommonMiddleware; o CORS precisa vir antes dele."""
    settings.CORS_ALLOWED_ORIGINS = [ALLOWED]

    response = api.get("/api/products", HTTP_ORIGIN=ALLOWED)

    assert response.status_code == 301
    assert response["Access-Control-Allow-Origin"] == ALLOWED


def test_cors_aberto_aceita_qualquer_origem(api, settings):
    settings.CORS_ALLOW_ALL_ORIGINS = True

    response = api.get("/api/products/", HTTP_ORIGIN=OTHER)

    assert response["Access-Control-Allow-Origin"] == "*"
