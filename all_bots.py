import asyncio
import logging
import json
from pathlib import Path
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# ========== НАСТРОЙКИ ==========
# Админский чат для уведомлений
ADMIN_CHAT_ID = -1003410520287

# Директория для хранения статистики
STATS_DIR = Path("stats_data")
STATS_DIR.mkdir(exist_ok=True)

# Файл для хранения токенов ботов
TOKENS_FILE = Path("bot_tokens.json")

# Токен статистического бота
STATS_BOT_TOKEN = "8149773704:AAEMPILxahaM1q_iJB1pPq1yesOs4pGSlNs"

# Список всех основных ботов (будет загружен из файла)
BOT_TOKENS = {}

# Username'ы ботов (будут заполнены автоматически при старте)
BOT_USERNAMES = {}

# Словарь для хранения запущенных ботов (bot_id: task)
RUNNING_BOTS = {}

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


# ========== ФУНКЦИИ УПРАВЛЕНИЯ ТОКЕНАМИ ==========
def load_tokens():
    """Загружает токены ботов из файла"""
    if TOKENS_FILE.exists():
        try:
            with open(TOKENS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load tokens: {e}")
            return {}

    # Если файл не существует, создаем с начальными токенами
    initial_tokens = {
        "8236682033": "8236682033:AAFeu-Kt3UWSuxpNmfkUiB_y7eOxlKyHErE",
        "8512131261": "8512131261:AAFzPt_cZjJYwObhKWkQb0IYmcA1scAaZs0",
        "8487915930": "8487915930:AAEjmQ9gKrg8fN53KQUdoEwBYJPyNQz7Kqk",
        "8522600978": "8522600978:AAFdjdcREfPFE_Ak4GbWHZ0u9hpb2RxWJ1I",
        "8263965404": "8263965404:AAHr7cDbSbXPbYU1k2zX3iNB-_Jt3R5bRuA",
        "8557307240": "8557307240:AAGHsOWEsHJYF_vhC39XXsUGVAl7kUg9Zxs",
        "8587347355": "8587347355:AAECr0VrZf4XkJpH7xtf5P8IChEpB42oMME"
    }
    save_tokens(initial_tokens)
    return initial_tokens


def save_tokens(tokens):
    """Сохраняет токены ботов в файл"""
    try:
        with open(TOKENS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tokens, f, ensure_ascii=False, indent=2)
        logger.info(f"Tokens saved successfully: {len(tokens)} bots")
    except Exception as e:
        logger.error(f"Failed to save tokens: {e}")


async def validate_and_add_token(token: str):
    """Валидирует токен и добавляет его в систему"""
    # Базовая проверка формата токена (должен быть вида "123456:ABC-DEF...")
    if not token or ':' not in token:
        return False, "❌ Неверный формат токена"

    try:
        # Пытаемся получить информацию о боте
        test_bot = Bot(token=token)
        me = await test_bot.get_me()
        bot_id = str(me.id)
        username = f"@{me.username}" if me.username else f"Bot {bot_id}"
        await test_bot.session.close()

        # Проверяем, не добавлен ли уже этот бот
        if bot_id in BOT_TOKENS:
            return False, f"❌ Бот {username} уже добавлен в систему"

        # Добавляем токен в словарь и сохраняем
        BOT_TOKENS[bot_id] = token
        BOT_USERNAMES[bot_id] = username
        save_tokens(BOT_TOKENS)

        # Запускаем бота
        task = asyncio.create_task(run_loan_bot(bot_id, token))
        RUNNING_BOTS[bot_id] = task

        logger.info(f"✅ New bot added and started: {username} ({bot_id})")
        return True, f"✅ Бот {username} успешно добавлен и запущен!\n\n🤖 ID: <code>{bot_id}</code>"

    except Exception as e:
        logger.error(f"Failed to validate token: {e}")
        return False, f"❌ Ошибка валидации токена: {type(e).__name__}"


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


def load_all_stats():
    """Загружает и агрегирует статистику со всех ботов"""
    if not STATS_DIR.exists():
        return None

    aggregated_stats = {
        "total_bots": 0,
        "active_bots": 0,
        "all_users": set(),
        "countries": {
            "russia": 0,
            "kazakhstan": 0
        },
        "bot_stats": {}
    }

    for stats_file in STATS_DIR.glob("bot_*.json"):
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                bot_stats = json.load(f)
                bot_id = bot_stats.get("bot_id", "unknown")

                aggregated_stats["total_bots"] += 1

                if bot_stats.get("users"):
                    aggregated_stats["active_bots"] += 1

                for user_id in bot_stats.get("users", {}).keys():
                    aggregated_stats["all_users"].add(user_id)

                aggregated_stats["countries"]["russia"] += bot_stats.get("countries", {}).get("russia", 0)
                aggregated_stats["countries"]["kazakhstan"] += bot_stats.get("countries", {}).get("kazakhstan", 0)

                aggregated_stats["bot_stats"][bot_id] = {
                    "users": len(bot_stats.get("users", {})),
                    "russia": bot_stats.get("countries", {}).get("russia", 0),
                    "kazakhstan": bot_stats.get("countries", {}).get("kazakhstan", 0)
                }

        except Exception as e:
            logger.error(f"Failed to load stats from {stats_file}: {e}")
            continue

    aggregated_stats["total_unique_users"] = len(aggregated_stats["all_users"])
    del aggregated_stats["all_users"]

    return aggregated_stats if aggregated_stats["total_bots"] > 0 else None


def format_stats_message(stats):
    """Форматирует сообщение со статистикой"""
    if not stats:
        return "📊 <b>Статистика</b>\n\n❌ Нет данных."

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

    bot_stats = stats.get("bot_stats", {})
    if bot_stats:
        sorted_bots = sorted(
            bot_stats.items(),
            key=lambda x: x[1]["users"],
            reverse=True
        )[:5]

        message += f"🏆 <b>Топ-5 самых активных ботов:</b>\n"
        for i, (bot_id, bot_data) in enumerate(sorted_bots, 1):
            bot_username = BOT_USERNAMES.get(bot_id, f"Bot {bot_id}")
            message += (
                f"{i}. {bot_username}: {bot_data['users']} пользователей "
                f"(🇷🇺 {bot_data['russia']} / 🇰🇿 {bot_data['kazakhstan']})\n"
            )

    return message


async def send_admin_notification(bot: Bot, bot_id: str, user_id: int, username: str, action: str):
    """Отправляет уведомление в админский чат"""
    try:
        bot_username = BOT_USERNAMES.get(bot_id, f"Bot {bot_id}")
        message = (
            f"📊 <b>Действие пользователя</b>\n\n"
            f"🤖 Бот: {bot_username}\n"
            f"👤 User ID: <code>{user_id}</code>\n"
            f"📝 Username: @{username if username else 'Не указан'}\n"
            f"🎯 Действие: {action}"
        )
        logger.info(f"Sending notification to chat {ADMIN_CHAT_ID}")
        result = await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=message,
            parse_mode="HTML"
        )
        logger.info(f"Notification sent successfully: message_id={result.message_id}")
    except Exception as e:
        logger.error(f"Failed to send admin notification to {ADMIN_CHAT_ID}: {type(e).__name__}: {e}")


