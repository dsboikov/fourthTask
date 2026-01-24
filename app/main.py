from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import text
from app.database import get_db
from app.config import settings
from app.logging_config import setup_logging
from sqlalchemy.orm import Session
from app.api import crud, schemas
from app.api.schemas import PostStatus
from fastapi.responses import HTMLResponse
import uuid

setup_logging()
app = FastAPI(title="AI Telegram Post Generator")


@app.get("/", response_class=HTMLResponse)
def dashboard(db: Session = Depends(get_db)):
    # Получаем статистику
    news_stats = crud.get_news_stats(db)
    posts_stats = crud.get_posts_stats(db)

    # Генерируем HTML
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
                <a href="/docs" target="_blank">📚 API документация</a>
                <a href="/posts/?post_status=draft" target="_blank">📄 Черновики</a>
                <a href="#" onclick="publishPosts(); return false;" class="draft">📤 Опубликовать черновики</a>
                <a href="/posts/?post_status=failed" class="failed" target="_blank">❌ Посты с ошибкой отправки</a>
                <a href="#" onclick="retryFailed(); return false;" class="failed">
                    🔄 Повторить отправку постов с ошибкой отправки</a>
            </div>
        </div>

        <script>
            async function publishPosts() {{
                const maxPosts = {settings.MAX_POSTS_PER_PUBLISH};
                if (confirm(`Опубликовать до ${{maxPosts}} черновиков?`)) {{
                    try {{
                        const response = await fetch('/publish-posts/', {{ method: 'POST' }});
                        const result = await response.json();
                        alert(`Опубликовано: ${{result.published}} постов`);
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
    return crud.create_post(db, post)


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
    return {"published": draft_count, "message": f"Запущена публикация до {settings.MAX_POSTS_PER_PUBLISH} постов"}
