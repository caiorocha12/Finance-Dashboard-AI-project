# Original functions recovered from Finance Dashboard project.
from datetime import datetime
import numpy as np
import pandas as pd
import yfinance as yf

def calculate_portfolio_metrics(daily_returns, portfolio_tickers, weights, benchmark="SPY"):

    # Returns for only the assets inside the portfolio
    asset_daily_returns = daily_returns[portfolio_tickers]

    # Portfolio daily returns
    portfolio_daily_returns = asset_daily_returns.dot(weights)

    # Cumulative growth and cumulative return
    portfolio_cumulative_growth = (1 + portfolio_daily_returns).cumprod()
    portfolio_cumulative_return = portfolio_cumulative_growth - 1

    # Total return
    portfolio_total_return = portfolio_cumulative_return.iloc[-1]

    # Average daily return
    portfolio_average_dailyreturn = portfolio_daily_returns.mean()

    # CAGR
    portfolio_years = len(portfolio_daily_returns) / 252
    portfolio_cagr = (np.power(portfolio_cumulative_growth.iloc[-1], 1 / portfolio_years)) - 1

    # Volatility
    portfolio_daily_std = portfolio_daily_returns.std()
    portfolio_annualized_volatility = portfolio_daily_std * np.sqrt(252)

    # Rolling volatility
    portfolio_daily_rolling_volatility = portfolio_daily_returns.rolling(window=30).std()
    portfolio_annual_rolling_volatility = portfolio_daily_rolling_volatility * np.sqrt(252)

    # Drawdown
    portfolio_running_peak = portfolio_cumulative_growth.cummax()
    portfolio_drawdown = (portfolio_cumulative_growth - portfolio_running_peak) / portfolio_running_peak
    portfolio_drawdown_max = portfolio_drawdown.min()

    # Best and worst days
    portfolio_best_day = portfolio_daily_returns.max()
    portfolio_worst_day = portfolio_daily_returns.min()

    # VaR 95%
    portfolio_value_atrisk95 = portfolio_daily_returns.quantile(0.05)

    # Expected Shortfall 95%
    portfolio_bad_days_mask = portfolio_daily_returns <= portfolio_value_atrisk95
    portfolio_bad_returns = portfolio_daily_returns[portfolio_bad_days_mask]
    portfolio_expected_shortfall = portfolio_bad_returns.mean()

    # Sharpe Ratio
    portfolio_sharpe_ratio = portfolio_cagr / portfolio_annualized_volatility

    # Correlation with benchmark
    portfolio_benchmark_correlation = portfolio_daily_returns.corr(daily_returns[benchmark])

    # Beta vs benchmark
    portfolio_beta = portfolio_daily_returns.cov(daily_returns[benchmark]) / daily_returns[benchmark].var()

    # Summary table
    portfolio_summary_df = pd.DataFrame({
        "Total Return": [portfolio_total_return],
        "Average Daily Return": [portfolio_average_dailyreturn],
        "CAGR": [portfolio_cagr],
        "Annualized Volatility": [portfolio_annualized_volatility],
        "Max Drawdown": [portfolio_drawdown_max],
        "Best Day": [portfolio_best_day],
        "Worst Day": [portfolio_worst_day],
        "VaR 95%": [portfolio_value_atrisk95],
        "Expected Shortfall 95%": [portfolio_expected_shortfall],
        "Sharpe Ratio": [portfolio_sharpe_ratio],
        f"Correlation with {benchmark}": [portfolio_benchmark_correlation],
        f"Beta vs {benchmark}": [portfolio_beta]
    }, index=["Portfolio"])

    # Display version
    portfolio_display_df = portfolio_summary_df.copy()

    percentage_columns = [
        "Total Return",
        "Average Daily Return",
        "CAGR",
        "Annualized Volatility",
        "Max Drawdown",
        "Best Day",
        "Worst Day",
        "VaR 95%",
        "Expected Shortfall 95%"
    ]

    portfolio_display_df[percentage_columns] = portfolio_display_df[percentage_columns] * 100
    portfolio_display_df = portfolio_display_df.round(2)

    portfolio_display_df = portfolio_display_df.rename(columns={
        "Total Return": "Total Return (%)",
        "Average Daily Return": "Average Daily Return (%)",
        "CAGR": "CAGR (%)",
        "Annualized Volatility": "Annualized Volatility (%)",
        "Max Drawdown": "Max Drawdown (%)",
        "Best Day": "Best Day (%)",
        "Worst Day": "Worst Day (%)",
        "VaR 95%": "VaR 95% (%)",
        "Expected Shortfall 95%": "Expected Shortfall 95% (%)"
    })

    results = {
        "portfolio_daily_returns": portfolio_daily_returns,
        "portfolio_cumulative_growth": portfolio_cumulative_growth,
        "portfolio_cumulative_return": portfolio_cumulative_return,
        "portfolio_rolling_volatility": portfolio_annual_rolling_volatility,
        "portfolio_drawdown": portfolio_drawdown,
        "summary": portfolio_summary_df,
        "display_summary": portfolio_display_df
    }

    return results


