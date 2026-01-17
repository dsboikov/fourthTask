#!/bin/sh
set -e

# Применяем миграции
echo "▶ Applying database migrations..."
uv run alembic upgrade head

# Запускаем переданную команду
exec "$@"