"""Run with: streamlit run app.py"""
from datetime import date
import os
from html import escape
import pandas as pd
import streamlit as st
from ai_inputs import parse_prompt
from ai_summary import summary_payload, generate_summary
from inputs import manual_inputs
from pipeline import analyze
from google.genai.errors import APIError
import httpx

st.set_page_config(page_title="Caio Rocha AI Financial Dashboard Project", page_icon="📈", layout="wide")
st.markdown("""
<style>
.individual-ticker-label {
    color: #4da6ff;
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    margin: 0.8rem 0 0.15rem 0;
}
</style>
""", unsafe_allow_html=True)
st.title("Caio Rocha AI Financial Dashboard Project")
st.caption("Explore assets, compare a portfolio, use any date and build an analysis from one prompt.")


def secret(name, default=""):
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets.get(name, default)
    except FileNotFoundError:
        return default


@st.cache_data(ttl=3600, show_spinner=False)
def run_analysis(payload):
    from inputs import DashboardInputs
    return analyze(DashboardInputs.model_validate_json(payload))


defaults = dict(tickers="AAPL, MSFT, NVDA, META, QQQ", weights="",
                start=date(2020, 1, 1), end=date.today(), benchmark="SPY")
for key, value in defaults.items():
    st.session_state.setdefault(key, value)

# AI runs before sidebar widgets so its settings can safely populate them.
requested = None
with st.expander("Build with AI", expanded=True):
    st.caption("Defaults: equal weights · Jan 1, 2020 to today · SPY benchmark. "
               "Your prompt is sent to Google Gemini when you click Generate.")
    with st.form("ai"):
        prompt = st.text_area("Describe your portfolio", placeholder=
                              "AAPL 60%, MSFT 40%, from 2022-01-01 to 2025-01-01, benchmark SPY")
        generate = st.form_submit_button("Generate dashboard")
    if generate:
        st.session_state.pop("result", None)
        try:
            with st.spinner("Reading your portfolio request…"):
                requested = parse_prompt(prompt, secret("GEMINI_API_KEY"),
                                         secret("GEMINI_MODEL", "gemini-3.5-flash-lite"))
            st.session_state.update(
                tickers=", ".join(requested.tickers),
                weights=", ".join(str(w * 100) for w in requested.weights)
                if requested.weights is not None else "",
                start=requested.start_date, end=requested.end_date, benchmark=requested.benchmark)
        except ValueError as exc:
            st.error(str(exc))
        except APIError as exc:
            messages = {
                400: "Gemini rejected the request format or API key (400).",
                401: "Gemini could not authenticate the API key (401).",
                403: "Gemini denied access (403). Check the key's API restrictions and project access.",
                404: "The configured Gemini model is unavailable (404). Check GEMINI_MODEL.",
                429: "Gemini's request limit or quota was reached (429). Wait and retry, or check your Google AI Studio quota.",
            }
            st.error(messages.get(exc.code, "Gemini is temporarily unavailable. Please retry."))
        except httpx.TimeoutException:
            st.error("Gemini took too long to respond. Please retry.")
        except httpx.ConnectError:
            st.error("The dashboard cannot connect to Gemini. This is a server network issue, not an API-key permission error.")
        except Exception as exc:
            st.error(f"AI request failed ({type(exc).__name__}). Please report this error type.")

with st.sidebar:
    st.header("Dashboard inputs")
    with st.form("manual"):
        st.text_input("Tickers, separated by commas", key="tickers")
        st.date_input("Start date", key="start")
        st.date_input("End date (exclusive)", key="end")
        st.text_input("Benchmark", key="benchmark")
        st.text_input("Weights (%) in ticker order", key="weights", help="Example: 60, 40. Leave blank for equal weights.")
        submit = st.form_submit_button("Build dashboard")
    st.caption("Edit inputs, then click Build dashboard to apply them.")

if submit:
    st.session_state.pop("result", None)
    try:
        requested = manual_inputs(*(st.session_state[k] for k in
                                    ["tickers", "weights", "start", "end", "benchmark"]))
    except ValueError as exc:
        st.error(str(exc))

if requested is not None:
    try:
        with st.spinner("Loading prices and calculating your dashboard…"):
            outputs = run_analysis(requested.model_dump_json())
        st.session_state.result = (requested, outputs)
        st.session_state.pop("ai_summary", None)
    except ValueError as exc:
        st.error(str(exc))
    except Exception:
        st.error("Could not load the analysis. Check the ticker symbols and connection, then retry.")

if "result" not in st.session_state:
    st.info("Enter your portfolio in the sidebar or describe it above to get started.")
    st.stop()

