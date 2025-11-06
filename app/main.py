import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.config import BOT_TOKEN
from app.handlers import user_commands, signal_handler, subs_handler
from app.scheduler.manager import setup_scheduler

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрируем все роутеры
    dp.include_router(user_commands.router)
    dp.include_router(signal_handler.router)
    dp.include_router(subs_handler.router)

    # Запускаем планировщик
    setup_scheduler(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
