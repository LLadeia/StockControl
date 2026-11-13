#!/bin/sh
# Ponto de entrada do contêiner da API: aplica as migrações pendentes e
# então executa o comando recebido (por padrão, o gunicorn).
set -e

python manage.py migrate --noinput

exec "$@"
