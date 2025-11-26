import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp_socks import ProxyConnector

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Замените на ваш токен

# Настройки прокси (опционально)
USE_PROXY = False  # Установите True, если нужен прокси
PROXY_HOST = "213.226.78.86"
PROXY_PORT = 8000
PROXY_USERNAME = "E5XeXW"
PROXY_PASSWORD = "PcnzYp"
PROXY_TYPE = "socks5"

# Формируем URL прокси
PROXY_URL = f"{PROXY_TYPE}://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}"

# Админский чат для уведомлений
ADMIN_CHAT_ID = -1003481337231

# Файл для хранения статистики
STATS_FILE = Path("bot_stats.json")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== ТЕКСТЫ СООБЩЕНИЙ ==========
START_MESSAGE = """Привет, я Бот 🤖 который поможет получить деньги 💸

Не хватает сейчас?
Я выручу!

Выберите страну для займа👇🏻"""

RUSSIA_MESSAGE = """✅Чтобы получить займ от 10 до 200 тыс. руб. необходимо перейти по одной из ссылок ниже и заполнить анкету на сайте. (В течение 5 минут деньги придут вам на карту):

🙋‍♀Совет: чтобы увеличить вероятность и скорость одобрения займа, оставьте анкеты сразу во всех компаниях!

💳 Займы для Граждан Российской Федерации 🇷🇺:

❤️ЗАЙМЕР - Акция «Первый займ под 0%»
➡️ https://cutt.ly/ctttvFaX

🔥Е-КАПУСТА - первый займ до 50 000 руб.
➡️ https://cutt.ly/htttbJ2N

MONEYMAN - Первый займ под 0%.
➡️ https://cutt.ly/5tttbqMb

LIME-ZAIM - 20.000₽ под 0% на 15 дней
➡️ https://cutt.ly/3tttHzwR

ONECLICKMONEY - Первый займ до 30.000₽
➡️ https://cutt.ly/ktttHg0j

А.ДЕНЬГИ - Первые 21 дней — бесплатно
➡️ https://cutt.ly/ytttHtBC

PAYPS - 10.000₽ под 0%
➡️ https://cutt.ly/GtttHqIs

МИГКРЕДИТ - первый займ до 100.000 руб
➡️ https://cutt.ly/0tttG7WU

СРОЧНОДЕНЬГИ - первый займ до 100.000 руб
➡️ https://cutt.ly/ztttG9b6

ТУРБОЗАЙМ - первый займ до 100.000 руб
➡️ https://cutt.ly/ZtttGM1T

ВЕББАНКИР - первый займ до 100.000 руб
➡️ https://cutt.ly/7tttGXyX

СМС Финанс - 7 дней без %
➡️ https://cutt.ly/xtttGJ4t

Credit7 - Первый Заем бесплатно
➡️ https://cutt.ly/ttttGSRM

BelkaCredit - Первый Заем бесплатно
➡️ https://cutt.ly/ZtttGRFC

Деньга - 14 дней без %
➡️ https://cutt.ly/xtttGmPq

Микроклад - До 15.000р на первый займ
➡️ https://cutt.ly/htttGxqq"""

KAZAKHSTAN_MESSAGE = """✅Чтобы получить необходимо перейти по одной из ссылок ниже и заполнить анкету на сайте. (В течение 5 минут деньги придут вам на карту):

🙋‍♀Совет: чтобы увеличить вероятность и скорость одобрения займа, оставьте анкеты сразу во всех компаниях!

CreditBar - Автоматическое одобрение 70 000 тенге
➡ https://cutt.ly/YeYPVWtv

Credit365 - До 145.000 тенге без переплат
➡ https://cutt.ly/yeYPVBUU

CreditPlus - Первый займ под 0.00%
➡ https://cutt.ly/YeYPBzvB

Quant - Первый займ под 0.00%
➡ https://cutt.ly/ieYPBZ8l

Acredit - Микрокредит под 0% до 145.000 тенге
➡ https://cutt.ly/FeYPNt2p

Vivus - до 170.000 тенге без %
➡ https://cutt.ly/XeYPNQwo"""


# ========== ФУНКЦИИ СОЗДАНИЯ КЛАВИАТУР ==========
def get_country_keyboard():
    """Создает клавиатуру с выбором страны"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Россия", callback_data="country_russia")],
        [InlineKeyboardButton(text="🇰🇿 Казахстан", callback_data="country_kazakhstan")]
    ])
    return keyboard


def get_back_keyboard():
    """Создает клавиатуру с кнопкой 'Назад'"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_start")]
    ])
    return keyboard


