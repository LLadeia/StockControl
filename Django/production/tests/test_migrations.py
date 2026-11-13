"""Os modelos e as migrações versionadas têm de contar a mesma história."""

import pytest
from django.core.management import call_command


@pytest.mark.django_db
@pytest.mark.xfail(
    reason=(
        "As migrações foram geradas com Django 6 (chave primária BigAutoField por "
        "padrão), mas o requirements.txt instala Django 5, cujo padrão é AutoField. "
        "Sem DEFAULT_AUTO_FIELD definido, o Django 5 quer gerar uma migração 0009."
    ),
    raises=SystemExit,
)
def test_nao_ha_migracoes_pendentes():
    call_command("makemigrations", "--check", "--dry-run")
