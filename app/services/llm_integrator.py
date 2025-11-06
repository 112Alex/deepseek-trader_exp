import aiohttp
from app.config import DEEPSEEK_API_KEY

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

async def generate_signal(ta_results: dict, symbol: str) -> str:
    """
    Генерирует торговый сигнал с помощью DeepSeek API на основе данных ТА.

    :param ta_results: Словарь с результатами технического анализа.
    :param symbol: Торговая пара.
    :return: Текстовый торговый сигнал или сообщение об ошибке.
    """
    if not DEEPSEEK_API_KEY:
        return "Ошибка: API ключ для DeepSeek не настроен."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }

    prompt = (
        f"Рынок: {symbol}. "
        f"RSI: {ta_results.get('rsi', 'N/A')}. "
        f"MACD пересечение: {ta_results.get('macd_cross', 'N/A')}. "
        "На основе этих данных, дай краткий и ясный торговый сигнал для трейдера. "
        "Укажи возможное направление сделки (лонг/шорт), ключевые уровни и риски. "
        "Ответ должен быть лаконичным, в пределах 2-3 предложений."
    )

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Ты — опытный крипто-аналитик, дающий торговые сигналы."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 150,
        "temperature": 0.7,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(DEEPSEEK_API_URL, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result['choices'][0]['message']['content'].strip()
                else:
                    # Пытаемся получить JSON с ошибкой
                    try:
                        error_json = await resp.json()
                        error_msg = error_json.get('error', {}).get('message', str(error_json))
                        error_code = error_json.get('error', {}).get('code', 'unknown')
                        
                        # Специальная обработка ошибки недостатка средств
                        if resp.status == 402 or 'Insufficient Balance' in error_msg:
                            return (
                                "⚠️ Ошибка: Недостаточно средств на аккаунте DeepSeek.\n\n"
                                "Пожалуйста, пополните баланс на https://platform.deepseek.com/\n"
                                "После пополнения баланса бот снова сможет генерировать сигналы."
                            )
                        
                        return f"Ошибка API DeepSeek (статус {resp.status}, код: {error_code}): {error_msg}"
                    except:
                        # Если не удалось распарсить JSON, получаем текст
                        error_text = await resp.text()
                        if resp.status == 402 or 'Insufficient Balance' in error_text:
                            return (
                                "⚠️ Ошибка: Недостаточно средств на аккаунте DeepSeek.\n\n"
                                "Пожалуйста, пополните баланс на https://platform.deepseek.com/\n"
                                "После пополнения баланса бот снова сможет генерировать сигналы."
                            )
                        return f"Ошибка API DeepSeek (статус {resp.status}): {error_text}"
    except aiohttp.ClientError as e:
        return f"Ошибка сети при обращении к DeepSeek: {e}"
    except Exception as e:
        return f"Непредвиденная ошибка при генерации сигнала: {e}"
