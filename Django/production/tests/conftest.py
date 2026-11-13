"""Fixtures compartilhadas pelos testes da API.

Os testes tratam a API como caixa-preta: fazem requisições HTTP e conferem a
resposta e o estado do banco, sem chamar as views diretamente.
"""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from production.models import Product, ProductRawMaterial, RawMaterial

USERNAME = "operador"
PASSWORD = "senha-de-teste-123"


@pytest.fixture(autouse=True)
def _ambiente_de_teste(settings, tmp_path):
    """Isola os testes do ambiente local.

    - uploads vão para um diretório temporário, nunca para Django/media;
    - hash de senha rápido, para a suíte não gastar tempo com PBKDF2.
    """
    settings.MEDIA_ROOT = tmp_path / "media"
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username=USERNAME,
        password=PASSWORD,
        email="operador@example.com",
        first_name="Olga",
        last_name="Operadora",
    )


@pytest.fixture
def anon_client():
    """Cliente sem credenciais.

    `raise_request_exception=False` faz uma exceção não tratada na view chegar
    ao teste como resposta 500, igual ao que um cliente HTTP real receberia.
    """
    return APIClient(raise_request_exception=False)


@pytest.fixture
def client(user):
    """Cliente autenticado (a emissão do JWT em si é coberta em test_auth.py)."""
    api_client = APIClient(raise_request_exception=False)
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def make_raw_material(db):
    def _make(name="Aço", stock=100, price="2.50", **extra):
        return RawMaterial.objects.create(name=name, stock=stock, price=price, **extra)

    return _make


@pytest.fixture
def make_product(db):
    def _make(name="Cadeira", price="150.00", stock=0, **extra):
        return Product.objects.create(name=name, price=price, stock=stock, **extra)

    return _make


@pytest.fixture
def make_bom(db):
    """Cria uma linha da ficha técnica (ProductRawMaterial)."""

    def _make(product, raw_material, quantity, manufacturing_price=None, price=None):
        return ProductRawMaterial.objects.create(
            product=product,
            raw_material=raw_material,
            quantity=quantity,
            manufacturing_price=manufacturing_price,
            price=price,
        )

    return _make
