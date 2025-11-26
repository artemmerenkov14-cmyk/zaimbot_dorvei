import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# ========== НАСТРОЙКИ ==========
# Админский чат для уведомлений
ADMIN_CHAT_ID = -1003481337231

# Директория для хранения статистики
STATS_DIR = Path("stats_data")
STATS_DIR.mkdir(exist_ok=True)

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


# ========== ФУНКЦИИ КЛАВИАТУР ==========
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
def get_stats_file(bot_id: str):
    """Возвращает путь к файлу статистики для конкретного бота"""
    return STATS_DIR / f"bot_{bot_id}.json"


def load_stats(bot_id: str):
    """Загружает статистику конкретного бота"""
    stats_file = get_stats_file(bot_id)
    if stats_file.exists():
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load stats for bot {bot_id}: {e}")

    return {
        "bot_id": bot_id,
        "users": {},
        "countries": {
            "russia": 0,
            "kazakhstan": 0
        }
    }


def save_stats(bot_id: str, stats):
    """Сохраняет статистику конкретного бота"""
    stats_file = get_stats_file(bot_id)
    try:
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save stats for bot {bot_id}: {e}")


def update_user_stats(bot_id: str, user_id: int, username: str, action: str = None):
    """Обновляет статистику пользователя для конкретного бота"""
    stats = load_stats(bot_id)

    user_id_str = str(user_id)
    now = datetime.now().isoformat()

    if user_id_str not in stats["users"]:
        stats["users"][user_id_str] = {
            "username": username,
            "first_seen": now,
            "last_action": action or "start"
        }
    else:
        stats["users"][user_id_str]["username"] = username
        stats["users"][user_id_str]["last_action"] = action or stats["users"][user_id_str]["last_action"]

    if action == "russia":
        stats["countries"]["russia"] += 1
    elif action == "kazakhstan":
        stats["countries"]["kazakhstan"] += 1

    save_stats(bot_id, stats)
    return stats


async def send_admin_notification(bot: Bot, bot_id: str, user_id: int, username: str, action: str):
    """Отправляет уведомление в админский чат"""
    try:
        message = (
            f"📊 <b>Действие пользователя</b>\n\n"
            f"🤖 Бот ID: <code>{bot_id}</code>\n"
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


# ========== КЛАСС БОТА ==========
class LoanBot:
    """Класс для управления одним ботом"""

    def __init__(self, bot_id: str, bot_token: str):
        self.bot_id = bot_id
        self.bot_token = bot_token
        self.bot = Bot(token=bot_token)
        self.dp = Dispatcher()
        self._setup_handlers()

    def _setup_handlers(self):
        """Настраивает обработчики"""
        self.dp.message.register(self.cmd_start, CommandStart())
        self.dp.callback_query.register(self.callback_country_russia, F.data == "country_russia")
        self.dp.callback_query.register(self.callback_country_kazakhstan, F.data == "country_kazakhstan")
        self.dp.callback_query.register(self.callback_back_to_start, F.data == "back_to_start")

    async def cmd_start(self, message: Message):
        """Обработчик команды /start"""
        logger.info(f"Bot {self.bot_id}: User {message.from_user.id} started")

        update_user_stats(self.bot_id, message.from_user.id, message.from_user.username, "start")

        await send_admin_notification(
            bot=self.bot,
            bot_id=self.bot_id,
            user_id=message.from_user.id,
            username=message.from_user.username,
            action="🚀 Запустил бота (/start)"
        )

        await message.answer(
            text=START_MESSAGE,
            reply_markup=get_country_keyboard()
        )

    async def callback_country_russia(self, callback: CallbackQuery):
        """Обработчик выбора России"""
        logger.info(f"Bot {self.bot_id}: User {callback.from_user.id} selected Russia")

        update_user_stats(self.bot_id, callback.from_user.id, callback.from_user.username, "russia")

        await callback.message.edit_text(
            text=RUSSIA_MESSAGE,
            reply_markup=get_back_keyboard(),
            disable_web_page_preview=True
        )
        await callback.answer()

    async def callback_country_kazakhstan(self, callback: CallbackQuery):
        """Обработчик выбора Казахстана"""
        logger.info(f"Bot {self.bot_id}: User {callback.from_user.id} selected Kazakhstan")

        update_user_stats(self.bot_id, callback.from_user.id, callback.from_user.username, "kazakhstan")

        await callback.message.edit_text(
            text=KAZAKHSTAN_MESSAGE,
            reply_markup=get_back_keyboard(),
            disable_web_page_preview=True
        )
        await callback.answer()

    async def callback_back_to_start(self, callback: CallbackQuery):
        """Обработчик кнопки 'Назад'"""
        logger.info(f"Bot {self.bot_id}: User {callback.from_user.id} returned to start")

        await callback.message.edit_text(
            text=START_MESSAGE,
            reply_markup=get_country_keyboard()
        )
        await callback.answer()

    async def start(self):
        """Запуск бота"""
        try:
            logger.info(f"Starting bot {self.bot_id}...")
            await self.bot.delete_webhook(drop_pending_updates=True)
            await self.dp.start_polling(self.bot, allowed_updates=self.dp.resolve_used_update_types())
        except Exception as e:
            logger.error(f"Bot {self.bot_id} error: {e}")
        finally:
            await self.bot.session.close()
            logger.info(f"Bot {self.bot_id} stopped")