# ========== КЛАСС ОСНОВНОГО БОТА ==========
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


# ========== СТАТИСТИЧЕСКИЙ БОТ ==========
async def cmd_stats(message: Message):
    """Обработчик команды /stats - работает только в админском чате"""
    # Проверяем, что команда пришла из админского чата
    if message.chat.id != ADMIN_CHAT_ID:
        logger.warning(f"Stats command from unauthorized chat: {message.chat.id}")
        return

    logger.info(f"Stats command received from {message.from_user.id} in admin chat")

    stats = load_all_stats()
    stats_message = format_stats_message(stats)

    await message.answer(
        text=stats_message,
        parse_mode="HTML"
    )


async def cmd_add(message: Message):
    """Обработчик команды /add <tokens> - добавляет одного или несколько ботов"""
    # Проверяем, что команда пришла из админского чата
    if message.chat.id != ADMIN_CHAT_ID:
        logger.warning(f"Add command from unauthorized chat: {message.chat.id}")
        return

    # Извлекаем токены из сообщения
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "❌ <b>Использование:</b> /add &lt;токен(ы)&gt;\n\n"
            "<b>Один токен:</b>\n"
            "/add 123456789:ABCdefGHIjklMNOpqrsTUVwxyz\n\n"
            "<b>Несколько токенов (через пробел):</b>\n"
            "/add токен1 токен2 токен3\n\n"
            "<b>Несколько токенов (построчно):</b>\n"
            "/add\n"
            "токен1\n"
            "токен2\n"
            "токен3",
            parse_mode="HTML"
        )
        return

    # Парсим токены - поддерживаем разделение пробелами, новыми строками и запятыми
    tokens_text = parts[1].strip()
    # Заменяем запятые на пробелы, затем разделяем по пробелам и новым строкам
    tokens_text = tokens_text.replace(',', ' ')
    raw_tokens = tokens_text.split()

    # Очищаем токены от кавычек
    tokens = [token.strip().strip('"').strip("'") for token in raw_tokens if token.strip()]

    if not tokens:
        await message.answer("❌ Не найдено ни одного токена")
        return

    logger.info(f"Add command received for {len(tokens)} token(s)")

    # Отправляем сообщение о начале проверки
    status_msg = await message.answer(
        f"⏳ Обрабатываю {len(tokens)} токен(ов)...\n\n"
        "Это может занять некоторое время."
    )

    # Счетчики результатов
    success_count = 0
    failed_count = 0
    results = []

    # Обрабатываем каждый токен
    for i, token in enumerate(tokens, 1):
        logger.info(f"Processing token {i}/{len(tokens)}: {token[:20]}...")

        # Валидируем и добавляем токен
        success, result_message = await validate_and_add_token(token)

        if success:
            success_count += 1
            results.append(f"✅ {i}. {result_message.split('✅ Бот ')[1].split(' успешно')[0]}")
        else:
            failed_count += 1
            # Извлекаем короткое сообщение об ошибке
            error_msg = result_message.replace('❌ ', '')
            results.append(f"❌ {i}. {error_msg}")

    # Формируем итоговое сообщение
    summary = (
        f"📊 <b>Результаты обработки:</b>\n\n"
        f"✅ Успешно добавлено: {success_count}\n"
        f"❌ Ошибок: {failed_count}\n"
        f"📝 Всего обработано: {len(tokens)}\n\n"
        f"<b>Детали:</b>\n"
    )

    # Добавляем результаты (ограничиваем вывод если много токенов)
    if len(results) <= 20:
        summary += "\n".join(results)
    else:
        # Показываем первые 15 и последние 5
        summary += "\n".join(results[:15])
        summary += f"\n\n... (скрыто {len(results) - 20} результатов) ...\n\n"
        summary += "\n".join(results[-5:])

    # Обновляем сообщение с результатом
    await status_msg.edit_text(summary, parse_mode="HTML")