def create_weights(portfolio_tickers, custom_weights=None):

    if custom_weights is None:
        weights = pd.Series(
            1 / len(portfolio_tickers),
            index=portfolio_tickers
        )

    else:
        weights = pd.Series(custom_weights)
        weights = weights.reindex(portfolio_tickers)

        if weights.isnull().any():
            missing = weights[weights.isnull()].index.tolist()
            raise ValueError(f"Missing weights for: {missing}")

        if round(weights.sum(), 4) != 1:
            raise ValueError("Weights must sum to 1.0")

    return weights


# Function that calls for the data

def get_stock_data(tickers, start_date, end_date=None, benchmark="SPY"):

    if end_date is None:
        end_date = datetime.today().strftime("%Y-%m-%d")
    
    download_tickers = tickers.copy()

    if benchmark not in download_tickers:
        download_tickers.append(benchmark)

    data = yf.download(
        tickers=download_tickers,
        start=start_date,
        end=end_date,
        interval="1d",
        auto_adjust=True,
        threads=False  # Avoid concurrent cache writes; calculations are unchanged.
    )

    close_price = data["Close"]

    if isinstance(close_price, pd.Series):
        close_price = close_price.to_frame()

    close_price = close_price.dropna(how="all")

    return close_price


def calculate_asset_metrics(close_price, portfolio_tickers, benchmark="SPY"):

    # Daily returns for all downloaded tickers, including benchmark
    daily_returns = close_price.pct_change().dropna()

    # Prices and returns for only the user's selected portfolio assets
    asset_close_price = close_price[portfolio_tickers]
    asset_daily_returns = daily_returns[portfolio_tickers]

    # Cumulative growth and cumulative return
    cumulative_growth = (1 + asset_daily_returns).cumprod()
    cumulative_return = cumulative_growth - 1

    # Total return
    total_return = (asset_close_price.iloc[-1] / asset_close_price.iloc[0]) - 1

    # Average daily return
    average_dailyreturn = asset_daily_returns.mean()

    # CAGR
    years = len(asset_close_price) / 252
    cagr = (np.power(asset_close_price.iloc[-1] / asset_close_price.iloc[0], 1 / years)) - 1

    # Volatility
    daily_std = asset_daily_returns.std()
    annualized_volatility = daily_std * np.sqrt(252)

    # Rolling volatility
    daily_rolling_volatility = asset_daily_returns.rolling(window=30).std()
    annual_rolling_volatility = daily_rolling_volatility * np.sqrt(252)

    # Drawdown
    running_peak = cumulative_growth.cummax()
    drawdown = (cumulative_growth - running_peak) / running_peak
    drawdown_max = drawdown.min()

    # Best and worst days
    best_day = asset_daily_returns.max()
    worst_day = asset_daily_returns.min()

    # VaR 95%
    value_atrisk95 = asset_daily_returns.quantile(0.05)

    # Expected Shortfall 95%
    bad_days_mask = asset_daily_returns <= value_atrisk95
    bad_returns = asset_daily_returns[bad_days_mask]
    expected_shortfall = bad_returns.mean()

    # Sharpe Ratio
    sharpe_ratio = cagr / annualized_volatility

    # Correlation with benchmark
    benchmark_returns = daily_returns[benchmark]
    benchmark_correlation = asset_daily_returns.corrwith(benchmark_returns)

    # Beta vs benchmark
    asset_beta = asset_daily_returns.apply(
        lambda asset_returns: asset_returns.cov(benchmark_returns) / benchmark_returns.var()
    )

    # Summary table
    summary_df = pd.concat([
        total_return,
        average_dailyreturn,
        cagr,
        annualized_volatility,
        drawdown_max,
        best_day,
        worst_day,
        value_atrisk95,
        expected_shortfall,
        sharpe_ratio,
        benchmark_correlation,
        asset_beta
    ], axis=1)

    summary_df.columns = [
        "Total Return",
        "Average Daily Return",
        "CAGR",
        "Annualized Volatility",
        "Max Drawdown",
        "Best Day",
        "Worst Day",
        "VaR 95%",
        "Expected Shortfall 95%",
        "Sharpe Ratio",
        f"Correlation with {benchmark}",
        f"Beta vs {benchmark}"
    ]

    # Display version
    display_summary_df = summary_df.copy()

    percentage_columns = [
        "Total Return",
        "Average Daily Return",
        "CAGR",
        "Annualized Volatility",
        "Max Drawdown",
        "Best Day",
        "Worst Day",
        "VaR 95%",
        "Expected Shortfall 95%"
    ]

    display_summary_df[percentage_columns] = display_summary_df[percentage_columns] * 100
    display_summary_df = display_summary_df.round(2)

    display_summary_df = display_summary_df.rename(columns={
        "Total Return": "Total Return (%)",
        "Average Daily Return": "Average Daily Return (%)",
        "CAGR": "CAGR (%)",
        "Annualized Volatility": "Annualized Volatility (%)",
        "Max Drawdown": "Max Drawdown (%)",
        "Best Day": "Best Day (%)",
        "Worst Day": "Worst Day (%)",
        "VaR 95%": "VaR 95% (%)",
        "Expected Shortfall 95%": "Expected Shortfall 95% (%)"
    })

    results = {
        "daily_returns": daily_returns,
        "asset_daily_returns": asset_daily_returns,
        "cumulative_growth": cumulative_growth,
        "cumulative_return": cumulative_return,
        "rolling_volatility": annual_rolling_volatility,
        "drawdown": drawdown,
        "summary": summary_df,
        "display_summary": display_summary_df
    }

    return results
