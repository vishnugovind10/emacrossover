# EMA Crossover
EMA crossover trading strategy in Python

1. We define two exponential moving averages, EMA, one with a longer look-back period of 40 candles and one with a longer of 20 candles
2. Fetch a current snapshot of our portfolio, on which the bot is trading, including information on the current balance of our quoted asset, USDT. The latter ensures that we have enough liquidity to open up a possible new position
3. Query for any open position by symbol. By calling this function we receive a boolean value indicating whether an open position for that symbol exists or not
4. Algorithm places a market order going long if the shorter EMA crosses above the longer, for the amount as defined above in buy_value
5. Algorithm closes the open position if the algorithm detects an open position and the shorter crosses below the longer EMA