async def cmd_list(message: Message):
    """Обработчик команды /list - показывает список всех ботов"""
    # Проверяем, что команда пришла из админского чата
    if message.chat.id != ADMIN_CHAT_ID:
        logger.warning(f"List command from unauthorized chat: {message.chat.id}")
        return

    logger.info(f"List command received from {message.from_user.id} in admin chat")

    if not BOT_TOKENS:
        await message.answer("❌ Нет активных ботов")
        return

    response = f"🤖 <b>Список активных ботов:</b> {len(BOT_TOKENS)}\n\n"

    for bot_id, token in BOT_TOKENS.items():
        username = BOT_USERNAMES.get(bot_id, f"Bot {bot_id}")
        status = "✅ Запущен" if bot_id in RUNNING_BOTS else "⏸ Остановлен"
        response += f"{status} {username}\n📱 ID: <code>{bot_id}</code>\n\n"

    await message.answer(response, parse_mode="HTML")


async def run_stats_bot():
    """Запуск статистического бота"""
    try:
        logger.info("Starting stats bot...")
        bot = Bot(token=STATS_BOT_TOKEN)
        dp = Dispatcher()

        # Регистрируем команды
        dp.message.register(cmd_stats, Command("stats"))
        dp.message.register(cmd_add, Command("add"))
        dp.message.register(cmd_list, Command("list"))

        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Stats bot error: {e}")
    finally:
        await bot.session.close()
        logger.info("Stats bot stopped")


async def fetch_bot_username(bot_id: str, bot_token: str):
    """Получает username бота через API"""
    try:
        bot = Bot(token=bot_token)
        me = await bot.get_me()
        username = f"@{me.username}" if me.username else f"Bot {bot_id}"
        await bot.session.close()
        return username
    except Exception as e:
        logger.error(f"Failed to get username for bot {bot_id}: {e}")
        return f"Bot {bot_id}"


async def run_loan_bot(bot_id: str, bot_token: str):
    """Запускает один бот займов"""
    try:
        bot = LoanBot(bot_id, bot_token)
        await bot.start()
    except Exception as e:
        logger.error(f"Failed to start bot {bot_id}: {e}")


# ========== ГЛАВНАЯ ФУНКЦИЯ ==========
async def main():
    """Запускает все боты одновременно"""
    global BOT_TOKENS

    # Загружаем токены из файла
    logger.info("📂 Загрузка токенов ботов из файла...")
    BOT_TOKENS = load_tokens()

    logger.info("=" * 60)
    logger.info(f"🚀 ЗАПУСК ВСЕХ БОТОВ")
    logger.info("=" * 60)
    logger.info(f"📊 Основных ботов: {len(BOT_TOKENS)}")
    logger.info(f"📈 Статистический бот: 1")
    logger.info(f"📊 Всего ботов: {len(BOT_TOKENS) + 1}")
    logger.info("=" * 60)

    # Получаем username'ы всех ботов через API
    logger.info("🔍 Получение username'ов ботов через API...")
    username_tasks = []
    for bot_id, bot_token in BOT_TOKENS.items():
        task = fetch_bot_username(bot_id, bot_token)
        username_tasks.append((bot_id, task))

    # Ждем получения всех username'ов
    for bot_id, task in username_tasks:
        username = await task
        BOT_USERNAMES[bot_id] = username
        logger.info(f"✅ {bot_id} → {username}")

    logger.info("=" * 60)

    tasks = []

    # Добавляем задачи для основных ботов
    for bot_id, bot_token in BOT_TOKENS.items():
        task = asyncio.create_task(run_loan_bot(bot_id, bot_token))
        tasks.append(task)
        RUNNING_BOTS[bot_id] = task
        logger.info(f"✅ Основной бот {BOT_USERNAMES.get(bot_id, bot_id)} добавлен в очередь")

    # Добавляем задачу для статистического бота
    stats_task = asyncio.create_task(run_stats_bot())
    tasks.append(stats_task)
    logger.info(f"✅ Статистический бот добавлен в очередь")

    logger.info("=" * 60)
    logger.info("🔄 Запуск всех ботов...")
    logger.info("=" * 60)

    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⛔ Все боты остановлены пользователем")
