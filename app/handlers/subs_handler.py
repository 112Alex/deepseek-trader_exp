from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from app.db import redis_storage

router = Router()

@router.message(Command("subscribe"))
async def cmd_subscribe(message: Message):
	args = message.text.split()
	if len(args) != 3:
		await message.answer(
			"Неверный формат. Используйте: /subscribe <СИМВОЛ> <ТАЙМФРЕЙМ>\n"
			"Пример: /subscribe BTC/USDT 1h"
		)
		return

	symbol = args[1].upper()
	timeframe = args[2].lower()
	chat_id = message.chat.id

	await redis_storage.add_subscriber(symbol, timeframe, chat_id)
	await message.answer(f"Вы подписались на сигналы {symbol} {timeframe}.")

@router.message(Command("unsubscribe"))
async def cmd_unsubscribe(message: Message):
	args = message.text.split()
	if len(args) != 3:
		await message.answer(
			"Неверный формат. Используйте: /unsubscribe <СИМВОЛ> <ТАЙМФРЕЙМ>\n"
			"Пример: /unsubscribe BTC/USDT 1h"
		)
		return

	symbol = args[1].upper()
	timeframe = args[2].lower()
	chat_id = message.chat.id

	await redis_storage.remove_subscriber(symbol, timeframe, chat_id)
	await message.answer(f"Вы отписались от сигналов {symbol} {timeframe}.")
