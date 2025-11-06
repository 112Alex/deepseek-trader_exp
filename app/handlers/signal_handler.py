from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from app.services import data_fetcher, analytics, llm_integrator

router = Router()

@router.message(Command("signal"))
async def cmd_signal(message: Message):
    args = message.text.split()
    if len(args) != 3:
        await message.answer(
            "Неверный формат. Используйте: /signal <СИМВОЛ> <ТАЙМФРЕЙМ>\n"
            "Пример: /signal BTC/USDT 1h"
        )
        return

    symbol = args[1].upper()
    timeframe = args[2].lower()

    # Отправляем "ждуна"
    wait_message = await message.answer(f"Анализирую {symbol} на таймфрейме {timeframe}... ⏳")

    # 1. Получаем данные
    ohlcv_df = await data_fetcher.get_ohlcv(symbol, timeframe)
    if ohlcv_df is None or ohlcv_df.empty:
        await wait_message.edit_text(f"Не удалось получить данные для {symbol}. Проверьте символ и попробуйте позже.")
        return

    # 2. Рассчитываем индикаторы
    ta_results = analytics.calculate_indicators(ohlcv_df)
    if not ta_results:
        await wait_message.edit_text("Не удалось рассчитать технические индикаторы.")
        return

    # 3. Генерируем сигнал
    signal_text = await llm_integrator.generate_signal(ta_results, symbol)

    # 4. Отправляем результат
    await wait_message.edit_text(signal_text)
