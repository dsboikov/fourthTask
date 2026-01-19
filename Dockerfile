FROM python:3.12-slim

# Установка системных зависимостей для бинарных пакетов
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy

# Устанавливаем uv
RUN pip install --no-cache-dir uv

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости СИСТЕМНО
RUN uv pip install --system --no-cache-dir .

# Копируем остальной код
COPY . .

# НЕ используем uv для запуска - только для установки
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]