import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.config import BOT_TOKEN
from app.handlers import user_commands, signal_handler

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Здесь будут регистрироваться роутеры
    dp.include_router(user_commands.router)
    dp.include_router(signal_handler.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
