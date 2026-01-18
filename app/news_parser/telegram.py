import asyncio
from telethon import TelegramClient
from telethon.errors import ChannelInvalidError
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

    async def _ensure_authorized(self):
        """Автоматическое подключение с проверкой авторизации"""
        await self.client.connect()
        if not await self.client.is_user_authorized():
            # В production-режиме это не должно происходить!
            # Но на случай ошибки — логируем и отключаемся
            logger.error("Telegram session is not authorized. Run `init_telegram` first!")
            await self.client.disconnect()  # type: ignore
            raise RuntimeError("Telegram session not authorized. Please run auth script.")

    async def parse_all(self) -> List[Dict]:
        await self._ensure_authorized()

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
            await self.client.disconnect()  # type: ignore

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
