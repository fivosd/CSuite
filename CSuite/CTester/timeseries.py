import pandas as pd
import CSuite.CSuite.BConnector as connector
import numpy as np
import scipy.stats as stats


class TimeSeries:
    data = None
    client = None
    col = 'close'
    symbol = ''
    interval = ''

    def __init__(self, client, data=None):
        self.client = client
        self.data = data

    # passes data onto the timeSeries using the get_SpotKlines() function
    def download(self, symbol, interval):
        self.symbol = symbol
        self.interval = interval
        self.data = connector.get_SpotKlines(self.client, symbol, interval)
        return self

    # changes the col object used as the primary Timeseries from the OCHL frame
    def slice(self, col='close'):
        self.col = col
        return self

    # returns a summary statistic pandas data frame
    def summarize(self, period=365):
        timeSeries = self.data[self.col]
        timeSeries = timeSeries[-period:].pct_change()
        downside = timeSeries[timeSeries.values < 0]
        sortino = ((timeSeries.mean()) * 365 - 0.01)/(downside.std()*np.sqrt(365))
        daily_draw_down = (timeSeries/timeSeries.rolling(center=False, min_periods=1, window=365).max())-1.0
        max_daily_draw_down = daily_draw_down.rolling(center=False, min_periods=1, window=365).min().min().round(4)
        calmar = round((timeSeries.mean()*365)/abs(max_daily_draw_down.min())*100, 4)

        returnP = round(timeSeries[-365:].sum(), 4)
        stdP = round(timeSeries[-365:].std()*np.sqrt(365), 4)
        sharpeP = round(returnP/stdP, 4)

        skew = self.data[self.col].pct_change().skew()
        kurt = self.data[self.col].pct_change().kurtosis()

        frame = pd.DataFrame(columns = ['Return', 'Vollatility', 'Sharpe', 'Sortino', 'MaxDrawDown', 'Calmar', 'Skew', 'Kurtosis'])
        frame.loc[0] = [round(returnP, 4)*100, round(stdP, 4)*100, round(sharpeP, 3), round(sortino, 3), round(max_daily_draw_down, 3), round(calmar, 3), round(skew, 3), round(kurt, 3)]

        return frame

    # returns the annualised returns estimation using Linear Regression of Logarithmic Returns
    def lin_reg(self, period=365):
        timeSeries = self.data[self.col]
        timeSeries = timeSeries[-period:].pct_change().dropna()
        returns = (timeSeries.cumsum()*100)+100
        log_ts = np.log(returns)
        x = np.arange(len(log_ts))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, log_ts)
        annualized_slope = ((np.power(np.exp(slope), 365) - 1) * 100) * (r_value ** 2)

        return round(annualized_slope, 3)

    # returns a Pandas DataFrame with the average performed return by Month
    def seasonality(self):

        monthly = self.data.resample('BM')
        monthly = (monthly.last().close - monthly.first().open)/monthly.first().open

        monthly = monthly*100
        frame = pd.DataFrame(data=list(zip(monthly.index, monthly.values)), columns=['timestamp', 'returns'])
        frame = frame.dropna()
        frame['positive'] = frame['returns'] > 0
        table = frame
        table['Month'] = [table.timestamp[i].month for i in range(0, len(table))]

        seasonality = []
        for i in range(1, 13):
            seasonality.append(table[table['Month'] == i].returns.mean())
        frame = pd.DataFrame()
        frame['seasonality'] = seasonality
        frame['positive'] = frame['seasonality'] > 0
        frame['months'] = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        return frame

    # returns plot of autocorrelation for specified lags
    def autocorrelation(self, period=365, lags=50, diff=False):
        from statsmodels.tsa.stattools import acf
        if diff:
            return acf(self.data[self.col][-period:].diff().dropna(), nlags=lags)
        else:
            return acf(self.data[self.col][-period:], nlags=lags)

    # returns a Pandas DataFrame with the results of the AD-Fuller test
    def adfuller(self, maxlag=5, mode='N', regression='c'):
        from statsmodels.tsa.stattools import adfuller
        if mode == 'N':
            adf = adfuller(self.data['close'], maxlag=maxlag, regression=regression)
        elif mode == 'L':
            adf = adfuller(np.log(self.data['close']), maxlag=maxlag, regression=regression)
        df = pd.DataFrame(columns=['adf', 'p-value', 'lags', 'NObs', 'cv_1%', 'cv_5%', 'cv_10%', 'ic'])
        ks = list(adf[0:4]) + list(adf[4].values()) + [adf[5]]
        df.loc[0] = ks

        return df
