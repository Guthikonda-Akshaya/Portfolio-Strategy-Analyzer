"""
Portfolio Rebalancing Simulator
--------------------------------
A student finance project that compares three portfolio rebalancing
strategies (Buy & Hold, Calendar Rebalancing, Threshold Rebalancing)
using real historical stock data pulled from Yahoo Finance.

This app is intentionally kept simple and readable so that every line
can be explained. It uses only: Streamlit, Pandas, NumPy, Plotly, yfinance.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from datetime import date


# ---------------------------------------------------------------------------
# DATA HANDLING FUNCTIONS
# ---------------------------------------------------------------------------

def parse_tickers_and_weights(tickers_text, weights_text):
    """Convert the raw sidebar text into a clean list of tickers and a
    NumPy array of weights (as fractions, e.g. 40% -> 0.40)."""
    tickers = [t.strip().upper() for t in tickers_text.split(",") if t.strip() != ""]
    weights_pct = [float(w.strip()) for w in weights_text.split(",") if w.strip() != ""]
    weights = np.array(weights_pct) / 100.0
    return tickers, weights


def validate_inputs(tickers, weights):
    """Check that the number of tickers matches the number of weights and
    that the weights sum to (approximately) 100%. Returns (is_valid, message)."""
    if len(tickers) == 0:
        return False, "Please enter at least one ticker symbol."
    if len(tickers) != len(weights):
        return False, "The number of tickers and weights must match."
    if not np.isclose(weights.sum(), 1.0, atol=0.01):
        return False, f"Weights must sum to 100%. Currently they sum to {weights.sum() * 100:.1f}%."
    return True, "OK"


def download_prices(tickers, start_date, end_date):
    """Download adjusted closing prices for the given tickers using yfinance.
    Tickers that fail to download are silently dropped so the app can still
    run with the remaining valid tickers. Returns a DataFrame of prices
    and a list of tickers that were successfully downloaded."""
    raw_data = yf.download(tickers, start=start_date, end=end_date, progress=False)

    # yfinance returns a MultiIndex column structure when multiple tickers
    # are requested. We only need the "Close" (adjusted by default) prices.
    if isinstance(raw_data.columns, pd.MultiIndex):
        prices = raw_data["Close"]
    else:
        # Only one ticker was requested, so wrap it in a DataFrame.
        prices = raw_data[["Close"]]
        prices.columns = tickers

    # Drop any ticker column that came back completely empty (invalid ticker).
    prices = prices.dropna(axis=1, how="all")
    valid_tickers = list(prices.columns)

    # Drop rows with missing data so all remaining tickers are aligned.
    prices = prices.dropna(axis=0, how="any")

    return prices, valid_tickers


# ---------------------------------------------------------------------------
# REBALANCING STRATEGIES
# Each strategy function simulates how a portfolio grows day by day and
# returns two things:
#   1. portfolio_value : a Series of total portfolio value over time
#   2. weights_over_time : a DataFrame showing each asset's actual weight
#                           on every day (used for the allocation chart)
# ---------------------------------------------------------------------------

def buy_and_hold_strategy(prices, target_weights, initial_investment):
    """Invest once according to target weights and never rebalance again.
    As prices move, the actual weights will naturally drift over time."""
    first_day_prices = prices.iloc[0]

    # Number of shares bought on day 1 for each asset.
    shares = (initial_investment * target_weights) / first_day_prices.values

    # Value of each asset holding on every day = shares * price.
    holdings_value = prices.multiply(shares, axis=1)

    portfolio_value = holdings_value.sum(axis=1)
    weights_over_time = holdings_value.div(portfolio_value, axis=0)

    return portfolio_value, weights_over_time


def get_rebalance_dates(trading_dates, frequency):
    """Return the set of dates on which a calendar rebalance should happen.
    A rebalance is triggered on the first trading day of a new month,
    quarter, or year (depending on the chosen frequency)."""
    rebalance_dates = set()
    trading_dates = list(trading_dates)

    for i in range(1, len(trading_dates)):
        previous_day = trading_dates[i - 1]
        current_day = trading_dates[i]

        if frequency == "Monthly" and current_day.month != previous_day.month:
            rebalance_dates.add(current_day)
        elif frequency == "Quarterly" and current_day.quarter != previous_day.quarter:
            rebalance_dates.add(current_day)
        elif frequency == "Yearly" and current_day.year != previous_day.year:
            rebalance_dates.add(current_day)

    return rebalance_dates


def calendar_rebalance_strategy(prices, target_weights, initial_investment, frequency):
    """Rebalance the portfolio back to target weights at fixed calendar
    intervals (Monthly, Quarterly, or Yearly)."""
    rebalance_dates = get_rebalance_dates(prices.index, frequency)

    shares = (initial_investment * target_weights) / prices.iloc[0].values

    value_history = []
    weight_history = []

    for current_date in prices.index:
        day_prices = prices.loc[current_date].values
        value_today = np.sum(shares * day_prices)

        # If today is a scheduled rebalance date, reset shares so that
        # each asset returns exactly to its target weight.
        if current_date in rebalance_dates:
            shares = (value_today * target_weights) / day_prices

        current_weights = (shares * day_prices) / value_today
        value_history.append(value_today)
        weight_history.append(current_weights)

    portfolio_value = pd.Series(value_history, index=prices.index)
    weights_over_time = pd.DataFrame(weight_history, index=prices.index, columns=prices.columns)

    return portfolio_value, weights_over_time


def threshold_rebalance_strategy(prices, target_weights, initial_investment, threshold):
    """Rebalance the portfolio back to target weights whenever any single
    asset's actual weight drifts more than 'threshold' away from its
    target weight."""
    shares = (initial_investment * target_weights) / prices.iloc[0].values

    value_history = []
    weight_history = []

    for current_date in prices.index:
        day_prices = prices.loc[current_date].values
        value_today = np.sum(shares * day_prices)
        current_weights = (shares * day_prices) / value_today

        # Check how far each asset has drifted from its target weight.
        drift = np.abs(current_weights - target_weights)
        if drift.max() > threshold:
            shares = (value_today * target_weights) / day_prices
            current_weights = target_weights.copy()

        value_history.append(value_today)
        weight_history.append(current_weights)

    portfolio_value = pd.Series(value_history, index=prices.index)
    weights_over_time = pd.DataFrame(weight_history, index=prices.index, columns=prices.columns)

    return portfolio_value, weights_over_time


# ---------------------------------------------------------------------------
# PERFORMANCE METRICS
# ---------------------------------------------------------------------------

def calculate_metrics(portfolio_value):
    """Calculate the six required performance metrics for a portfolio
    value time series. Risk-free rate is assumed to be 0 for Sharpe Ratio."""
    daily_returns = portfolio_value.pct_change().dropna()

    initial_value = portfolio_value.iloc[0]
    final_value = portfolio_value.iloc[-1]

    total_return = (final_value / initial_value) - 1

    # Convert number of trading days into number of years (approx 252
    # trading days per year) to annualize the return.
    num_years = len(portfolio_value) / 252
    annualized_return = (final_value / initial_value) ** (1 / num_years) - 1

    annualized_volatility = daily_returns.std() * np.sqrt(252)

    sharpe_ratio = annualized_return / annualized_volatility if annualized_volatility != 0 else 0

    # Maximum drawdown: the largest peak-to-trough decline in portfolio value.
    running_max = portfolio_value.cummax()
    drawdown = (portfolio_value - running_max) / running_max
    max_drawdown = drawdown.min()

    return {
        "Final Value ($)": round(final_value, 2),
        "Total Return (%)": round(total_return * 100, 2),
        "Annualized Return (%)": round(annualized_return * 100, 2),
        "Annualized Volatility (%)": round(annualized_volatility * 100, 2),
        "Sharpe Ratio": round(sharpe_ratio, 2),
        "Max Drawdown (%)": round(max_drawdown * 100, 2),
    }


# ---------------------------------------------------------------------------
# PLOTLY VISUALIZATIONS
# ---------------------------------------------------------------------------

def plot_portfolio_values(value_series_dict):
    """Line chart comparing portfolio value over time across strategies."""
    fig = go.Figure()
    for strategy_name, value_series in value_series_dict.items():
        fig.add_trace(go.Scatter(
            x=value_series.index,
            y=value_series.values,
            mode="lines",
            name=strategy_name
        ))
    fig.update_layout(
        title="Portfolio Value Over Time",
        xaxis_title="Date",
        yaxis_title="Portfolio Value ($)"
    )
    return fig


def plot_risk_return(metrics_dict):
    """Scatter plot comparing annualized volatility (risk) vs annualized
    return for each strategy."""
    fig = go.Figure()
    for strategy_name, metrics in metrics_dict.items():
        fig.add_trace(go.Scatter(
            x=[metrics["Annualized Volatility (%)"]],
            y=[metrics["Annualized Return (%)"]],
            mode="markers+text",
            marker=dict(size=14),
            text=[strategy_name],
            textposition="top center",
            name=strategy_name
        ))
    fig.update_layout(
        title="Risk vs Return Comparison",
        xaxis_title="Annualized Volatility (%)",
        yaxis_title="Annualized Return (%)"
    )
    return fig


def plot_allocation_over_time(weights_over_time, strategy_name):
    """Stacked area chart showing how each asset's weight in the
    portfolio changes over time for a single chosen strategy."""
    fig = go.Figure()
    for ticker in weights_over_time.columns:
        fig.add_trace(go.Scatter(
            x=weights_over_time.index,
            y=weights_over_time[ticker] * 100,
            mode="lines",
            stackgroup="one",
            name=ticker
        ))
    fig.update_layout(
        title=f"Portfolio Allocation Over Time ({strategy_name})",
        xaxis_title="Date",
        yaxis_title="Weight (%)"
    )
    return fig


# ---------------------------------------------------------------------------
# STREAMLIT USER INTERFACE
# ---------------------------------------------------------------------------

def main():
    st.set_page_config(page_title="Portfolio Rebalancing Simulator")
    st.title("Portfolio Rebalancing Simulator")
    st.write(
        "A simple academic tool for comparing Buy & Hold, Calendar Rebalancing, "
        "and Threshold Rebalancing strategies using historical stock data."
    )

    # ---------------- Sidebar inputs ----------------
    st.sidebar.header("Portfolio Setup")
    tickers_text = st.sidebar.text_input("Tickers (comma separated)", "AAPL, MSFT, GOOGL")
    weights_text = st.sidebar.text_input("Weights % (comma separated)", "40, 30, 30")
    start_date = st.sidebar.date_input("Start Date", date(2019, 1, 1))
    end_date = st.sidebar.date_input("End Date", date(2024, 1, 1))
    initial_investment = st.sidebar.number_input("Initial Investment ($)", value=10000, step=1000)

    st.sidebar.header("Rebalancing Settings")
    frequency = st.sidebar.selectbox("Calendar Rebalance Frequency", ["Monthly", "Quarterly", "Yearly"])
    threshold_pct = st.sidebar.slider("Threshold Rebalance Trigger (%)", 1, 20, 5)

    allocation_choice = st.sidebar.selectbox(
        "Strategy to Show in Allocation Chart",
        ["Buy & Hold", "Calendar Rebalancing", "Threshold Rebalancing"],
        index=2
    )

    run_simulation = st.sidebar.button("Simulate")

    if not run_simulation:
        st.info("Set your portfolio in the sidebar and click 'Simulate' to begin.")
        return

    # ---------------- Input validation ----------------
    tickers, weights = parse_tickers_and_weights(tickers_text, weights_text)
    is_valid, message = validate_inputs(tickers, weights)
    if not is_valid:
        st.error(message)
        return

    if start_date >= end_date:
        st.error("Start date must be before end date.")
        return

    # ---------------- Data download ----------------
    with st.spinner("Downloading historical price data..."):
        prices, valid_tickers = download_prices(tickers, start_date, end_date)

    if prices.empty or len(valid_tickers) == 0:
        st.error("No valid price data could be downloaded. Please check your tickers.")
        return

    dropped_tickers = [t for t in tickers if t not in valid_tickers]
    if dropped_tickers:
        st.warning(f"These tickers were invalid and were excluded: {', '.join(dropped_tickers)}")

    # Re-align weights to only the tickers that were successfully downloaded,
    # then re-normalize so they still sum to 100%.
    weight_map = dict(zip(tickers, weights))
    aligned_weights = np.array([weight_map[t] for t in valid_tickers])
    aligned_weights = aligned_weights / aligned_weights.sum()
    prices = prices[valid_tickers]

    # ---------------- Run the three strategies ----------------
    threshold = threshold_pct / 100.0

    bh_value, bh_weights = buy_and_hold_strategy(prices, aligned_weights, initial_investment)
    cal_value, cal_weights = calendar_rebalance_strategy(prices, aligned_weights, initial_investment, frequency)
    th_value, th_weights = threshold_rebalance_strategy(prices, aligned_weights, initial_investment, threshold)

    value_series_dict = {
        "Buy & Hold": bh_value,
        "Calendar Rebalancing": cal_value,
        "Threshold Rebalancing": th_value,
    }

    weights_series_dict = {
        "Buy & Hold": bh_weights,
        "Calendar Rebalancing": cal_weights,
        "Threshold Rebalancing": th_weights,
    }

    # ---------------- Metrics table ----------------
    metrics_dict = {name: calculate_metrics(series) for name, series in value_series_dict.items()}
    metrics_table = pd.DataFrame(metrics_dict).T
    st.subheader("Performance Metrics")
    st.dataframe(metrics_table)

    # ---------------- Visualizations ----------------
    st.subheader("Portfolio Value Over Time")
    st.plotly_chart(plot_portfolio_values(value_series_dict))

    st.subheader("Risk vs Return Comparison")
    st.plotly_chart(plot_risk_return(metrics_dict))

    st.subheader("Portfolio Allocation Over Time")
    st.plotly_chart(plot_allocation_over_time(weights_series_dict[allocation_choice], allocation_choice))


if __name__ == "__main__":
    main()
