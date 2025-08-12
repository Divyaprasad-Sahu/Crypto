import requests
import os

EXCHANGES = {
    'Binance': 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT',
    'Coinbase': 'https://api.coinbase.com/v2/prices/BTC-USD/spot',
    'Kraken': 'https://api.kraken.com/0/public/Ticker?pair=XBTUSD',
    'Gemini': 'https://api.gemini.com/v1/pubticker/btcusd',
    'Bitstamp': 'https://www.bitstamp.net/api/v2/ticker/btcusd/',
    'Bitfinex': 'https://api.bitfinex.com/v1/pubticker/btcusd',
}

def get_price(exchange, url):
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        d = r.json()
        if exchange == 'Binance':
            return float(d['price'])
        elif exchange == 'Coinbase':
            return float(d['data']['amount'])
        elif exchange == 'Kraken':
            return float(d['result']['XXBTZUSD']['c'][0])
        elif exchange == 'Gemini':
            return float(d['last'])
        elif exchange == 'Bitstamp':
            return float(d['last'])
        elif exchange == 'Bitfinex':
            return float(d['last_price'])
    except Exception:
        return None

def notify_discord(profit, buy_ex, buy_price, sell_ex, sell_price):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("Discord webhook URL not found in environment variables.")
        return

    message = {
        "content": f"🚨 Arbitrage Alert! 🚨\nProfit: **${profit:.2f}**\nBuy at {buy_ex} @ ${buy_price:.2f}\nSell at {sell_ex} @ ${sell_price:.2f}"
    }

    try:
        requests.post(webhook_url, json=message, timeout=5)
        print("Notification sent to Discord.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Discord notification: {e}")

def run_arbitrage_check():
    prices = {ex: get_price(ex, url) for ex, url in EXCHANGES.items()}
    good_prices = {k: v for k, v in prices.items() if v is not None}
    
    if len(good_prices) < 2:
        print("Not enough prices available to check for arbitrage.")
        return

    buy_ex = min(good_prices, key=good_prices.get)
    sell_ex = max(good_prices, key=good_prices.get)
    buy_price = good_prices[buy_ex]
    sell_price = good_prices[sell_ex]
    profit = sell_price - buy_price
    
    if profit > 200:
        notify_discord(profit, buy_ex, buy_price, sell_ex, sell_price)
    else:
        print(f"Current profit is ${profit:.2f}, not meeting the $200 threshold.")

if __name__ == '__main__':
    run_arbitrage_check()