# ========== ФУНКЦИИ СТАТИСТИКИ ==========
def load_stats():
    """Загружает статистику из файла"""
    if STATS_FILE.exists():
        try:
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load stats: {e}")

    # Возвращаем пустую статистику
    return {
        "users": {},  # {user_id: {"username": "...", "first_seen": "...", "last_action": "..."}}
        "countries": {
            "russia": 0,
            "kazakhstan": 0
        }
    }


def save_stats(stats):
    """Сохраняет статистику в файл"""
    try:
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save stats: {e}")


def update_user_stats(user_id: int, username: str, action: str = None):
    """Обновляет статистику пользователя"""
    stats = load_stats()

    user_id_str = str(user_id)
    now = datetime.now().isoformat()

    # Добавляем или обновляем пользователя
    if user_id_str not in stats["users"]:
        stats["users"][user_id_str] = {
            "username": username,
            "first_seen": now,
            "last_action": action or "start"
        }
    else:
        stats["users"][user_id_str]["username"] = username
        stats["users"][user_id_str]["last_action"] = action or stats["users"][user_id_str]["last_action"]

    # Обновляем счетчик стран
    if action == "russia":
        stats["countries"]["russia"] += 1
    elif action == "kazakhstan":
        stats["countries"]["kazakhstan"] += 1

    save_stats(stats)
    return stats


async def send_admin_notification(bot: Bot, user_id: int, username: str, action: str):
    """Отправляет уведомление в админский чат"""
    try:
        message = (
            f"📊 <b>Действие пользователя</b>\n\n"
            f"👤 User ID: <code>{user_id}</code>\n"
            f"📝 Username: @{username if username else 'Не указан'}\n"
            f"🎯 Действие: {action}"
        )
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=message,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to send admin notification: {e}")


# ========== ОБРАБОТЧИКИ ==========
async def cmd_start(message: Message, bot: Bot):
    """Обработчик команды /start"""
    logger.info(f"User {message.from_user.id} ({message.from_user.username}) started the bot")

    # Сохраняем статистику пользователя
    update_user_stats(message.from_user.id, message.from_user.username, "start")

    # Отправляем уведомление в админский чат
    await send_admin_notification(
        bot=bot,
        user_id=message.from_user.id,
        username=message.from_user.username,
        action="🚀 Запустил бота (/start)"
    )

    await message.answer(
        text=START_MESSAGE,
        reply_markup=get_country_keyboard()
    )


async def callback_country_russia(callback: CallbackQuery, bot: Bot):
    """Обработчик выбора России"""
    logger.info(f"User {callback.from_user.id} selected Russia")

    # Сохраняем статистику выбора страны
    update_user_stats(callback.from_user.id, callback.from_user.username, "russia")

    await callback.message.edit_text(
        text=RUSSIA_MESSAGE,
        reply_markup=get_back_keyboard(),
        disable_web_page_preview=True
    )
    await callback.answer()


async def callback_country_kazakhstan(callback: CallbackQuery, bot: Bot):
    """Обработчик выбора Казахстана"""
    logger.info(f"User {callback.from_user.id} selected Kazakhstan")

    # Сохраняем статистику выбора страны
    update_user_stats(callback.from_user.id, callback.from_user.username, "kazakhstan")

    await callback.message.edit_text(
        text=KAZAKHSTAN_MESSAGE,
        reply_markup=get_back_keyboard(),
        disable_web_page_preview=True
    )
    await callback.answer()


async def callback_back_to_start(callback: CallbackQuery):
    """Обработчик кнопки 'Назад'"""
    logger.info(f"User {callback.from_user.id} returned to start")

    await callback.message.edit_text(
        text=START_MESSAGE,
        reply_markup=get_country_keyboard()
    )
    await callback.answer()


# ========== ГЛАВНАЯ ФУНКЦИЯ ==========
async def main():
    """Основная функция запуска бота"""

    # Создаем бота с прокси или без
    if USE_PROXY:
        logger.info(f"Starting bot with proxy: {PROXY_HOST}:{PROXY_PORT}")
        bot = Bot(token=BOT_TOKEN, proxy=PROXY_URL)
    else:
        logger.info("Starting bot without proxy")
        bot = Bot(token=BOT_TOKEN)

    # Создаем диспетчер
    dp = Dispatcher()

    # Регистрируем обработчики
    dp.message.register(cmd_start, CommandStart())
    dp.callback_query.register(callback_country_russia, F.data == "country_russia")
    dp.callback_query.register(callback_country_kazakhstan, F.data == "country_kazakhstan")
    dp.callback_query.register(callback_back_to_start, F.data == "back_to_start")

    # Удаляем webhook и запускаем polling
    try:
        logger.info("Bot is starting...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    finally:
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
