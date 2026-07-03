# Portfolio Rebalancing Analysis

A student finance project built with Streamlit that compares three
portfolio rebalancing strategies using real historical stock/ETF price
data from Yahoo Finance.

This project was built as an academic exercise to demonstrate portfolio
management concepts, basic financial analytics, and Python programming.
It is intentionally kept simple rather than production-grade, so that
every function can be explained line-by-line.

## Project Overview

Given a set of tickers, target weights, and a date range, the app
simulates how a portfolio would have performed under three different
rebalancing approaches, then compares them side by side using
performance metrics and charts.

## Features

- Enter any combination of stock/ETF tickers and target weights
- Automatic validation that weights sum to 100%
- Historical adjusted closing price download via `yfinance`
- Graceful handling of invalid or delisted tickers
- Three rebalancing strategies:
  - **Buy & Hold** — invest once, never rebalance
  - **Calendar Rebalancing** — rebalance monthly, quarterly, or yearly
  - **Threshold Rebalancing** — rebalance whenever any asset drifts
    beyond a chosen percentage from its target weight
- Six performance metrics per strategy:
  - Final Portfolio Value
  - Total Return
  - Annualized Return
  - Annualized Volatility
  - Sharpe Ratio (risk-free rate assumed to be 0)
  - Maximum Drawdown
- Three Plotly visualizations:
  - Portfolio Value Over Time (all strategies)
  - Risk vs Return Comparison (scatter plot)
  - Portfolio Allocation Over Time (stacked area chart, for a chosen strategy)

## Technologies

- Python 3
- Streamlit — user interface
- Pandas — data handling and time series calculations
- NumPy — numerical calculations
- Plotly — interactive charts
- yfinance — historical stock price data

## Live Demo

 **[Launch Portfolio Strategy Analyzer](https://portfolio-rebalancing-analysis.streamlit.app/)**

### Using the App

1. In the sidebar, enter comma-separated tickers (e.g. `AAPL, MSFT, GOOGL`).
2. Enter comma-separated weights that sum to 100 (e.g. `40, 30, 30`).
3. Choose a start date, end date, and initial investment amount.
4. Choose a calendar rebalancing frequency and a threshold percentage.
5. Click **Simulate** to download data, run all three strategies, and
   view the metrics table and charts.

## Project Structure

```
portfolio_sim/
├── app.py        # Main Streamlit application (all logic in one file)
└── README.md      # Project documentation
```

## Limitations / Assumptions

- Transaction costs and taxes are not modeled.
- The risk-free rate is assumed to be 0% for the Sharpe Ratio.
- Rebalancing is assumed to happen instantly at the closing price with
  no slippage.
- Dividends are only included to the extent that `yfinance`'s adjusted
  close price reflects them.

## Future Improvements

- Add transaction cost assumptions to rebalancing strategies
- Allow a custom, user-defined risk-free rate for the Sharpe Ratio
- Add the ability to compare more than one calendar frequency at once
- Add a benchmark comparison (e.g. S&P 500)
- Allow saving/exporting simulation results
