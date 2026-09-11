import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from .config import load_settings
from .api.vast_client import VastApiClient
from .middlewares.auth import AdminAuthMiddleware
from .handlers import setup_routers


async def main():
    settings = load_settings()

    logging.basicConfig(
        level=settings.logging_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logger = logging.getLogger("bot")
    logger.info("Starting Vast.ai Telegram Bot...")

    bot = Bot(token=settings.telegram_bot_token, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())

    vast_client = VastApiClient(
        api_key=settings.vast_api_key,
        base_url=settings.vast_api_base_url,
    )

    # Register admin authentication middleware
    auth_middleware = AdminAuthMiddleware(admin_ids=settings.admin_ids)
    dp.message.middleware(auth_middleware)
    dp.callback_query.middleware(auth_middleware)

    # Dependency injection: make vast_client available in all handler arguments
    dp["vast_client"] = vast_client
    dp["settings"] = settings

    # Include handler routers
    main_router = setup_routers()
    dp.include_router(main_router)

    try:
        # Delete webhook to ensure polling starts cleanly
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Bot started successfully. Listening for updates...")
        await dp.start_polling(bot)
    finally:
        logger.info("Shutting down bot...")
        await vast_client.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped by user.")
