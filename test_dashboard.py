from datetime import date
from unittest.mock import patch, MagicMock
import numpy as np
import pandas as pd
import pytest
from inputs import DashboardInputs, manual_inputs
from pipeline import analyze
from ai_inputs import parse_prompt, ParsedRequest


def settings(**changes):
    data = dict(tickers=["AAPL", "MSFT"], weights=[0.6, 0.4],
                start_date="2022-01-01", end_date="2023-01-01", benchmark="SPY")
    return DashboardInputs(**(data | changes))


def prices():
    rng = np.random.default_rng(12)
    return pd.DataFrame(100 * np.cumprod(1 + rng.normal(.001, .01, (65, 3)), axis=0),
                        columns=["AAPL", "MSFT", "SPY"], index=pd.bdate_range("2022-01-03", periods=65))


@pytest.mark.parametrize("changes", [dict(weights=[.3, .4]), dict(weights=[float('nan'), .4]),
    dict(weights=[-.1, 1.1]), dict(weights=[1]), dict(tickers=["AAPL", "aapl"]),
    dict(start_date="2023-01-01"), dict(tickers=[]), dict(benchmark="bad symbol")])
def test_reject_bad_inputs(changes):
    with pytest.raises(ValueError):
        settings(**changes)


def test_manual_percentages():
    s = manual_inputs("aapl, msft", "60%, 40", date(2022, 1, 1), date(2023, 1, 1), "spy")
    assert s == settings()


def test_pipeline_preserves_weighted_returns():
    p = prices()
    with patch("pipeline.get_stock_data", return_value=p):
        _, a, w, result = analyze(settings())
    expected = p.pct_change().dropna()[["AAPL", "MSFT"]].dot(w)
    pd.testing.assert_series_equal(result["portfolio_daily_returns"], expected)
    assert result["summary"].iloc[0]["Total Return"] == pytest.approx((1 + expected).prod() - 1)
    assert list(a["summary"].index) == ["AAPL", "MSFT"]


def test_gaps_rejected():
    p = prices()
    p.iloc[4, 0] = np.nan
    with patch("pipeline.get_stock_data", return_value=p), pytest.raises(ValueError, match="gaps"):
        analyze(settings())


def test_ai_response_validated():
    client = MagicMock()
    parsed = ParsedRequest(
        **settings().model_dump(mode="json"), clarification=None)
    client.models.generate_content.return_value.text = parsed.model_dump_json()
    with patch("ai_inputs.genai.Client") as factory:
        factory.return_value.__enter__.return_value = client
        assert parse_prompt("AAPL 60%, MSFT 40%", "test-key", "test-model") == settings()
        parsed.weights = [.1, .1]
        client.models.generate_content.return_value.text = parsed.model_dump_json()
        with pytest.raises(ValueError):
            parse_prompt("test", "test-key", "test-model")
        client.models.generate_content.return_value.text = None
        with pytest.raises(ValueError, match="usable"):
            parse_prompt("test", "test-key", "test-model")


def test_streamlit_manual_dashboard():
    from streamlit.testing.v1 import AppTest
    with patch("pipeline.get_stock_data", return_value=prices()):
        app = AppTest.from_file("app.py").run()
        assert not app.exception
        app.text_input(key="tickers").set_value("AAPL, MSFT")
        app.text_input(key="weights").set_value("60, 40")
        next(b for b in app.button if b.label == "Build dashboard").click().run()
        assert not app.exception
        assert len(app.dataframe) == 2
        assert len(app.metric) == 3

        app.text_input(key="weights").set_value("10, 10")
        next(b for b in app.button if b.label == "Build dashboard").click().run()
        assert app.error
        assert len(app.metric) == 0


def test_chart_toggle_and_summary_lifecycle():
    from streamlit.testing.v1 import AppTest
    with patch("pipeline.get_stock_data", return_value=prices()), patch("ai_summary.generate_summary", return_value="Historical summary.") as summary:
        app = AppTest.from_file("app.py").run()
        app.text_input(key="tickers").set_value("AAPL, MSFT")
        next(b for b in app.button if b.label == "Build dashboard").click().run()
        app.button(key="generate_summary").click().run()
        assert summary.call_count == 1
        app.radio(key="chart_view").set_value("Individual").run()
        assert not app.exception
        assert summary.call_count == 1
        assert app.session_state['ai_summary'] == 'Historical summary.'
        next(b for b in app.button if b.label == "Build dashboard").click().run()
        assert 'ai_summary' not in app.session_state


def test_summary_limit_and_empty_response():
    from ai_summary import generate_summary
    with patch('ai_summary.genai.Client') as factory:
        client = factory.return_value.__enter__.return_value
        client.models.generate_content.return_value.text = 'word ' * 350
        assert len(generate_summary('{}', 'test-key', 'test-model').split()) == 300
        client.models.generate_content.return_value.text = ''
        with pytest.raises(ValueError):
            generate_summary('{}', 'test-key', 'test-model')


def test_streamlit_ai_populates_and_runs():
    from streamlit.testing.v1 import AppTest
    with patch("pipeline.get_stock_data", return_value=prices()), patch("ai_inputs.parse_prompt", return_value=settings()):
        app = AppTest.from_file("app.py").run()
        app.text_area[0].set_value("AAPL 60%, MSFT 40%")
        app.button[0].click().run()
        assert not app.exception
        assert app.text_input(key="tickers").value == "AAPL, MSFT"
        assert len(app.metric) == 3
