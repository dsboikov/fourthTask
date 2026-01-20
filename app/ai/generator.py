import logging
from app.ai.openai_client import client
from app.config import settings

logger = logging.getLogger(__name__)

async def generate_post_from_news(news_summary: str) -> dict:
    """
    Генерирует пост для Telegram на основе краткого содержания новости.
    Возвращает {'title': str, 'content': str}
    """
    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты редактор популярного IT-канала в Telegram. "
                        "Твоя задача — написать короткий, цепляющий пост (до 1000 символов) на основе новости. "
                        "Используй эмодзи, хештеги и дружелюбный тон. "
                        "Не упоминай источник новости. "
                        "Формат: сначала заголовок (1 строка), затем пустая строка, затем текст поста."
                    )
                },
                {"role": "user", "content": f"Новость: {news_summary}"}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        
        raw_text = response.choices[0].message.content.strip()
        
        # Разделяем на заголовок и контент
        parts = raw_text.split('\n\n', 1)
        if len(parts) == 2:
            title, content = parts
        else:
            # Если нет пустой строки — первая строка как заголовок
            lines = raw_text.split('\n', 1)
            title = lines[0]
            content = lines[1] if len(lines) > 1 else raw_text
        
        return {
            "title": title.strip(),
            "content": content.strip()
        }
        
    except Exception as e:
        logger.error(f"Ошибка генерации поста: {e}")
        raise