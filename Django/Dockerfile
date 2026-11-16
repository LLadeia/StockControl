# syntax=docker/dockerfile:1

# ─── Base: dependências da aplicação e código ──────────────────────────────
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# A aplicação roda com um usuário sem privilégios.
RUN useradd --create-home --uid 1000 app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=app:app . .

# ─── Testes: base + dependências de desenvolvimento ────────────────────────
# Uso: docker compose run --rm tests
FROM base AS test

RUN pip install -r requirements-dev.txt

USER app
CMD ["pytest", "-p", "no:cacheprovider"]

# ─── Aplicação (estágio padrão) ────────────────────────────────────────────
FROM base AS app

# O collectstatic só precisa carregar as configurações; DEBUG=True vale apenas
# para este comando e dispensa uma SECRET_KEY durante o build.
RUN DEBUG=True python manage.py collectstatic --noinput \
    && mkdir -p media \
    && chown -R app:app staticfiles media

USER app
EXPOSE 8000

# Aplica as migrações e então executa o comando.
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-"]
