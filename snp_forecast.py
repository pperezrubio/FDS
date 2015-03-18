# -*- coding: utf-8 -*-
"""
Created on Tue Nov 04 17:33:48 2014

@author: dbi
"""

# snp_forecast.py

import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn

from FactSetOnDemand import  Factlet
from sklearn.qda import QDA

from backtest import Strategy, Portfolio
from forecast import create_lagged_series

class SNPForecastingStrategy(Strategy):
    """    
    Requires:
    symbol - A stock symbol on which to form a strategy on.
    bars - A DataFrame of bars for the above symbol."""

    def __init__(self, symbol, bars):
        self.symbol = symbol
        self.bars = bars
        self.create_periods()
        self.fit_model()

    def create_periods(self):
        """Create training/test periods."""
        self.start_train = datetime.datetime(2001,1,10)
        self.start_test = datetime.datetime(2013,1,1)
        self.end_period = datetime.datetime(2013,12,31)

    def fit_model(self):
        """Fits a Quadratic Discriminant Analyser to the
        US stock ."""
        # Create a lagged series of the S&P500 US stock market index
        snpret = create_lagged_series(self.symbol, self.start_train, 
                                      self.end_period, lags=5) 

        # Use the prior two days of returns as 
        # predictor values, with direction as the response
        X = snpret[["Lag1","Lag2"]]
        y = snpret["Direction"]

        # Create training and test sets
        X_train = X[X.index < self.start_test]
        y_train = y[y.index < self.start_test]

        # Create the predicting factors for use 
        # in direction forecasting
        self.predictors = X[X.index >= self.start_test]

        # Create the Quadratic Discriminant Analysis model
        # and the forecasting strategy
        self.model = QDA()
        self.model.fit(X_train, y_train)

    def generate_signals(self):
        """Returns the DataFrame of symbols containing the signals
        to go long, short or hold (1, -1 or 0)."""
        signals = pd.DataFrame(index=self.bars.index)
        signals['signal'] = 0.0       

        # Predict the subsequent period with the QDA model
        signals['signal'] = self.model.predict(self.predictors)

        # Remove the first five signal entries to eliminate
        # NaN issues with the signals DataFrame
        signals['signal'][0:5] = 0.0
        signals['positions'] = signals['signal'].diff() 

        return signals
        

class MarketIntradayPortfolio(Portfolio):
    """Buys or sells 500 shares of an asset at the opening price of
    every bar, depending upon the direction of the forecast, closing 
    out the trade at the close of the bar.

    Requires:
    symbol - A stock symbol which forms the basis of the portfolio.
    bars - A DataFrame of bars for a symbol set.
    signals - A pandas DataFrame of signals (1, 0, -1) for each symbol.
    initial_capital - The amount in cash at the start of the portfolio."""

    def __init__(self, symbol, bars, signals, initial_capital=100000.0):
        self.symbol = symbol        
        self.bars = bars
        self.signals = signals
        self.initial_capital = float(initial_capital)
        self.positions = self.generate_positions()
        
    def generate_positions(self):
        """Generate the positions DataFrame, based on the signals
        provided by the 'signals' DataFrame."""
        positions = pd.DataFrame(index=self.signals.index).fillna(0.0)

        # Long or short 500 shares of SPY based on 
        # directional signal every day
        positions[self.symbol] = 500*self.signals['signal']
        return positions
                    
    def backtest_portfolio(self):
        """Backtest the portfolio and return a DataFrame containing
        the equity curve and the percentage returns."""

        # Set the portfolio object to have the same time period
        # as the positions DataFrame
        portfolio = pd.DataFrame(index=self.positions.index)
        pos_diff = self.positions.diff()

        # Work out the intraday profit of the difference
        # in open and closing prices and then determine
        # the daily profit by longing if an up day is predicted
        # and shorting if a down day is predicted        
        portfolio['price_diff'] = self.bars['Close']-self.bars['Open']
        portfolio['price_diff'][0:5] = 0.0
        portfolio['profit'] = self.positions[self.symbol] * portfolio['price_diff']

        # Generate the equity curve and percentage returns
        portfolio['total'] = self.initial_capital + portfolio['profit'].cumsum()
        portfolio['returns'] = portfolio['total'].pct_change()
        return portfolio
        

if __name__ == "__main__":
    start_test = datetime.datetime(2013,1,1)
    end_period = datetime.datetime(2013,12,31)

    # Obtain the bars for FDS    
    
    factlet = Factlet.ExtractFormulaHistory("AAPL","p_price_open,p_price_high,p_price_low,p_price,p_volume_frq",["dates",start_test.strftime("%m/%d/%Y") + ":" + end_period.strftime("%m/%d/%Y")+":D"])

    raw = []
    for r in xrange(factlet.getNumberOfRows()):
        date = factlet.getValueAsString(1, r)
        op = factlet.getValueAsDouble(2, r)
        high = factlet.getValueAsDouble(3, r)
        low = factlet.getValueAsDouble(4, r)
        close = factlet.getValueAsDouble(5, r)
        vol = factlet.getValueAsDouble(6, r)
        raw.append((date, op,high,low,close,vol))	# store

    data = pd.DataFrame(raw, columns=['Date','Open','High','Low','Close','Volume'])
    data.Date = pd.tseries.tools.to_datetime(data.Date)
    data = data.set_index('Date')
    bars = data[data.index >= start_test]

    
    # Create the forecasting strategy
    snpf = SNPForecastingStrategy("AAPL", bars)
    signals = snpf.generate_signals()

    # Create the portfolio based on the forecaster
    portfolio = MarketIntradayPortfolio("AAPL", bars, signals,              
                                        initial_capital=100000.0)
    returns = portfolio.backtest_portfolio()

    # Plot results
    fig = plt.figure()
    fig.patch.set_facecolor('white')

    # Plot the price of the comparable
    ax1 = fig.add_subplot(211,  ylabel='FDS price in $')
    bars['Close'].plot(ax=ax1, color='r', lw=2.)

    # Plot the equity curve
    ax2 = fig.add_subplot(212, ylabel='Portfolio value in $')
    returns['total'].plot(ax=ax2, lw=2.)

    fig.show()
    