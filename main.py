import asyncio
import logging
import os
from dotenv import load_dotenv
import requests
import time
from openai import OpenAI

from aiogram import Bot
from aiogram import Dispatcher
from aiogram import F, types
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Simulation Variables (Virtual Counter)
virtual_usd = 0.0
virtual_crypto = 0.0
SYMBOL = 'BTCUSDT'

def get_market_price(symbol):
    try:
        response = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}")
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        return float(data['price'])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching market price: {e}")
        return None

def get_deepseek_decision(price, usd_balance, crypto_balance, portfolio_value):
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com/v1"
    )

    system_prompt = "You are an expert crypto trading analyst. Your goal is to maximize portfolio value. Based on the data, respond with ONLY ONE WORD: BUY, SELL, or HOLD."
    user_prompt = f"Current {SYMBOL} price is ${price}. My current portfolio: ${usd_balance:.2f} USD and {crypto_balance} {SYMBOL}. Total portfolio value is ${portfolio_value:.2f}. What is my next move?"

    try:
        response = client.chat.completions.create(
            model="deepseek-chat", # Assuming deepseek-chat is the model name based on common LLM API usage
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=5
        )
        decision = response.choices[0].message.content.strip().upper()
        if decision in ["BUY", "SELL", "HOLD"]:
            return decision
        else:
            print(f"DeepSeek returned an unexpected decision: {decision}")
            return "HOLD" # Default to HOLD on unexpected response
    except Exception as e:
        print(f"Error getting DeepSeek decision: {e}")
        return "HOLD" # Default to HOLD on error

@dp.message(CommandStart())
async def handle_start(msg: types.Message):
    await msg.answer(text='Привет! Я бот-симулятор торговли криптовалютой. Укажите начальный баланс в USD, на который будет торговать LLM в течение 1 минуты.')

@dp.message()
async def handle_balance_input(msg: types.Message):
    try:
        initial_usd_balance = float(msg.text)
        if initial_usd_balance <= 0:
            await msg.answer("Пожалуйста, введите положительное число для начального баланса.")
            return

        await msg.answer(f"Начинаем симуляцию с балансом ${initial_usd_balance:.2f} USD на 1 минуту. Пожалуйста, подождите...")

        virtual_usd = initial_usd_balance
        virtual_crypto = 0.0
        start_time = time.time()
        
        simulation_log = []

        while time.time() - start_time < 60: # Симуляция на 1 минуту
            current_price = get_market_price(SYMBOL)

            if current_price is None:
                simulation_log.append("Не удалось получить рыночную цену. Пропускаем цикл...")
                await asyncio.sleep(5) # Ждем 5 секунд перед следующей попыткой
                continue

            current_portfolio_value = virtual_usd + (virtual_crypto * current_price)
            
            decision = get_deepseek_decision(current_price, virtual_usd, virtual_crypto, current_portfolio_value)
            
            log_entry = f"Цена {SYMBOL}: ${current_price:.2f}, Портфель: ${current_portfolio_value:.2f}, Решение DeepSeek: {decision}"
            simulation_log.append(log_entry)

            # Execute Trade
            if decision == "BUY":
                if virtual_usd > 10: # Ensure enough USD to make a meaningful trade
                    crypto_to_buy = virtual_usd / current_price
                    virtual_crypto += crypto_to_buy
                    virtual_usd = 0.0
                    simulation_log.append(f"Выполнена ПОКУПКА: Конвертировано все USD в {crypto_to_buy:.6f} {SYMBOL}")
                else:
                    simulation_log.append("ПОКУПКА проигнорирована: Недостаточный баланс USD.")
            elif decision == "SELL":
                if virtual_crypto > 0:
                    usd_to_sell = virtual_crypto * current_price
                    virtual_usd += usd_to_sell
                    virtual_crypto = 0.0
                    simulation_log.append(f"Выполнена ПРОДАЖА: Конвертировано все {SYMBOL} в ${usd_to_sell:.2f} USD")
                else:
                    simulation_log.append("ПРОДАЖА проигнорирована: Нет криптовалюты для продажи.")
            elif decision == "HOLD":
                simulation_log.append("Выполнено УДЕРЖАНИЕ: Сделка не совершена.")
            
            await asyncio.sleep(5) # Ждем 5 секунд между циклами в течение 1 минуты

        final_portfolio_value = virtual_usd + (virtual_crypto * current_price)
        
        result_message = "--- Результаты симуляции ---\n"
        result_message += "\n".join(simulation_log)
        result_message += f"\nНачальный баланс: ${initial_usd_balance:.2f} USD\n"
        result_message += f"Конечный баланс: {virtual_usd:.2f} USD, {virtual_crypto:.6f} {SYMBOL}\n"
        result_message += f"Итоговая стоимость портфеля: ${final_portfolio_value:.2f}"
        
        await msg.answer(text=result_message)

    except ValueError:
        await msg.answer("Пожалуйста, введите корректное число для начального баланса.")
    except Exception as e:
        await msg.answer(f"Произошла ошибка: {e}")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot, allowed_updates=['message, edited_message'])

if __name__ == '__main__':
    asyncio.run(main())