import requests
import time
from openai import OpenAI

# Simulation Variables (Virtual Counter)
virtual_usd = 1000.0
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
        api_key="sk-6d7a6ef96c6d4801ab4ad7b03bde28ff",
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

if __name__ == "__main__":
    print(f"Starting DeepSeek Trader simulation for {SYMBOL}...")
    print(f"Initial Balance: {virtual_usd:.2f} USD, {virtual_crypto} {SYMBOL}")

    while True:
        current_price = get_market_price(SYMBOL)

        if current_price is None:
            print("Could not retrieve market price. Waiting for next cycle...")
            time.sleep(900)
            continue

        current_portfolio_value = virtual_usd + (virtual_crypto * current_price)
        print(f"\n--- New Cycle ---")
        print(f"Current {SYMBOL} Price: ${current_price:.2f}")
        print(f"Current Portfolio Value: ${current_portfolio_value:.2f}")

        decision = get_deepseek_decision(current_price, virtual_usd, virtual_crypto, current_portfolio_value)
        print(f"DeepSeek decided: {decision}")

        # Execute Trade
        if decision == "BUY":
            if virtual_usd > 10: # Ensure enough USD to make a meaningful trade
                crypto_to_buy = virtual_usd / current_price
                virtual_crypto += crypto_to_buy
                virtual_usd = 0.0
                print(f"Executed BUY: Converted all USD to {crypto_to_buy:.6f} {SYMBOL}")
            else:
                print("BUY decision ignored: Insufficient USD balance.")
        elif decision == "SELL":
            if virtual_crypto > 0:
                usd_to_sell = virtual_crypto * current_price
                virtual_usd += usd_to_sell
                virtual_crypto = 0.0
                print(f"Executed SELL: Converted all {SYMBOL} to ${usd_to_sell:.2f} USD")
            else:
                print("SELL decision ignored: No crypto to sell.")
        elif decision == "HOLD":
            print("Executed HOLD: No trade made.")

        # Log Status
        final_portfolio_value = virtual_usd + (virtual_crypto * current_price)
        print(f"New Balance: {virtual_usd:.2f} USD, {virtual_crypto:.6f} {SYMBOL}")
        print(f"Final Portfolio Value (this cycle): ${final_portfolio_value:.2f}")

        # Wait for 15 minutes
        print("Waiting for 15 minutes...")
        time.sleep(900)
