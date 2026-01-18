import asyncio
from telethon import TelegramClient
from telethon.errors import ChannelInvalidError, SessionPasswordNeededError
from datetime import datetime
from typing import List, Dict
import logging

from app.config import settings

logger = logging.getLogger(__name__)

class TelegramNewsParser:
    def __init__(self):
        self.client = TelegramClient(
            settings.TELEGRAM_SESSION_NAME,
            settings.TELEGRAM_API_ID,
            settings.TELEGRAM_API_HASH
        )
        self.channels = [
            "webfrl",
            "expert_mag",
            "hahacker_news",
        ]

    async def i_auth(self):
        try:
            phone = input('Введите номер телефона (в формате +7XXXXXXXXXX): ').strip()
            await self.client.send_code_request(phone)
            code = input('Введите код из Telegram: ').strip()
            try:
                await self.client.sign_in(phone, code)
                me = await self.client.get_me()
                logger.info(
                    f'Успешно авторизован как {me.first_name} {me.last_name or ""} (@{me.username or "без username"})')
            except SessionPasswordNeededError:
                password = input('Введите пароль двухфакторной аутентификации: ').strip()
                if not password:
                    logger.error('Пароль не может быть пустым')
                    return

                await self.client.sign_in(password=password)
                me = await self.client.get_me()
                logger.info(
                    f'Успешно авторизован как {me.first_name} {me.last_name or ""} (@{me.username or "без username"})')
        except Exception as e:
            logger.error(f'Ошибка при авторизации: {e}', exc_info=True)
        finally:
            await self.client.disconnect()

    async def parse_all(self) -> List[Dict]:
        # Подключаемся вручную
        await self.client.connect()

        # Если сессия новая — авторизуемся
        if not await self.client.is_user_authorized():
            print("⚠️ Требуется авторизация в Telegram!")
            await self.i_auth()
            await self.client.start()  # Это блокирует выполнение до завершения авторизации

        all_news = []
        try:
            for channel in self.channels:
                try:
                    news = await self._parse_channel(channel)
                    all_news.extend(news)
                    logger.info(f"Fetched {len(news)} items from Telegram channel @{channel}")
                except ChannelInvalidError:
                    logger.warning(f"Channel @{channel} not found or private")
                except Exception as e:
                    logger.error(f"Error parsing @{channel}: {e}")
        finally:
            await self.client.disconnect()

        return all_news

    async def _parse_channel(self, channel: str) -> List[Dict]:
        messages = await self.client.get_messages(channel, limit=15)
        items = []
        for msg in messages:
            if not msg.text or not msg.text.strip():
                continue

            url = f"https://t.me/{channel}/{msg.id}"
            summary = msg.text[:2000]

            items.append({
                "title": self._extract_title(msg.text),
                "url": url,
                "summary": summary,
                "source": f"t.me/{channel}",
                "published_at": msg.date or datetime.utcnow(),
                "raw_text": msg.text
            })
        return items

    @staticmethod
    def _extract_title(text: str) -> str:
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            return lines[0][:80]
        return text[:80]

    def run_sync(self) -> List[Dict]:
        """Запуск в синхронном контексте из Celery"""
        return asyncio.run(self.parse_all())
