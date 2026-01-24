# Учебный проект "AI-генератор постов для Telegram"

## **Описание**
Учебный проект, реализующий функционал сервиса, который парсит новости с определённого списка сайтов/Telegram-каналов и на их основе создаёт новый. Для рерайтинга использует ИИ. 
Публикация проходит по расписанию в Telegram-канал, с возможностью ручного управления и мониторинга через API.

### **Интегрированные сервисы:**
+ парсинг новостей (сайты и Telegram-каналы);
+ очередь задач;
+ генерация постов с помощью AI;
+ публикация через Telethon;
+ панель управления источниками.

## **Установка**
- клонировать репозиторий или скачать и разархивировать архив на сервер/локальный компьютер
### Запуск:
```docker-compose build --no-cache```
### Авторизация телеграм при первом запуске:
```
docker-compose up -d postgres redis
docker-compose run --rm init_telegram
```
### После этого обычный запуск:
```docker-compose up```

### Добавить список дефолтных источников для парсинга
```
docker-compose exec app uv run python -m scripts.init_sources
```

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
```docker-compose exec postgres pg_dump -U postgres aibotdb > backup.sql```

### Восстановление данных из бэкапа вручную
```docker-compose exec -T postgres psql -U postgres -d aibotdb < backup.sql```


## Веб-интерфейс:
```http://localhost:8000/```
Авторизация проходит по ключу, установленному в .env файле

### Получить только неудачные посты:
```curl "http://localhost:8000/posts/?status=failed"```

### Перезапустить неудачные посты:
```curl -X POST "http://localhost:8000/posts/retry-failed"```

### Проверить черновики перед публикацией:
```curl "http://localhost:8000/posts/?status=draft"```

