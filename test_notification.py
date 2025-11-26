import asyncio
from aiogram import Bot

# Тестируем отправку в группу
ADMIN_CHAT_ID = -1003410520287
BOT_TOKEN = "8236682033:AAFeu-Kt3UWSuxpNmfkUiB_y7eOxlKyHErE"  # Первый бот из списка

async def test_send():
    bot = Bot(token=BOT_TOKEN)

    try:
        print(f"Отправляю тестовое сообщение в чат {ADMIN_CHAT_ID}...")
        result = await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text="✅ Тестовое сообщение от бота\n\nЕсли вы видите это - бот работает правильно!"
        )
        print(f"✅ Успешно отправлено! Message ID: {result.message_id}")
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")
        print("\nВозможные причины:")
        print("1. Бот не добавлен в группу")
        print("2. У бота нет прав на отправку сообщений")
        print("3. Неправильный ID чата")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(test_send())
