"""Checks at the app boundary, preserving the original calculation functions."""
import numpy as np
from finance import get_stock_data, calculate_asset_metrics, create_weights, calculate_portfolio_metrics


def analyze(settings):
    prices = get_stock_data(settings.tickers, settings.start_date.isoformat(),
                            settings.end_date.isoformat(), settings.benchmark)
    required = list(dict.fromkeys([*settings.tickers, settings.benchmark]))
    missing = [t for t in required if t not in prices or prices[t].dropna().empty]
    if missing:
        raise ValueError("No price data for: " + ", ".join(missing))
    prices = prices[required]
    # Refuse incomplete histories rather than silently alter notebook alignment rules.
    if prices.isna().any().any():
        raise ValueError("Price histories contain gaps or different listing dates. "
                         "Choose a later start date or another ticker combination.")
    if len(prices) < 3:
        raise ValueError("Choose a range with at least three trading-day prices.")
    if not np.isfinite(prices.to_numpy()).all() or (prices <= 0).any().any():
        raise ValueError("The data provider returned invalid prices.")
    assets = calculate_asset_metrics(prices, settings.tickers, settings.benchmark)
    custom = dict(zip(settings.tickers, settings.weights)) if settings.weights is not None else None
    weights = create_weights(settings.tickers, custom)
    portfolio = calculate_portfolio_metrics(assets["daily_returns"], settings.tickers,
                                             weights, settings.benchmark)
    return prices, assets, weights, portfolio
