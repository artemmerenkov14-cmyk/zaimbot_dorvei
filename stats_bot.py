import asyncio
import logging
import json
from pathlib import Path
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = "8149773704:AAEMPILxahaM1q_iJB1pPq1yesOs4pGSlNs"

# Админский чат, откуда принимать команды
ADMIN_CHAT_ID = -1003481337231

# Файл со статистикой
STATS_FILE = Path("bot_stats.json")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ========== ФУНКЦИИ СТАТИСТИКИ ==========
def load_stats():
    """Загружает статистику из файла"""
    if STATS_FILE.exists():
        try:
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load stats: {e}")
            return None

    return None


def format_stats_message(stats):
    """Форматирует сообщение со статистикой"""
    if not stats:
        return "📊 <b>Статистика</b>\n\n❌ Файл статистики не найден или пуст"

    total_users = len(stats.get("users", {}))
    russia_count = stats.get("countries", {}).get("russia", 0)
    kazakhstan_count = stats.get("countries", {}).get("kazakhstan", 0)

    message = (
        f"📊 <b>СТАТИСТИКА БОТА</b>\n\n"
        f"👥 <b>Всего пользователей:</b> {total_users}\n\n"
        f"🌍 <b>Выбор стран:</b>\n"
        f"🇷🇺 Россия: {russia_count}\n"
        f"🇰🇿 Казахстан: {kazakhstan_count}\n\n"
        f"📈 <b>Процентное соотношение:</b>\n"
    )

    # Вычисляем проценты
    total_country_selections = russia_count + kazakhstan_count
    if total_country_selections > 0:
        russia_percent = (russia_count / total_country_selections) * 100
        kazakhstan_percent = (kazakhstan_count / total_country_selections) * 100
        message += (
            f"🇷🇺 Россия: {russia_percent:.1f}%\n"
            f"🇰🇿 Казахстан: {kazakhstan_percent:.1f}%"
        )
    else:
        message += "Пока нет выборов стран"

    return message


# ========== ОБРАБОТЧИКИ ==========
async def cmd_stats(message: Message):
    """Обработчик команды /stats"""
    # Проверяем, что команда пришла из админского чата
    if message.chat.id != ADMIN_CHAT_ID:
        logger.warning(f"Stats command from unauthorized chat: {message.chat.id}")
        return

    logger.info(f"Stats command received from {message.from_user.id}")

    # Загружаем и отправляем статистику
    stats = load_stats()
    stats_message = format_stats_message(stats)

    await message.answer(
        text=stats_message,
        parse_mode="HTML"
    )


# ========== ГЛАВНАЯ ФУНКЦИЯ ==========
async def main():
    """Основная функция запуска бота"""
    logger.info("Starting stats bot...")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрируем обработчик команды /stats
    dp.message.register(cmd_stats, Command("stats"))

    # Запускаем polling
    try:
        logger.info("Stats bot is running...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    finally:
        await bot.session.close()
        logger.info("Stats bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stats bot stopped by user")
