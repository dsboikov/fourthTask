FROM python:3.13-slim

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

# Создаём пользователя без root-прав на всякий пожарный
RUN useradd --create-home --shell /bin/bash appuser && chown -R appuser:appuser /app
USER appuser

# Миграция при старте
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# По умолчанию — запуск FastAPI
CMD ["/app/entrypoint.sh", "uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]