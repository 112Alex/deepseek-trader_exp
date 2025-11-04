import ccxt.async_support as ccxt
import pandas as pd

async def get_ohlcv(symbol: str, timeframe: str, limit: int = 100) -> pd.DataFrame | None:
    """
    Асинхронно получает исторические данные OHLCV с Binance.

    :param symbol: Торговая пара (например, 'BTC/USDT').
    :param timeframe: Таймфрейм (например, '1h', '4h', '1d').
    :param limit: Количество свечей для загрузки.
    :return: DataFrame с данными OHLCV или None в случае ошибки.
    """
    exchange = ccxt.binance()
    try:
        # Загружаем данные OHLCV
        ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        if not ohlcv:
            return None

        # Преобразуем в pandas DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        # Преобразуем timestamp в читаемую дату
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df

    except ccxt.NetworkError as e:
        print(f"Сетевая ошибка при запросе к Binance: {e}")
        return None
    except ccxt.ExchangeError as e:
        print(f"Ошибка биржи при запросе {symbol}: {e}")
        return None
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
        return None
    finally:
        # Всегда закрываем соединение
        await exchange.close()
