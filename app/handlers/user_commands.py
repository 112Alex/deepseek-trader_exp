from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать в Crypto Bot!\n"
        "Я помогу вам получить торговые сигналы на основе технического анализа и AI.\n"
        "Для списка команд используйте /help"
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Доступные команды:\n"
        "/start - Начало работы\n"
        "/help - Показать это сообщение\n"
        "/signal <SYMBOL> <TIMEFRAME> - Получить сигнал по требованию (например, /signal BTC/USDT 1h)\n"
        "/subscribe <SYMBOL> <TIMEFRAME> - Подписаться на рассылку сигналов\n"
        "/unsubscribe <SYMBOL> <TIMEFRAME> - Отписаться от рассылки"
    )
