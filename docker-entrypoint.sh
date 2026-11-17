#!/bin/sh
# docker-entrypoint.sh — Punto de entrada unificado
set -e

echo "==> [entrypoint] Ejecutando migraciones de base de datos..."
python manage.py migrate --noinput

echo "==> [entrypoint] Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "==> [entrypoint] Verificando la configuración de Django..."
python manage.py check --deploy 2>/dev/null || python manage.py check

echo "==> [entrypoint] Iniciando Gunicorn..."
exec gunicorn core.wsgi \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --log-file - \
    --access-logfile -