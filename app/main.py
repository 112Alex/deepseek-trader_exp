import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from app.config import BOT_TOKEN, REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD
from app.handlers import user_commands, signal_handler, subs_handler
from app.scheduler.manager import setup_scheduler

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Инициализируем RedisStorage для FSM (как указано в ТЗ)
    # Формируем URL для Redis с учетом пароля
    if REDIS_PASSWORD:
        redis_url = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    else:
        redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    
    redis_storage = RedisStorage.from_url(redis_url)
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=redis_storage)

    # Регистрируем все роутеры
    dp.include_router(user_commands.router)
    dp.include_router(signal_handler.router)
    dp.include_router(subs_handler.router)

    # Запускаем планировщик
    scheduler = setup_scheduler(bot)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        # Закрываем соединения при завершении
        await bot.session.close()
        await redis_storage.close()
        # Закрываем Redis клиент для подписок
        from app.db.redis_storage import redis_client
        await redis_client.aclose()
        if scheduler:
            scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
