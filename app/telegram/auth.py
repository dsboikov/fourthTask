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
        while True:
            phone = input("Введите номер телефона в международном формате (например, +79991234567): ").strip()
            if phone.startswith('+') and phone[1:].isdigit():
                break
            print("❌ Неверный формат. Номер должен начинаться с '+' и содержать только цифры.")

        try:
            # Запрашиваем код и сохраняем phone_code_hash
            code_request = await client.send_code_request(phone)
            print(f"✅ Запрос кода отправлен. Phone code hash: {code_request.phone_code_hash}")

            code = input("Введите код из Telegram: ").strip()

            try:
                # Передаём phone_code_hash
                result = await client.sign_in(
                    phone=phone,
                    code=code,
                    phone_code_hash=code_request.phone_code_hash
                )
                print(f"🔍 Результат sign_in: {result}")

                if await client.is_user_authorized():
                    print("✅ Авторизация успешна! Сессия сохранена.")
                else:
                    print("❌ Сессия не активна после sign_in.")
                    return False

            except SessionPasswordNeededError:
                print("🔑 Требуется пароль двухфакторной аутентификации.")
                password = input("Введите пароль: ")
                result = await client.sign_in(password=password)
                print(f"🔍 Результат 2FA sign_in: {result}")

                if await client.is_user_authorized():
                    print("✅ Авторизация с 2FA успешна!")
                else:
                    print("❌ Сессия не активна после 2FA.")
                    return False

        except Exception as e:
            print(f"❌ Исключение при sign_in: {type(e).__name__}: {e}")
            return False
    else:
        print("✅ Сессия уже активна.")

    await client.disconnect()  # type: ignore
    # Проверим, что файл сессии создан
    import os
    session_file = f"{settings.TELEGRAM_SESSION_NAME}.session"
    if os.path.exists(session_file):
        print(f"📁 Файл сессии сохранён: {session_file}")
    else:
        print(f"❌ Файл сессии НЕ найден: {session_file}")

    return True


if __name__ == "__main__":
    asyncio.run(initialize_telegram_session())