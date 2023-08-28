import ccxt
import numpy as np
import pandas as pd
import time

# Binance API credentials
api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_API_SECRET'

# Initialize the Binance API
binance = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
})

# Trading parameters
symbol = 'BTC/USDT'
short_ema_period = 20
long_ema_period = 50
vwap_period = 20
buy_amount = 0.01  # Adjust as needed
stop_loss_percent = 2  # Adjust as needed
take_profit_percent = 3  # Adjust as needed
trailing_stop_percent = 1  # Adjust as needed

# Calculate Exponential Moving Average (EMA)
def calculate_ema(data, period):
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()
    ema = np.convolve(data, weights, mode='full')[:len(data)]
    return ema

while True:
    try:
        # Fetch candlestick data
        timeframe = '15m'  # Change to 15 minutes
        candles = binance.fetch_ohlcv(symbol, timeframe=timeframe, limit=long_ema_period)
        df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        close_prices = df['close'].values
        
        # Calculate indicators
        short_ema = calculate_ema(close_prices, short_ema_period)
        long_ema = calculate_ema(close_prices, long_ema_period)
        vwap = df['volume'].rolling(window=vwap_period).apply(lambda x: np.dot(x, df['close']) / x.sum(), raw=False)
        
        # Calculate stop loss and take profit levels
        current_price = df['close'].iloc[-1]
        stop_loss_price = current_price * (1 - stop_loss_percent / 100)
        take_profit_price = current_price * (1 + take_profit_percent / 100)
        
        # Check for buy and sell signals
        balance = binance.fetch_balance()
        if short_ema[-1] > long_ema[-1] and df['close'].iloc[-1] < vwap.iloc[-1]:
            if balance['total'][symbol.split('/')[0]] * current_price > buy_amount:
                buy_order = binance.create_market_buy_order(symbol, buy_amount)
                print("Buy order placed:", buy_order)
                stop_loss_order = binance.create_limit_sell_order(symbol, balance['total'][symbol.split('/')[0]], stop_loss_price)
                print("Stop loss order placed:", stop_loss_order)
                take_profit_order = binance.create_limit_sell_order(symbol, balance['total'][symbol.split('/')[0]], take_profit_price)
                print("Take profit order placed:", take_profit_order)
                
        elif short_ema[-1] < long_ema[-1] and df['close'].iloc[-1] > vwap.iloc[-1]:
            for open_order in binance.fetch_open_orders(symbol):
                if open_order['side'] == 'sell':
                    binance.cancel_order(open_order['id'])
                    print("Cancelled open sell order:", open_order['id'])
            if balance['total'][symbol.split('/')[0]] > 0:
                sell_order = binance.create_market_sell_order(symbol, balance['total'][symbol.split('/')[0]])
                print("Sell order placed:", sell_order)
        
        time.sleep(900)  # Wait for 15 minutes before the next iteration
        
    except Exception as e:
        print("An error occurred:", e)
        time.sleep(60)  # Wait for a minute before retrying
