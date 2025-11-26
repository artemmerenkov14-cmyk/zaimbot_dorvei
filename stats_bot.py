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

# Директория со статистикой всех ботов
STATS_DIR = Path("stats_data")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ========== ФУНКЦИИ СТАТИСТИКИ ==========
def load_all_stats():
    """Загружает и агрегирует статистику со всех ботов"""
    if not STATS_DIR.exists():
        return None

    aggregated_stats = {
        "total_bots": 0,
        "active_bots": 0,
        "all_users": set(),  # Используем set для уникальных пользователей
        "countries": {
            "russia": 0,
            "kazakhstan": 0
        },
        "bot_stats": {}  # Статистика по каждому боту
    }

    # Читаем все файлы статистики
    for stats_file in STATS_DIR.glob("bot_*.json"):
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                bot_stats = json.load(f)
                bot_id = bot_stats.get("bot_id", "unknown")

                aggregated_stats["total_bots"] += 1

                # Если у бота есть пользователи - считаем его активным
                if bot_stats.get("users"):
                    aggregated_stats["active_bots"] += 1

                # Добавляем уникальных пользователей
                for user_id in bot_stats.get("users", {}).keys():
                    aggregated_stats["all_users"].add(user_id)

                # Агрегируем статистику по странам
                aggregated_stats["countries"]["russia"] += bot_stats.get("countries", {}).get("russia", 0)
                aggregated_stats["countries"]["kazakhstan"] += bot_stats.get("countries", {}).get("kazakhstan", 0)

                # Сохраняем статистику конкретного бота
                aggregated_stats["bot_stats"][bot_id] = {
                    "users": len(bot_stats.get("users", {})),
                    "russia": bot_stats.get("countries", {}).get("russia", 0),
                    "kazakhstan": bot_stats.get("countries", {}).get("kazakhstan", 0)
                }

        except Exception as e:
            logger.error(f"Failed to load stats from {stats_file}: {e}")
            continue

    # Конвертируем set обратно в число
    aggregated_stats["total_unique_users"] = len(aggregated_stats["all_users"])
    del aggregated_stats["all_users"]  # Удаляем set, так как он не нужен в выводе

    return aggregated_stats if aggregated_stats["total_bots"] > 0 else None


def format_stats_message(stats):
    """Форматирует сообщение со статистикой"""
    if not stats:
        return "📊 <b>Статистика</b>\n\n❌ Нет данных. Запустите боты командой: python3 run_all_bots.py"

    total_bots = stats.get("total_bots", 0)
    active_bots = stats.get("active_bots", 0)
    total_users = stats.get("total_unique_users", 0)
    russia_count = stats.get("countries", {}).get("russia", 0)
    kazakhstan_count = stats.get("countries", {}).get("kazakhstan", 0)

    message = (
        f"📊 <b>ОБЩАЯ СТАТИСТИКА СЕТИ БОТОВ</b>\n\n"
        f"🤖 <b>Всего ботов:</b> {total_bots}\n"
        f"✅ <b>Активных ботов:</b> {active_bots}\n"
        f"👥 <b>Уникальных пользователей:</b> {total_users}\n\n"
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
            f"🇰🇿 Казахстан: {kazakhstan_percent:.1f}%\n\n"
        )
    else:
        message += "Пока нет выборов стран\n\n"

    # Топ 5 самых активных ботов
    bot_stats = stats.get("bot_stats", {})
    if bot_stats:
        sorted_bots = sorted(
            bot_stats.items(),
            key=lambda x: x[1]["users"],
            reverse=True
        )[:5]

        message += f"🏆 <b>Топ-5 самых активных ботов:</b>\n"
        for i, (bot_id, bot_data) in enumerate(sorted_bots, 1):
            message += (
                f"{i}. Бот {bot_id}: {bot_data['users']} пользователей "
                f"(🇷🇺 {bot_data['russia']} / 🇰🇿 {bot_data['kazakhstan']})\n"
            )

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
    stats = load_all_stats()
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
