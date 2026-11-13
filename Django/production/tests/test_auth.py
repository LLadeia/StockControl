"""Autenticação JWT e proteção das rotas."""

from datetime import timedelta

import pytest
from rest_framework_simplejwt.tokens import AccessToken

from .conftest import PASSWORD, USERNAME

TOKEN_URL = "/api/token/"
REFRESH_URL = "/api/token/refresh/"
USER_INFO_URL = "/api/auth/user/"


def obter_tokens(anon_client):
    response = anon_client.post(
        TOKEN_URL, {"username": USERNAME, "password": PASSWORD}, format="json"
    )
    assert response.status_code == 200
    return response.data


class TestObterToken:
    def test_credenciais_validas_retornam_access_e_refresh(self, anon_client, user):
        response = anon_client.post(
            TOKEN_URL, {"username": USERNAME, "password": PASSWORD}, format="json"
        )

        assert response.status_code == 200
        assert set(response.data) == {"access", "refresh"}

    def test_senha_errada_retorna_401(self, anon_client, user):
        response = anon_client.post(
            TOKEN_URL, {"username": USERNAME, "password": "errada"}, format="json"
        )

        assert response.status_code == 401
        assert "access" not in response.data

    def test_usuario_inexistente_retorna_401(self, anon_client, db):
        response = anon_client.post(
            TOKEN_URL, {"username": "ninguem", "password": PASSWORD}, format="json"
        )

        assert response.status_code == 401

    def test_usuario_inativo_nao_recebe_token(self, anon_client, user):
        user.is_active = False
        user.save()

        response = anon_client.post(
            TOKEN_URL, {"username": USERNAME, "password": PASSWORD}, format="json"
        )

        assert response.status_code == 401

    def test_campos_obrigatorios(self, anon_client, db):
        response = anon_client.post(TOKEN_URL, {}, format="json")

        assert response.status_code == 400
        assert set(response.data) == {"username", "password"}


class TestUsarToken:
    def test_access_token_libera_rota_protegida(self, anon_client, user):
        access = obter_tokens(anon_client)["access"]

        anon_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = anon_client.get("/api/products/")

        assert response.status_code == 200

    def test_token_invalido_retorna_401(self, anon_client, db):
        anon_client.credentials(HTTP_AUTHORIZATION="Bearer nao-e-um-jwt")

        response = anon_client.get("/api/products/")

        assert response.status_code == 401

    def test_token_expirado_retorna_401(self, anon_client, user):
        token = AccessToken.for_user(user)
        token.set_exp(lifetime=-timedelta(minutes=1))

        anon_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = anon_client.get("/api/products/")

        assert response.status_code == 401

    def test_refresh_token_nao_serve_como_access(self, anon_client, user):
        refresh = obter_tokens(anon_client)["refresh"]

        anon_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh}")
        response = anon_client.get("/api/products/")

        assert response.status_code == 401


class TestRenovarToken:
    def test_refresh_valido_retorna_novo_access(self, anon_client, user):
        refresh = obter_tokens(anon_client)["refresh"]

        response = anon_client.post(REFRESH_URL, {"refresh": refresh}, format="json")

        assert response.status_code == 200
        assert "access" in response.data

        anon_client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        assert anon_client.get("/api/products/").status_code == 200

    def test_refresh_invalido_retorna_401(self, anon_client, db):
        response = anon_client.post(REFRESH_URL, {"refresh": "invalido"}, format="json")

        assert response.status_code == 401


class TestUsuarioAutenticado:
    def test_retorna_dados_do_usuario_logado(self, client, user):
        response = client.get(USER_INFO_URL)

        assert response.status_code == 200
        assert response.data == {
            "id": user.id,
            "username": USERNAME,
            "email": "operador@example.com",
            "is_superuser": False,
            "is_staff": False,
            "first_name": "Olga",
            "last_name": "Operadora",
        }

    def test_nao_expoe_a_senha(self, client):
        response = client.get(USER_INFO_URL)

        assert "password" not in response.data


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("method", "url"),
    [
        ("get", USER_INFO_URL),
        ("get", "/api/products/"),
        ("post", "/api/products/"),
        ("get", "/api/products/1/"),
        ("get", "/api/products/1/can_produce/"),
        ("post", "/api/products/1/produce/"),
        ("get", "/api/raw-materials/"),
        ("post", "/api/raw-materials/"),
        ("get", "/api/product-raw-materials/"),
        ("post", "/api/product-raw-materials/"),
        ("get", "/api/production-logs/"),
        ("get", "/api/production-logs/by_model/?model=Product"),
    ],
)
def test_rotas_exigem_autenticacao(anon_client, method, url):
    response = getattr(anon_client, method)(url)

    assert response.status_code == 401
