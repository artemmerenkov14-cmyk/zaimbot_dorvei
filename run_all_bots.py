import asyncio
import logging
from loan_bot_class import LoanBot

# ========== СПИСОК ВСЕХ БОТОВ ==========
BOT_TOKENS = {
    # Активные боты
    "8236682033": "8236682033:AAFeu-Kt3UWSuxpNmfkUiB_y7eOxlKyHErE",
    "8512131261": "8512131261:AAHgbkXUzEA17cjmTL1DhUVj_w_nLRRlmxE",
    "8487915930": "8487915930:AAEOjW-EM3adl2d0JFU0gSqv-qPA0u9-jC0",
    "8522600978": "8522600978:AAHYw9idOsu8w4S336lroAGRsr8aDODeP9I",
    "8263965404": "8263965404:AAEDuMdtm3S5XvT7_YfnARMr_mYzvg5Y95U",
    "8557307240": "8557307240:AAE5Bm3DMkc1AnSx-Qh9o1LLDsJnk48bOlQ",
    "8587347355": "8587347355:AAGuRoCpPv4ew0eJySICQeRMTnnYIXZQ5Wg",
}

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_bot(bot_id: str, bot_token: str):
    """Запускает один бот"""
    try:
        bot = LoanBot(bot_id, bot_token)
        await bot.start()
    except Exception as e:
        logger.error(f"Failed to start bot {bot_id}: {e}")


async def main():
    """Запускает все боты одновременно"""
    logger.info("=" * 60)
    logger.info(f"🚀 ЗАПУСК СЕТКИ БОТОВ")
    logger.info("=" * 60)
    logger.info(f"📊 Всего ботов: {len(BOT_TOKENS)}")
    logger.info("=" * 60)

    # Создаем задачи для всех ботов
    tasks = []
    for bot_id, bot_token in BOT_TOKENS.items():
        task = asyncio.create_task(run_bot(bot_id, bot_token))
        tasks.append(task)
        logger.info(f"✅ Бот {bot_id} добавлен в очередь запуска")

    logger.info("=" * 60)
    logger.info("🔄 Запуск всех ботов...")
    logger.info("=" * 60)

    # Запускаем все боты одновременно
    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⛔ Все боты остановлены пользователем")
