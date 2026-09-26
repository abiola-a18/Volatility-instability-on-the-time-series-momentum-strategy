import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import plotly.express as px

def Time_Series_Momentum_Signal_Table_unscaled(tickers,*, start_date, end_date):
    raw_data = yf.download(
    tickers = tickers,
    # Please be advised the start and end date are "yyyy-mm-dd"
    start = start_date, # From what point do we want to start getting stock date
    end = end_date, # From what point do we want to stop getting stock data
    interval = "1d", # The sample rate of the data one stock data every day
    ignore_tz=True,
    auto_adjust=True, # Adjust all fields by splits and dividends)
    )
    #picking only close prices
    raw_data = raw_data['Close']
    #re-naming columns
    data = raw_data[[tickers]].copy()
    data.columns = ['close']

    data['daily_return'] = data['close'].pct_change().fillna(0)
    data['momentum_signal_unsigned'] = ((1 + data['daily_return']).rolling(window=12).apply(np.prod, raw=True).shift(2).fillna(0)-1)
    data.loc[data.index[:13], 'momentum_signal_unsigned'] = 0

    conditions = [
    data['momentum_signal_unsigned'] > 0,
    data['momentum_signal_unsigned'] < 0
    ]
    choices = [
    data['daily_return'],
    -data['daily_return']
    ]

    data['momentum_signal'] = np.sign(data['momentum_signal_unsigned'])
    return data

def Time_Series_Momentum_Prior_Strategies(tickers,*, start_date, end_date):
   """Prior strategy created"""
   import numpy as np
   import pandas as pd
   import matplotlib.pyplot as plt
   import yfinance as yf
   import plotly.express as px
   data = Time_Series_Momentum_Signal_Table_unscaled(tickers, start_date=start_date, end_date=end_date)
   conditions = [
      data['momentum_signal'] > 0,
      data['momentum_signal'] < 0]
   choices = [
      data['daily_return'],
      -data['daily_return']
      ]
   data.loc[:, 'unscaled_profits'] = np.select(conditions, choices, default=0)
   data['cumulative_unscaled_profits'] = data['unscaled_profits'].cumsum()
   plt.figure(figsize=(14, 7))
   plt.plot(data.index, data['cumulative_unscaled_profits'], label='Cumulative Unscaled Profits', color='green')
   plt.title('Cumulative Unscaled Profits Over Time')
   plt.xlabel('Date')
   plt.ylabel('Cumulative Unscaled Profits')
   plt.grid(True)
   plt.legend()
   plt.show()
   return plt.plot(data.index, data['cumulative_unscaled_profits'], label='Cumulative Unscaled Profits', color='green')

def Time_Series_Momentum_Volatility_strategies(tickers,*, start_date, end_date):
   data = Time_Series_Momentum_Prior_Strategies(tickers, start_date, end_date)
   data['abs_daily_return'] = data['daily_return'].abs()
   #Initialize the EWMA column
   data['EWMA'] = 0.0
   
   # Set the first EWMA value to the first absolute daily return
   data.loc[data.index[0], 'EWMA'] = data['abs_daily_return'].iloc[0]
   
   # Calculate EWMA for subsequent days
   nu = 0.2
   for i in range(1, len(data)):
      data.loc[data.index[i], 'EWMA'] = np.sqrt((1 - nu) * (data['EWMA'].iloc[i-1])**2 + nu * (data['abs_daily_return'].iloc[i])**2)
    
    monthly_target_volatility = 0.2/np.sqrt(12)
   data['w_t'] = monthly_target_volatility / data['EWMA']
   conditions = [
      data['momentum_signal'] > 0,
      data['momentum_signal'] < 0
      ]
   choices = [
      data['daily_return']* data['w_t'],
      -data['daily_return'] *data['w_t']
      ]
   data.loc[:, 'scaled_profits'] = np.select(conditions, choices, default=0)
   data['cumulative_scaled_profits'] = data['scaled_profits'].cumsum().fillna(0)
   plt.figure(figsize=(14, 7))
   plt.plot(data.index, data['cumulative_scaled_profits'], label='Cumulative Scaled Profits', color='blue')
   plt.title('Cumulative Scaled Profits Over Time')
   plt.xlabel('Date')
   plt.ylabel('Cumulative Scaled Profits')
   plt.grid(True)
   plt.legend()
   return plt.plot(data.index, data['cumulative_scaled_profits'], label='Cumulative Scaled Profits', color='blue')

def Sharpe_Ratio_Comparison(data1, data2, tickers, start_date=start_date, end_date=end_date):
   """Calcluating and Comparing the sharpe ratio of the different strategies"""
   
   data1 = Time_Series_Momentum_Signal_Table_unscaled(tickers, start_date=start_date, end_date=end_date)
   conditions = [
      data1['momentum_signal'] > 0,
      data1['momentum_signal'] < 0]
    choices = [
       data1['daily_return'],
       -data1['daily_return']
       ]
   data1.loc[:, 'unscaled_profits'] = np.select(conditions, choices, default=0)
   data1['cumulative_unscaled_profits'] = data['unscaled_profits'].cumsum()

   data2 = = Time_Series_Momentum_Prior_Strategies(tickers, start_date, end_date)
   data2['abs_daily_return'] = data2['daily_return'].abs()
   #Initialize the EWMA column
   data2['EWMA'] = 0.0
   # Set the first EWMA value to the first absolute daily return
   data2.loc[data.index[0], 'EWMA'] = data2['abs_daily_return'].iloc[0]
    # Calculate EWMA for subsequent days
    # nu = 0.2
    for i in range(1, len(data)):
      data2.loc[data.index[i], 'EWMA'] = np.sqrt((1 - nu) * (data2['EWMA'].iloc[i-1])**2 + nu * (data2['abs_daily_return'].iloc[i])**2)
      monthly_target_volatility = 0.2/np.sqrt(12)
      data2['w_t'] = monthly_target_volatility / data['EWMA']
      conditions = [
         data2['momentum_signal'] > 0,
         data2['momentum_signal'] < 0
         ]
      choices = [
         data2['daily_return']* data2['w_t'],
         -data2['daily_return'] *data2['w_t']
         ]
      data2.loc[:, 'scaled_profits'] = np.select(conditions, choices, default=0)
      data2['cumulative_scaled_profits'] = data['scaled_profits'].cumsum().fillna(0)
      #Risk free rate at this current moment
      risk_free_rate = 0.536

      Sharpe_prior = (data1.loc['Date' == "2024-12-31", columns = "cumulative_unscaled_profits"] - risk_free_rate) / data1.std(axis = 'unscaled_profits')
      Sharpe_post = (data2.loc['Date' == "2024-12-31", columns = "cumulative_unscaled_profits"] - risk_free_rate) / data2.std(axis = 'unscaled_profits')