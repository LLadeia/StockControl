"""A configuração vem de variáveis de ambiente e falha de forma segura.

Cada teste carrega core.settings em um processo novo, com o ambiente
controlado, porque é assim que a aplicação lê a configuração ao subir.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from .test_secret_key import STRONG_KEY

DJANGO_DIR = Path(__file__).resolve().parents[2]

# Variáveis que core.settings lê. Todas são definidas explicitamente em cada
# teste (vazias quando o teste não as informa), para que um .env local do
# desenvolvedor não interfira: o ambiente tem precedência sobre o arquivo.
VARIABLES = ["SECRET_KEY", "ALLOWED_HOSTS", "CORS_ALLOWED_ORIGINS"]
BOOLEAN_VARIABLES = {"DEBUG": "False", "CORS_ALLOW_ALL_ORIGINS": "False"}

PRINT_SETTINGS = """
import json
from django.conf import settings
print(json.dumps({
    "DEBUG": settings.DEBUG,
    "SECRET_KEY": settings.SECRET_KEY,
    "ALLOWED_HOSTS": settings.ALLOWED_HOSTS,
    "CORS_ALLOWED_ORIGINS": settings.CORS_ALLOWED_ORIGINS,
    "CORS_ALLOW_ALL_ORIGINS": settings.CORS_ALLOW_ALL_ORIGINS,
    "DATABASE": {
        key: settings.DATABASES["default"][key]
        for key in ("ENGINE", "NAME", "USER", "PASSWORD", "HOST", "PORT")
    },
}))
"""


def run_with_env(**variables):
    env = {key: value for key, value in os.environ.items() if key not in VARIABLES}
    env.update({name: "" for name in VARIABLES})
    env.update(BOOLEAN_VARIABLES)
    env.update(variables)
    env["DJANGO_SETTINGS_MODULE"] = "core.settings"
    return subprocess.run(
        [sys.executable, "-c", PRINT_SETTINGS],
        cwd=DJANGO_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def load_settings(**variables):
    result = run_with_env(**variables)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


class TestProducao:
    """DEBUG=False: a aplicação só sobe com uma SECRET_KEY forte."""

    @pytest.mark.parametrize(
        "key",
        ["", "curta", "django-insecure-" + STRONG_KEY, "a" * 60],
        ids=["ausente", "curta", "prefixo-inseguro", "repetitiva"],
    )
    def test_recusa_subir_com_chave_fraca(self, key):
        result = run_with_env(DEBUG="False", SECRET_KEY=key)

        assert result.returncode != 0
        assert "ImproperlyConfigured" in result.stderr
        assert "SECRET_KEY recusada" in result.stderr

    def test_sobe_com_chave_forte(self):
        settings = load_settings(DEBUG="False", SECRET_KEY=STRONG_KEY)

        assert settings["DEBUG"] is False
        assert settings["SECRET_KEY"] == STRONG_KEY

    def test_debug_desligado_e_o_padrao(self):
        result = run_with_env(SECRET_KEY="")

        assert result.returncode != 0
        assert "SECRET_KEY recusada" in result.stderr

    def test_cors_fechado_por_padrao(self):
        settings = load_settings(SECRET_KEY=STRONG_KEY)

        assert settings["CORS_ALLOW_ALL_ORIGINS"] is False
        assert settings["CORS_ALLOWED_ORIGINS"] == []


class TestDesenvolvimento:
    """DEBUG=True: sobe sem chave, com uma chave marcada como insegura."""

    def test_sobe_sem_secret_key(self):
        settings = load_settings(DEBUG="True", SECRET_KEY="")

        assert settings["DEBUG"] is True
        assert settings["SECRET_KEY"].startswith("django-insecure-")

    def test_usa_a_secret_key_informada(self):
        settings = load_settings(DEBUG="True", SECRET_KEY="minha-chave-local")

        assert settings["SECRET_KEY"] == "minha-chave-local"


class TestBancoDeDados:
    def test_conexao_vem_das_variaveis_postgres(self):
        settings = load_settings(
            SECRET_KEY=STRONG_KEY,
            POSTGRES_DB="estoque",
            POSTGRES_USER="app",
            POSTGRES_PASSWORD="segredo",
            POSTGRES_HOST="db.interno",
            POSTGRES_PORT="6543",
        )

        assert settings["DATABASE"] == {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "estoque",
            "USER": "app",
            "PASSWORD": "segredo",
            "HOST": "db.interno",
            "PORT": "6543",
        }

    def test_a_suite_roda_contra_postgresql(self, db):
        from django.db import connection

        assert connection.vendor == "postgresql"


class TestListas:
    def test_allowed_hosts_separados_por_virgula(self):
        settings = load_settings(
            SECRET_KEY=STRONG_KEY, ALLOWED_HOSTS="api.exemplo.com, estoque.exemplo.com"
        )

        assert settings["ALLOWED_HOSTS"] == ["api.exemplo.com", "estoque.exemplo.com"]

    def test_cors_allowed_origins_separadas_por_virgula(self):
        settings = load_settings(
            SECRET_KEY=STRONG_KEY,
            CORS_ALLOWED_ORIGINS="https://app.exemplo.com,http://localhost:5173",
        )

        assert settings["CORS_ALLOWED_ORIGINS"] == [
            "https://app.exemplo.com",
            "http://localhost:5173",
        ]

    def test_cors_pode_ser_aberto_explicitamente(self):
        settings = load_settings(SECRET_KEY=STRONG_KEY, CORS_ALLOW_ALL_ORIGINS="True")

        assert settings["CORS_ALLOW_ALL_ORIGINS"] is True
