# Caio's Finance Dashboard

This Streamlit app wraps the four functions recovered from the linked **Finance Dashboard project** conversation. Verified against your supplied finance_data_analysis.ipynb: final asset, portfolio, and weight functions are structurally identical. Every returned table and series matched in four single/multi-asset, equal/custom-weight scenarios. The original notebook was not modified.

## Run

From this folder, using Python 3.10 or newer:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Manual inputs work without a Gemini key. For AI, create `.streamlit/secrets.toml` locally (this file is ignored by Git):

```toml
GEMINI_API_KEY = "your-key-here"
GEMINI_MODEL = "gemini-3.5-flash-lite"
```

Environment variables with the same names also work. Select a model your API account can access that supports structured outputs. Never put a real key in app.py or commit it.

Try: **AAPL 60%, MSFT 40%, from 2022-01-01 to 2025-01-01, benchmark SPY**.

## Step by step

1. **Keep the calculations in `finance.py`.** The original calculation bodies and output dictionary keys are retained. Downloads now run sequentially to avoid a cache database lock observed during testing. Moving the functions out of the notebook lets the dashboard import them without executing notebook cells.
2. **Collect settings in `app.py`.** The sidebar has tickers, dates, benchmark, and optional percentage weights. Blank weights mean equal allocation. A form applies the inputs together when you click Build dashboard.
3. **Validate inputs in `inputs.py`.** Both manual and AI settings must pass identical checks: unique symbols, valid dates, finite nonnegative weights, and a 100% total. The app supports long-only, fully invested portfolios.
4. **Call the engine in `pipeline.py`.** Download prices, calculate asset metrics, create weights, then calculate portfolio metrics. Missing symbols, gaps, invalid prices, and ranges with fewer than three prices produce an explanation. No missing ticker is silently discarded. Results are cached for an hour.
5. **Render the function outputs in `app.py`.** Display summary tables, cumulative returns, rolling volatility, drawdowns, weights, and portfolio-versus-benchmark growth. The metric selector provides all asset bar charts without repeating the same plotting code. CSV downloads contain the displayed summaries.
6. **Translate prompts in `ai_inputs.py`.** Google Gemini returns structured settings; Python validates them, fills the sidebar, and runs the same analysis automatically. AI never generates executable code or calculates financial metrics. Incomplete requests produce a clarification instead. Failed requests clear the prior dashboard so old results are not mistaken for new ones.

## Preserved calculation conventions

- Adjusted prices; 252 trading days per year; 30-return rolling volatility.
- Fixed weights applied every day imply daily rebalancing, without transaction costs.
- The existing Sharpe label represents CAGR / annualized volatility, without a risk-free rate.
- Asset CAGR counts price rows; portfolio CAGR counts return rows.
- Drawdown starts its peak at the first calculated growth value, potentially understating an initial loss. No initial $1 baseline is inserted in the recovered functions.
- The data provider's end date is exclusive. Short periods may have no rolling-volatility line; undefined ratios remain missing.

These conventions are documented rather than changed to preserve your existing logic. The app rejects incomplete price matrices before the original functions run, avoiding differences in pandas missing-price filling behavior.

## Tests

```sh
pip install pytest
python -m pytest -q
```

Tests use deterministic synthetic prices and mocked AI responses; they do not spend API credits.

## References

- [Streamlit forms](https://docs.streamlit.io/develop/api-reference/execution-flow/st.form)
- [Streamlit session state](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state)
- [Google Gemini structured outputs](https://ai.google.dev/gemini-api/docs/structured-output)

## Chart views and AI summary

Use Together / Individual under Assets to overlay stocks or show separate charts per stock. Generate summary creates up to 300 words from the current allocations, calculated asset/portfolio metrics and benchmark return. It sends only these results and dates to Gemini. The summary persists when switching chart views and clears when a new analysis is built. Python enforces the word limit.
