"""Configuração usada pelo pytest.

Fixa as variáveis de ambiente antes de carregar core.settings, para que a
suíte rode igual em qualquer máquina: sem depender de um .env local e sem
ser afetada pelo que estiver nele.
"""

import os

os.environ.update(
    {
        "DEBUG": "False",
        "SECRET_KEY": "chave-usada-somente-nos-testes-automatizados-0123456789",
        "ALLOWED_HOSTS": "testserver",
        "CORS_ALLOWED_ORIGINS": "http://localhost:5173",
        "CORS_ALLOW_ALL_ORIGINS": "False",
    }
)

from .settings import *  # noqa: E402, F403
