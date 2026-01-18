FROM python:3.12-slim

WORKDIR /app

# Устанавливаем uv
RUN pip install --no-cache-dir uv

# Копируем только то, что нужно для установки зависимостей
COPY pyproject.toml ./
COPY uv.lock ./

# Устанавливаем зависимости
RUN uv pip install --system --no-cache-dir .

# Копируем весь код
COPY . .

# Миграция при старте
RUN chmod +x /app/entrypoint.sh

# Создаём пользователя без root-прав на всякий пожарный
RUN useradd --create-home --shell /bin/bash appuser && chown -R appuser:appuser /app
USER appuser

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]