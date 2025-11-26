import asyncio
import logging
from loan_bot_class import LoanBot

# ========== СПИСОК ВСЕХ БОТОВ ==========
BOT_TOKENS = {
    # Основные боты из первого списка
    "7920877021": "7920877021:AAH9Ds5E8wWX-kJ1BKWLlwloJ9vNi_uCDX0",
    "7839466677": "7839466677:AAEUkMe8IT8sDGlWfjJWCoNuhEvPoMl5eDQ",
    "7925604558": "7925604558:AAEozeToobWk3UTV8-y9N2DgaQm0Tf8sLYU",
    "7747890893": "7747890893:AAFoxqhVwNvT_DJh6XhEMkSwo_BoYbEg7lc",
    "7585296020": "7585296020:AAFQcy-hmMviE3w4tsEBG8qNDgd01hJ-hLg",
    "7722763920": "7722763920:AAGfcmbhq3kt-kaKClhq2B6daIA1lvWSOAE",
    "8126783626": "8126783626:AAFU3QNPqE8OjElU2L1MILk71x6aSYwJcUY",
    "7063464189": "7063464189:AAGjzBvwZcvi3LmYnyi41CcStAm4YVhccTM",
    "8123867698": "8123867698:AAE9eCkVy1ShZ10pBPFki0NyZfoKRBH-fHE",
    "8150952830": "8150952830:AAGop0ebkbYqwqZ34s0vxSb6poVBVfxMeRM",
    "8151466695": "8151466695:AAEQAA7OXqDTqg4Kk9lLdN4WB6CGO9He0Vk",
    "8041297599": "8041297599:AAE-PHhID9Fua_9PniS9As-EesDpsPCvwDY",
    "7286478518": "7286478518:AAFEARbC1zYlwVCIkPegEwx-J1eyPLT24IU",
    "7613004423": "7613004423:AAEY7CxhRYI8JA6gUh41mrNnFQYdv5detH8",
    "7270320247": "7270320247:AAFu4TE2beZmtCSrIc4nAwvxt-HEMqZciac",
    "7642842800": "7642842800:AAGWCmvTy55LCqmJ20Zg7Zd7DSpB_IWLKkE",
    "7909237062": "7909237062:AAFpknwPauepQbG_iRdxZVy8SJV2WHFQLyA",
    "7589654399": "7589654399:AAErrlrtUkdY9AX3rvCX5SdHj6lVfKhM83c",
    "8109635276": "8109635276:AAEJcyJGFz3KjFp0qnqck9Mel9U6IIN2AeA",
    "8128384924": "8128384924:AAGKLznKeFTkrVCkC8AnwGsULZGv8Xuqgn4",
    "8192958191": "8192958191:AAEMHaQzNkyY0EUnp_mJwkEmO33fHT0BSYw",
    "7922338982": "7922338982:AAEE3tbdqJZ7QRp9N1f0ZrN5pALYPCEapiI",
    "7792041277": "7792041277:AAHnZ93KgNVgdFeRhPdu0N3Se0sGsJoWepQ",
    "8177227317": "8177227317:AAFixoew7f0U_8YDu5f58kN8Sx34856HlOY",
    "7653622197": "7653622197:AAHISJMy8H9QdUyAA293yuzNHqDvpdEs7_g",
    "7218931285": "7218931285:AAFM721qCcnI4nBf4R-TEtrdSRzwikoBSXI",
    "8078293237": "8078293237:AAGd-BKEKI0h03sh7mcHwvR0nHEaX5Lkw7M",
    "7734014892": "7734014892:AAEzUcLQ4oUfSJ5YqsLPiIjWQ2eCOB7y19k",
    "7276206871": "7276206871:AAGXOHsg-mTjfhy2Gd5UI0NFwIlY-huts1M",
    "7554544329": "7554544329:AAGf9vUWDH2IJCQliDaiqP10Ccm3P-Rbw3M",
    "7147634795": "7147634795:AAHAvyuYHZXcFzoqtztIg8RZDeaeMojUDlg",
    "7763343692": "7763343692:AAGHJfrPFaPODdjOc_91alCpRvPH643Rf9U",
    "7990796999": "7990796999:AAERiPsqhp04b_HEUfAJKgxgA9j3D_pEnR8",
    "7466199972": "7466199972:AAEEzKqA2FJGfGMXfWw-8gL6PEN-LOGkMeo",

    # Новые боты из второго списка
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
