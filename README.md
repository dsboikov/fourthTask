# Учебный проект "AI-генератор постов для Telegram"

## **Описание**
Учебный проект, реализующий функционал сервиса, который парсит новости с определённого списка сайтов/Telegram-каналов и на их основе создаёт новый. Для рерайтинга использует ИИ. 
Публикация проходит по расписанию в Telegram-канал, с возможностью ручного управления и мониторинга через API.

## **Сделано:**
✅ Настроил Docker-инфраструктуру с PostgreSQL, Redis, Celery
✅ Реализовал парсинг новостей из RSS и Telegram
✅ Интегрировал OpenAI с прокси через SSH
✅ Создал полный CRUD для news_items и posts
✅ Реализовал публикацию в Telegram
✅ Добавил гибкое управление источниками через админку
✅ Защитил всё авторизацией и сделал удобную панель управления

## 4. **Структура проекта**
```
/
├── alembic/
│   ├── README
│   ├── env.py
│   └── script.py.mako
├── app/
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── generator.py
│   │   └── openai_client.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── crud.py
│   │   ├── endpoints.py
│   │   └── schemas.py
│   ├── news_parser/
│   │   ├── __init__.py
│   │   ├── sites.py
│   │   └── telegram.py
│   ├── telegram/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── bot.py
│   │   └── publisher.py
│   ├── auth.py
│   ├── config.py
│   ├── database.py
│   ├── logging_config.py
│   ├── main.py
│   ├── models.py
│   └── tasks.py
├── scripts/
│   ├── __init__.py
│   └── init_sources.py
├── .dockerignore
├── .env
├── .gitignore
├── .python-version
├── Dockerfile
├── README.md
├── __init__.py
├── alembic.ini
├── celery_worker.py
├── docker-compose.yml
├── pyproject.toml
└── uv.lock
```


## **Установка**
- Клонировать репозиторий или скачать и разархивировать архив на сервер/локальный компьютер
- Создать и наполнить файл .env на основе .env.example
- Выполнить
```
docker-compose build --no-cache
```
- Для инициализации таблиц БД последовательно выполнить:
```
docker-compose up -d postgres redis
docker-compose run --rm app uv run alembic revision --autogenerate -m "init"
docker-compose run --rm app uv run alembic upgrade head
```
- Для авторизации телеграм выполнить
```
docker-compose run --rm init_telegram
```
- Для демо обавить список дефолтных источников для парсинга
```
docker-compose exec app uv run python -m scripts.init_sources
```
- Выполнить обычный запуск
```
docker-compose up
```
- Перейти на http://127.0.0.1:8000/ где можно авторизоваться по ключу, указанному в .env


### Мануальный запуск сбора новостей
```
docker-compose exec app uv run python -c "
from app.tasks import fetch_news_from_sites, fetch_news_from_telegram
fetch_news_from_sites.delay()
fetch_news_from_telegram.delay()
"
```

### Мануальный запуск генерации постов
```
docker-compose exec app uv run python -c "
from app.tasks import generate_posts_for_unprocessed_news
generate_posts_for_unprocessed_news.delay()
"
```

### Мануальный запуск публикации в Telegram
```
docker-compose exec app uv run python -c "
from app.tasks import publish_posts_to_telegram
publish_posts_to_telegram.delay()
"
```

### Проверка логов celery
```docker-compose logs celery_worker```


### Бэкап данных вручную
```
docker-compose exec postgres pg_dump -U postgres aibotdb > backup.sql
```

### Восстановление данных из бэкапа вручную
```
docker-compose exec -T postgres psql -U postgres -d aibotdb < backup.sql
```


## Веб-интерфейс:
```http://localhost:8000/```
Авторизация проходит по ключу, установленному в .env файле

### Получить только неудачные посты:
```curl "http://localhost:8000/posts/?status=failed"```

### Перезапустить неудачные посты:
```curl -X POST "http://localhost:8000/posts/retry-failed"```

### Проверить черновики перед публикацией:
```curl "http://localhost:8000/posts/?status=draft"```



