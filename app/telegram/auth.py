import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from app.config import settings


async def initialize_telegram_session():
    """Интерактивная инициализация сессии Telethon"""
    print("🚀 Инициализация Telegram-сессии...")

    client = TelegramClient(
        settings.TELEGRAM_SESSION_NAME,
        settings.TELEGRAM_API_ID,
        settings.TELEGRAM_API_HASH
    )

    await client.connect()

    if not await client.is_user_authorized():
        print("📱 Требуется авторизация в Telegram.")
        phone = input("Введите номер телефона в международном формате (например, +79991234567): ").strip()

        try:
            # Запрашиваем код
            code_request = await client.send_code_request(phone)

            # Если есть двухфакторная аутентификация
            if code_request.phone_code_hash is None:
                print("❌ Не удалось запросить код. Проверьте номер телефона.")
                return False

            # Ввод кода
            code = input("Введите код из Telegram: ").strip()

            try:
                await client.sign_in(phone, code, phone_code_hash=code_request.phone_code_hash)
            except SessionPasswordNeededError:
                password = input("Введите пароль двухфакторной аутентификации: ")
                await client.sign_in(password=password)

            if await client.is_user_authorized():
                print("✅ Авторизация успешна! Сессия сохранена.")
            else:
                print("❌ Авторизация не завершена.")
                return False

        except Exception as e:
            print(f"❌ Ошибка авторизации: {e}")
            return False
    else:
        print("✅ Сессия уже активна.")

    await client.disconnect()
    return True


if __name__ == "__main__":
    asyncio.run(initialize_telegram_session())