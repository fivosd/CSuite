# CSuite
*CSuite is a Python library enabling easy integration with Binance API for crypto market data analysis, trade execution and portfolio managment.*
---
**Currently Available: Connector Module**

This release of CTrader includes the connector module. This module - wrapped in *csuite.py* - deals with instance creation, static data retrival and light data processing.
More features will be added to the CSuite over time; Backtesting capabilities are in the pipeline as well as simple trade execution. 

This library uses the Binance client library but simplifies data retrival & connection into 1 line commands. The objective of the connector, and library as a whole is to enable easy access to complex secondary features in a library with built-in connection to Binance.

## Available Functions

#### connect_client(filename)
The connect client function takes a formated JSON file as input and returns a Binance client object. This returned object is necessary input in most following functions.

### Spot
#### get_SpotKlines(client,symbol,interval)
Requires client (above), symbol in Binance ('BTCUSDT') pair format and, interval ('1m','5m','30m'...'3d'). Returns pandas DataFrame Timeseries. 

#### batch_historic(client, symbols, interval, mode)
This function downloads historic data for multiple pairs at the same time, it works exactly the same as *get_SpotKlines* but requires mode field and symbols to be an *array* **NOT** *string*. The mode changes the return format.
##### Modes available:
1. Nominal ('N'): Returns timeseries of nominal prices
2. Return ('R'): Returns timeseries of *pct_change()* of prices
3. Volatility ('V'): Returns timeseries of rolling 7-day standard deviation of returns

### Futures
#### get_FuturesKlines(client, symbol, interval)
First of the futures functions, works like *get_SpotKlines(client,symbol,interval)* but returns Binance futures prices.

#### get_FuturesSpread(client, symbol, interval):
This function returns the Spread between the futures and spot in % terms (already multiplied) for the last 100 data-points.

#### get_FuturesOI(client, symbol, interval):
This function returns the futures Open Interest for the last 100 data-points of the specified interval. 

#### get_LiveSpread(client, symbol)
Returns current spot-futures sprad of pair in % terms, due to API limitations futures price is 5m average; please do not use this to trade in real-time.

#### get_FuturesLS(client, symbol, period)
Returns futures long-short ratio of pair in DataFrame format with 3 columns (Long (%), SHort (%), Long/Short Ratio).

#### get_FuturesFundingRate(client, ticker, period)
Returns futures funding rate (max 8h interval) as DataFrame.

### Options
#### get_options_skew(client, maturity, strikes)
This function downloads BTC Vanillia Option data from Binance API. Requires single maturity and strike in String format. Returns DataFrame with Columns: *'strike', 'direction', 'bidIV', 'askIV', 'delta', 'gamma', 'theta', 'vega'*.

**Binance Maturity Format**: YYMMDD -> e.g. 24/12/21 = 211224


#### get_omm_skew(client, maturities, strikes):
This function downloads BTC Vanillia Option data from Binance API. Requires multiple maturities and strikes in Array format. This function enables batch Options data download, all strikes for a maturity must be present.
Returns DataFrame with Columns: *'strike', 'direction', 'bidIV', 'askIV', 'delta', 'gamma', 'theta', 'vega'*.

**Example Call:**
`multi_expiry_skew = csuite.get_omm_skew(client,['211224','211231','220128'],[['35000','40000','42000','44000','46000','48000','50000','52000','54000','56000','58000','60000','65000','70000'],['32000','36000','40000','44000','48000','52000','56000','60000','65000','75000','80000'],['30000','35000','40000','45000','50000','55000','60000','65000','70000','80000']])`

#### IV_skew(data, price)
This function transforms the output of *get_omm_skew* (data/table format) into a symetric put-call Implied volatility array. It returns an array with the IV of Puts under the price and IV of Calls over the price. As price, pass current price. 
