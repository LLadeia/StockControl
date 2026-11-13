"""Critérios que tornam uma SECRET_KEY fraca."""

import pytest

from core.secret_key import DEVELOPMENT_KEY, weak_secret_key_reason

STRONG_KEY = "Zk3vQ9-xT7mB2pLw8RfYc5NhJ6dGs4aUe1oViXtKqM0bCzWyEr"


@pytest.mark.parametrize(
    ("key", "reason"),
    [
        ("", "não foi definida"),
        (None, "não foi definida"),
        ("django-insecure-" + STRONG_KEY, "django-insecure-"),
        (DEVELOPMENT_KEY, "django-insecure-"),
        ("curta", "menos de 50 caracteres"),
        (STRONG_KEY[:49], "menos de 50 caracteres"),
        ("abab" * 20, "caracteres diferentes"),
    ],
    ids=["vazia", "ausente", "prefixo-inseguro", "chave-de-dev", "curta", "49-chars", "repetitiva"],
)
def test_chave_fraca_e_recusada_com_o_motivo(key, reason):
    assert reason in weak_secret_key_reason(key)


def test_chave_forte_e_aceita():
    assert len(STRONG_KEY) == 50
    assert weak_secret_key_reason(STRONG_KEY) is None
