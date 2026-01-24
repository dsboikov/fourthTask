from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from sqlalchemy import text
from app.database import get_db
from app.config import settings
from app.logging_config import setup_logging
from sqlalchemy.orm import Session
from app.api import crud, schemas
from app.api.schemas import PostStatus
from fastapi.responses import HTMLResponse
from app.auth import require_auth
from app.auth import router as auth_router
import uuid

setup_logging()
app = FastAPI(
    title="AI Telegram Post Generator",
    docs_url=None,
    redoc_url=None
)
app.include_router(auth_router)


@app.get("/docs", include_in_schema=False)
def protected_docs(request: Request):
    auth_check = require_auth(request)
    if auth_check:
        return auth_check
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API docs")


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    # Проверяем аутентификацию
    auth_check = require_auth(request)
    if auth_check:
        return auth_check

    # Получаем статистику
    news_stats = crud.get_news_stats(db)
    posts_stats = crud.get_posts_stats(db)

    # Получаем источники
    sources = crud.get_news_sources(db, limit=20)

    # Генерируем HTML для таблицы источников
    sources_html = ""
    for source in sources:
        status_badge = "🟢 Активен" if source.is_active else "🔴 Неактивен"
        sources_html += f"""
        <tr>
            <td>{source.id}</td>
            <td>{source.name}</td>
            <td>{source.parser_type}</td>
            <td>{status_badge}</td>
            <td>
                <a href="#" onclick="toggleSource({source.id}, {str(source.is_active).lower()}); return false;">
                    {'Выключить' if source.is_active else 'Включить'}
                </a>
                |
                <a href="/docs#/default/update_news_source_sources__source_id__put" target="_blank">Редактировать</a>
            </td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Telegram Bot Dashboard</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin: 10px 0; }}
            .stats {{ display: flex; gap: 20px; }}
            .stat-box {{ background: #f5f5f5; padding: 12px; border-radius: 6px; min-width: 150px; }}
            .actions a {{ display: inline-block; margin: 5px 10px 5px 0; padding: 8px 16px; 
                        background: #007bff; color: white; text-decoration: none; border-radius: 4px; }}
            .actions a.failed {{ background: #dc3545; }}
            .actions a.draft {{ background: #28a745; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>📊 AI Telegram Bot Dashboard</h1>

        <div class="stats">
            <div class="stat-box">
                <h3>📰 Новости</h3>
                <p><strong>Всего:</strong> {news_stats['total']}</p>
                <p><strong>Обработано:</strong> {news_stats['processed']}</p>
                <p><strong>Не обработано:</strong> {news_stats['unprocessed']}</p>
            </div>

            <div class="stat-box">
                <h3>📝 Посты</h3>
                <p><strong>Всего:</strong> {posts_stats['total']}</p>
                <p><strong>Черновики:</strong> {posts_stats['draft']}</p>
                <p><strong>Опубликовано:</strong> {posts_stats['published']}</p>
                <p><strong>Ошибка:</strong> {posts_stats['failed']}</p>
                <p><strong>Макс. за публикацию:</strong> {settings.MAX_POSTS_PER_PUBLISH}</p>
            </div>
        </div>

        <div class="card">
            <h3>🚀 Быстрые действия</h3>
            <div class="actions">
                <a href="/docs" target="_blank">📚 API Docs</a>
                <a href="/posts/?post_status=draft" target="_blank">📄 Черновики</a>
                <a href="/posts/?post_status=failed" class="failed" target="_blank">❌ Ошибки</a>
                <a href="#" onclick="publishPosts(); return false;" class="draft">📤 Опубликовать черновики</a>
                <a href="#" onclick="retryFailed(); return false;" class="failed">🔄 Повторить ошибки</a>
            </div>
        </div>

        <div class="card">
            <h3>📡 Источники новостей ({len(sources)})</h3>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Название</th>
                        <th>Тип</th>
                        <th>Статус</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    {sources_html}
                </tbody>
            </table>
            <a href="/docs#/default/create_news_source_sources__post" target="_blank" style="margin-top: 10px; display: inline-block;">
                ➕ Добавить источник
            </a>
        </div>

        <script>
            async function publishPosts() {{
                const maxPosts = {settings.MAX_POSTS_PER_PUBLISH};
                if (confirm(`Опубликовать до ${{maxPosts}} черновиков?`)) {{
                    try {{
                        const response = await fetch('/publish-posts/', {{ 
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }}
                        }});
                        const result = await response.json();
                        alert(`Результат: ${{result.message}}`);
                        location.reload();
                    }} catch (error) {{
                        alert('Ошибка публикации: ' + error.message);
                    }}
                }}
            }}

            async function retryFailed() {{
                if (confirm('Перевести все ошибочные посты в черновики?')) {{
                    try {{
                        const response = await fetch('/posts/retry-failed', {{ method: 'POST' }});
                        const result = await response.json();
                        alert(`Готово к повторной публикации: ${{result.length}} постов`);
                        location.reload();
                    }} catch (error) {{
                        alert('Ошибка: ' + error.message);
                    }}
                }}
            }}

            async function toggleSource(sourceId, isActive) {{
                const newStatus = !isActive;
                const action = newStatus ? 'включить' : 'выключить';
                
                if (confirm(`Вы уверены, что хотите ${{action}} источник ${{sourceId}}?`)) {{
                    try {{
                        const response = await fetch(`/sources/${{sourceId}}/toggle`, {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json'
                            }}
                        }});
                        
                        if (response.ok) {{
                            const updatedSource = await response.json();
                            alert(`✅ Источник ${{sourceId}} ${{updatedSource.is_active ? 'включён' : 'выключен'}}`);
                            location.reload();
                        }} else {{
                            const error = await response.json();
                            alert(`❌ Ошибка: ${{error.detail || 'Неизвестная ошибка'}}`);
                        }}
                    }} catch (error) {{
                        alert(`❌ Ошибка сети: ${{error.message}}`);
                    }}
                }}
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health/db")
def health_db(db=Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"db": "ok"}
    except Exception as e:
        return {"db": "error", "detail": str(e)}


@app.get("/news/", response_model=list[schemas.NewsItemRead])
def read_news_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_news_items(db, skip=skip, limit=limit)


@app.get("/news/{news_id}", response_model=schemas.NewsItemRead)
def read_news_item(news_id: str, db: Session = Depends(get_db)):
    try:
        news_uuid = uuid.UUID(news_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    news = crud.get_news_item(db, news_uuid)
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")
    return news


@app.post("/news/", response_model=schemas.NewsItemRead, status_code=status.HTTP_201_CREATED)
def create_news_item(news: schemas.NewsItemCreate, db: Session = Depends(get_db)):
    return crud.create_news_item(db, news)


@app.put("/news/{news_id}", response_model=schemas.NewsItemRead)
def update_news_item(news_id: str, news_update: schemas.NewsItemUpdate, db: Session = Depends(get_db)):
    try:
        news_uuid = uuid.UUID(news_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    news = crud.update_news_item(db, news_uuid, news_update)
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")
    return news


@app.delete("/news/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_news_item(news_id: str, db: Session = Depends(get_db)):
    try:
        news_uuid = uuid.UUID(news_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    success = crud.delete_news_item(db, news_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="News item not found")


@app.get("/posts/", response_model=list[schemas.PostRead])
def read_posts(
        post_status: PostStatus = None,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    if post_status:
        return crud.get_posts_by_status(db, post_status, skip=skip, limit=limit)
    return crud.get_posts(db, skip=skip, limit=limit)


@app.post("/posts/retry-failed", response_model=list[uuid.UUID])
def retry_failed_posts_endpoint(db: Session = Depends(get_db)):
    """Переводит все посты со статусом 'failed' в 'draft' для повторной публикации"""
    return crud.retry_failed_posts(db)


@app.get("/posts/{post_id}", response_model=schemas.PostRead)
def read_post(post_id: str, db: Session = Depends(get_db)):
    try:
        post_uuid = uuid.UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    post = crud.get_post(db, post_uuid)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.post("/posts/", response_model=schemas.PostRead, status_code=status.HTTP_201_CREATED)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_post(db, post)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/posts/{post_id}", response_model=schemas.PostRead)
def update_post(post_id: str, post_update: schemas.PostUpdate, db: Session = Depends(get_db)):
    try:
        post_uuid = uuid.UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    post = crud.update_post(db, post_uuid, post_update)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: str, db: Session = Depends(get_db)):
    try:
        post_uuid = uuid.UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    success = crud.delete_post(db, post_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")


@app.post("/publish-posts/", response_model=dict)
def trigger_publish_posts(db: Session = Depends(get_db)):
    """Запускает публикацию постов"""
    # Проверяем, есть ли черновики
    draft_count = crud.get_posts_stats(db)["draft"]
    if draft_count == 0:
        return {"published": 0, "message": "Нет черновиков для публикации"}

    # Запускаем задачу
    from app.tasks import publish_posts_to_telegram
    publish_posts_to_telegram.delay()

    return {
        "published": min(draft_count, settings.MAX_POSTS_PER_PUBLISH),
        "message": f"Запущена публикация до {settings.MAX_POSTS_PER_PUBLISH} постов"
    }


@app.get("/sources/", response_model=list[schemas.NewsSourceRead])
def read_news_sources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_news_sources(db, skip=skip, limit=limit)


@app.get("/sources/{source_id}", response_model=schemas.NewsSourceRead)
def read_news_source(source_id: int, db: Session = Depends(get_db)):
    source = crud.get_news_source(db, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Источник не найден")
    return source


@app.post("/sources/", response_model=schemas.NewsSourceRead, status_code=status.HTTP_201_CREATED)
def create_news_source(source: schemas.NewsSourceCreate, db: Session = Depends(get_db)):
    return crud.create_news_source(db, source)


@app.put("/sources/{source_id}", response_model=schemas.NewsSourceRead)
def update_news_source(source_id: int, source_update: schemas.NewsSourceUpdate, db: Session = Depends(get_db)):
    source = crud.update_news_source(db, source_id, source_update)
    if not source:
        raise HTTPException(status_code=404, detail="Источник не найден")
    return source


@app.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_news_source(source_id: int, db: Session = Depends(get_db)):
    success = crud.delete_news_source(db, source_id)
    if not success:
        raise HTTPException(status_code=404, detail="Источник не найден")


@app.post("/sources/{source_id}/toggle", response_model=schemas.NewsSourceRead)
def toggle_source(
        source_id: int,
        request: Request,
        db: Session = Depends(get_db)
):
    # Проверяем авторизацию
    auth_check = require_auth(request)
    if auth_check:
        raise HTTPException(status_code=403, detail="Требуется авторизация")

    source = crud.get_news_source(db, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Источник не найден")

    source.is_active = not source.is_active
    db.commit()
    db.refresh(source)

    return source