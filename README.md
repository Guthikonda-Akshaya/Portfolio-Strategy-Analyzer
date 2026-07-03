# Portfolio Rebalancing Analysis

A finance project built with **Python** and **Streamlit** to compare three portfolio rebalancing strategies using historical stock and ETF price data from **Yahoo Finance**.

The project demonstrates core portfolio management concepts, portfolio performance evaluation, and financial data visualization through an interactive web application.

---

## Project Overview

The application allows users to create a custom investment portfolio by selecting stock or ETF tickers, assigning target weights, and choosing a historical time period. It then simulates the portfolio under three different rebalancing strategies and compares their performance using standard financial metrics and interactive visualizations.

---

## Features

- Create custom portfolios using stock and ETF tickers
- Validate portfolio weights before simulation
- Download historical market data using **Yahoo Finance**
- Handle invalid or unavailable ticker symbols gracefully
- Compare three portfolio rebalancing strategies:
  - **Buy & Hold** – Invest once and never rebalance
  - **Calendar Rebalancing** – Rebalance monthly, quarterly, or yearly
  - **Threshold Rebalancing** – Rebalance when an asset's weight exceeds a specified drift threshold
- Evaluate portfolio performance using:
  - Final Portfolio Value
  - Total Return
  - Annualized Return
  - Annualized Volatility
  - Sharpe Ratio
  - Maximum Drawdown
- Interactive visualizations for:
  - Portfolio Value Over Time
  - Risk vs Return Comparison
  - Portfolio Allocation Over Time

---

## Technologies

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- yfinance

---

## Live Demo

 **[Launch Portfolio Rebalancing Analysis](https://portfolio-rebalancing-analysis.streamlit.app/)**

---

## Using the Application

1. Enter stock or ETF tickers (comma separated).
2. Enter the corresponding portfolio weights (must sum to 100%).
3. Select the analysis period.
4. Choose the calendar rebalancing frequency.
5. Select the threshold percentage for threshold rebalancing.
6. Click **Simulate** to compare all three strategies.

---

## Project Structure

```text
.
├── app.py
├── requirements.txt
└── README.md
```

---

## Assumptions

- Transaction costs and taxes are not considered.
- The risk-free rate is assumed to be **0%** while computing the Sharpe Ratio.
- Rebalancing is assumed to occur instantly at the closing price.
- Historical prices are obtained from Yahoo Finance.

---

## Future Improvements

- Include transaction costs during rebalancing
- Allow a user-defined risk-free rate
- Compare multiple calendar rebalancing frequencies simultaneously
- Add benchmark comparison (e.g., S&P 500)
- Export portfolio performance reports

---

## Acknowledgements

- Historical market data provided by **Yahoo Finance**
- Built using **Streamlit**, **Plotly**, and the **Python** data science ecosystem.