settings, (prices, assets, weights, portfolio) = st.session_state.result
st.subheader("Your analysis")
st.write(" · ".join(f"{t}: {w:.2%}" for t, w in weights.items()))
st.caption(f"Requested: {settings.start_date} to {settings.end_date} (exclusive). "
           f"Available prices: {prices.index[0].date()} to {prices.index[-1].date()}. "
           f"Benchmark: {settings.benchmark}.")
for col, metric in zip(st.columns(3), ["Total Return", "CAGR", "Annualized Volatility"]):
    col.metric(metric, f"{portfolio['summary'].iloc[0][metric]:.2%}")

with st.container(border=True):
    st.subheader("AI portfolio summary")
    st.caption("Up to 300 words based on this analysis. Generating sends allocations and calculated metrics to Gemini.")
    if st.button("Generate summary", key="generate_summary"):
        try:
            with st.spinner("Summarizing your portfolio…"):
                st.session_state.ai_summary = generate_summary(
                    summary_payload(settings, prices, assets, weights, portfolio),
                    secret("GEMINI_API_KEY"), secret("GEMINI_MODEL", "gemini-3.5-flash-lite"))
        except Exception:
            st.warning("The summary is unavailable right now. Please retry; your dashboard is still available.")
    if st.session_state.get("ai_summary"):
        st.write(st.session_state.ai_summary)
    else:
        st.caption("Generate a short explanation of performance, risk, and the benchmark comparison.")

asset_tab, portfolio_tab, notes_tab = st.tabs(["Assets", "Portfolio", "Calculation notes"])
with asset_tab:
    st.dataframe(assets["display_summary"])
    st.download_button("Download asset summary", assets["display_summary"].to_csv(), "assets.csv")
    chart_view = st.radio("Asset chart view", ["Together", "Individual"], horizontal=True, key="chart_view")
    for label, key in [("Cumulative return (%)", "cumulative_return"),
                       ("30-day annualized rolling volatility (%)", "rolling_volatility"),
                       ("Drawdown (%)", "drawdown")]:
        st.subheader(label)
        if chart_view == "Together":
            st.line_chart(assets[key] * 100)
        else:
            for ticker in settings.tickers:
                st.markdown(
                    f'<div class="individual-ticker-label">{escape(ticker)}</div>',
                    unsafe_allow_html=True,
                )
                st.line_chart(assets[key][[ticker]] * 100)
    metric = st.selectbox("Compare an asset metric", assets["summary"].columns)
    percent = metric not in ["Sharpe Ratio", f"Correlation with {settings.benchmark}",
                            f"Beta vs {settings.benchmark}"]
    st.caption(metric + (" (%)" if percent else ""))
    st.bar_chart(assets["summary"][[metric]] * (100 if percent else 1))
with portfolio_tab:
    st.dataframe(portfolio["display_summary"])
    st.download_button("Download portfolio summary", portfolio["display_summary"].to_csv(), "portfolio.csv")
    st.subheader("Weights (%)")
    st.bar_chart(weights * 100)
    st.subheader(f"Growth of $1: portfolio vs {settings.benchmark}")
    benchmark_growth = (1 + assets["daily_returns"][settings.benchmark]).cumprod()
    st.line_chart(pd.DataFrame({"Portfolio": portfolio["portfolio_cumulative_growth"],
                               f"Benchmark ({settings.benchmark})": benchmark_growth}))
    for label, key in [("Cumulative return (%)", "portfolio_cumulative_return"),
                       ("Drawdown (%)", "portfolio_drawdown"),
                       ("30-day annualized rolling volatility (%)", "portfolio_rolling_volatility")]:
        st.subheader(label)
        st.line_chart(portfolio[key] * 100)
with notes_tab:
    st.write("These calculations were verified against the finance_data_analysis.ipynb notebook (located on github). "
             "Prices are adjusted; annualization uses 252 trading days. "
             "Portfolio returns apply fixed weights each day (daily rebalancing), without fees.")
    st.write("The notebook's Sharpe Ratio is CAGR divided by annualized volatility. "
             "Drawdown peaks begin at the first calculated growth value, so an initial loss "
             "can be understated. Asset CAGR counts price rows; portfolio CAGR counts return rows. "
             "These existing conventions are preserved, not corrected in this conversion.")
    st.write("Rolling volatility needs 30 daily returns. Undefined metrics appear as missing values. "
             "Incomplete price histories are rejected so gaps cannot silently change the calculations.")
    st.write("AI extracts settings and can explain calculated results. Python performs all financial calculations. "
             "The same validation and finance functions handle both manual and AI requests.")
    st.write("This dashboard is intended for visual and educational purposes only. It is not supposed to give you financial tips.")
