from app.db import redis_storage
from app.services import data_fetcher, analytics, llm_integrator
from aiogram import Bot
import asyncio

# Функция для рассылки сигналов всем подписчикам
async def check_signals_and_notify(bot: Bot):
	subscriptions = await redis_storage.get_all_subscriptions()
	for key in subscriptions:
		# Ключ вида sub:BTCUSDT:1h
		try:
			_, symbol_tf = key.split(":", 1)
			# Разделяем символ и таймфрейм
			# Пример: BTCUSDT:1h
			if ":" in symbol_tf:
				symbol, timeframe = symbol_tf.split(":")
			else:
				# Если формат не соответствует, пропускаем
				continue
			symbol_fmt = symbol[:3] + "/" + symbol[3:]  # BTCUSDT -> BTC/USDT

			# Получаем подписчиков
			subscribers = await redis_storage.get_subscribers(symbol, timeframe)
			if not subscribers:
				continue

			# Получаем данные
			ohlcv_df = await data_fetcher.get_ohlcv(symbol_fmt, timeframe)
			if ohlcv_df is None or ohlcv_df.empty:
				continue

			# Считаем индикаторы
			ta_results = analytics.calculate_indicators(ohlcv_df)
			if not ta_results:
				continue

			# Генерируем сигнал
			signal_text = await llm_integrator.generate_signal(ta_results, symbol_fmt)

			# Отправляем всем подписчикам
			for chat_id in subscribers:
				try:
					await bot.send_message(chat_id=int(chat_id), text=signal_text)
					await asyncio.sleep(0.1)  # чтобы не спамить API Telegram
				except Exception as e:
					print(f"Ошибка отправки сообщения {chat_id}: {e}")
		except Exception as e:
			print(f"Ошибка обработки подписки {key}: {e}")
