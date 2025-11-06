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
                symbol_raw, timeframe = symbol_tf.split(":")
            else:
                # Если формат не соответствует, пропускаем
                continue
            
            # Преобразуем символ обратно в формат с "/"
            # Ищем позицию, где заканчивается базовая валюта (обычно 3-4 символа)
            # Список популярных базовых валют для определения длины
            base_currencies = ['BTC', 'ETH', 'BNB', 'SOL', 'ADA', 'XRP', 'DOT', 'DOGE', 'MATIC', 'LTC', 'AVAX', 'UNI', 'LINK', 'ATOM', 'ETC', 'XLM', 'ALGO', 'VET', 'ICP', 'FIL', 'TRX', 'EOS', 'AAVE', 'THETA', 'XTZ', 'AXS', 'SAND', 'MANA', 'FLOW', 'NEAR', 'FTM', 'GRT', 'CHZ', 'ENJ', 'HBAR', 'ZIL', 'BAT', 'ZEC', 'DASH', 'WAVES', 'MKR', 'COMP', 'YFI', 'SNX', 'SUSHI', 'CRV', '1INCH', 'ALPHA', 'ZEN', 'SKL', 'STORJ']
            
            symbol_fmt = symbol_raw
            # Пытаемся найти известную базовую валюту
            for base in sorted(base_currencies, key=len, reverse=True):
                if symbol_raw.startswith(base):
                    symbol_fmt = f"{base}/{symbol_raw[len(base):]}"
                    break
            
            # Если не нашли известную валюту, используем эвристику (первые 3-4 символа)
            if symbol_fmt == symbol_raw:
                # Пробуем разделить по 3 символам (BTC/USDT)
                if len(symbol_raw) >= 6:
                    symbol_fmt = f"{symbol_raw[:3]}/{symbol_raw[3:]}"
                elif len(symbol_raw) >= 7:
                    # Пробуем разделить по 4 символам (MATIC/USDT)
                    symbol_fmt = f"{symbol_raw[:4]}/{symbol_raw[4:]}"
                else:
                    continue

            # Получаем подписчиков (используем symbol_raw, так как ключ в Redis без "/")
            subscribers = await redis_storage.get_subscribers(symbol_raw, timeframe)
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
