import pandas as pd
import pandas_ta as ta

def calculate_indicators(df: pd.DataFrame) -> dict:
    """
    Рассчитывает технические индикаторы (RSI, MACD) для DataFrame.

    :param df: DataFrame с данными OHLCV.
    :return: Словарь с последними значениями индикаторов.
    """
    if df is None or df.empty:
        return {}
    
    # Проверяем, что данных достаточно для расчета индикаторов
    # RSI требует минимум 14 свечей, MACD требует минимум 26 свечей
    if len(df) < 26:
        return {}

    try:
        # Расчет RSI
        df.ta.rsi(append=True)

        # Расчет MACD
        df.ta.macd(append=True)

        # Проверяем наличие необходимых колонок
        if 'RSI_14' not in df.columns or 'MACD_12_26_9' not in df.columns:
            return {}

        # Получаем последние значения
        latest_rsi = df['RSI_14'].iloc[-1]
        latest_macd = df['MACD_12_26_9'].iloc[-1]
        latest_macdh = df['MACDh_12_26_9'].iloc[-1] # Гистограмма
        latest_macds = df['MACDs_12_26_9'].iloc[-1] # Сигнальная линия

        # Определяем пересечение MACD
        macd_cross = 'neutral'
        # Проверяем, что есть минимум 2 значения для сравнения
        if len(df) >= 2:
            # Если гистограмма сменила знак с минуса на плюс (бычий сигнал)
            if latest_macdh > 0 and df['MACDh_12_26_9'].iloc[-2] < 0:
                macd_cross = 'bullish'
            # Если гистограмма сменила знак с плюса на минус (медвежий сигнал)
            elif latest_macdh < 0 and df['MACDh_12_26_9'].iloc[-2] > 0:
                macd_cross = 'bearish'

        return {
            'rsi': round(latest_rsi, 2),
            'macd': round(latest_macd, 2),
            'macd_histogram': round(latest_macdh, 2),
            'macd_signal': round(latest_macds, 2),
            'macd_cross': macd_cross
        }
    except Exception as e:
        print(f"Ошибка при расчете индикаторов: {e}")
        return {}
