"""Validação da SECRET_KEY usada fora do modo de desenvolvimento.

Os critérios são os mesmos do `manage.py check --deploy` (security.W009),
com a diferença de que aqui uma chave fraca impede a aplicação de subir,
em vez de gerar apenas um aviso.
"""

MIN_LENGTH = 50
MIN_UNIQUE_CHARACTERS = 5
INSECURE_PREFIX = "django-insecure-"

# Usada somente quando DEBUG=True e nenhuma SECRET_KEY foi definida.
DEVELOPMENT_KEY = INSECURE_PREFIX + "chave-somente-para-desenvolvimento-local"


def weak_secret_key_reason(key):
    """Devolve o motivo pelo qual a chave é fraca, ou None se ela for aceitável."""
    if not key:
        return "não foi definida"
    if key.startswith(INSECURE_PREFIX):
        return f"começa com '{INSECURE_PREFIX}', o prefixo das chaves de exemplo do Django"
    if len(key) < MIN_LENGTH:
        return f"tem menos de {MIN_LENGTH} caracteres"
    if len(set(key)) < MIN_UNIQUE_CHARACTERS:
        return f"tem menos de {MIN_UNIQUE_CHARACTERS} caracteres diferentes"
    return None
