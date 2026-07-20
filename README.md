# Finance-Dashboard-AI-project
AI-Powered Portfolio Risk &amp; Performance Dashboard  This project analyzes stock and ETF performance using historical market data from Yahoo Finance. The current version is a research notebook focused on financial metric calculation and visualization. The next phase will convert the analysis into a Streamlit dashboard with AI.

# AI-Powered Portfolio Risk & Performance Dashboard

This project analyzes the historical performance and risk of individual assets and a custom portfolio using real market data from Yahoo Finance.

The main goal of this project is to build a complete finance/data science workflow: starting from raw stock price data, calculating financial metrics, creating visualizations, and later turning everything into an interactive dashboard with an AI layer.

Right now, the project is in the notebook analysis phase. The dashboard and AI features are the next step.

## Project Overview

The project allows the user to choose a group of stocks or ETFs, download historical price data, calculate return and risk metrics, and compare the portfolio against SPY as a benchmark.

The analysis is divided into two main parts:

1. Individual asset analysis  
2. Portfolio-level analysis  

For the individual assets, the project compares each ticker separately. For the portfolio section, the project combines the selected assets using custom weights and evaluates how the full portfolio behaves over time.

## Current Features

The current notebook includes:

- Historical stock data download using `yfinance`
- Daily returns calculation
- Cumulative return analysis
- Total return calculation
- Average daily return
- CAGR
- Annualized volatility
- 30-day rolling volatility
- Max drawdown
- Best and worst trading days
- Value at Risk 95%
- Expected Shortfall 95%
- Sharpe Ratio
- Correlation with SPY
- Portfolio weights
- Portfolio daily returns
- Portfolio cumulative return
- Portfolio drawdown
- Portfolio rolling volatility
- Portfolio vs SPY comparison

## Visualizations

The project currently includes visualizations for both individual assets and the portfolio.

### Individual Asset Visualizations

- Cumulative return over time
- Rolling volatility over time
- Total return by ticker
- Average daily return by ticker
- CAGR by ticker
- Annualized volatility by ticker
- Max drawdown by ticker
- Sharpe ratio by ticker

### Portfolio Visualizations

- Portfolio weights
- Portfolio cumulative return
- Portfolio vs SPY cumulative growth
- Portfolio drawdown over time
- Portfolio rolling volatility

Some metrics, such as VaR, Expected Shortfall, best/worst day, and correlation with SPY, are kept mainly in the summary table because they are useful but not always visually intuitive.

## Why SPY Is Used

SPY is used as the benchmark for the project. Even if the user does not include SPY in the portfolio, the app will use SPY internally for comparison metrics such as correlation, beta, and portfolio comparison.
