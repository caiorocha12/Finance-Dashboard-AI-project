"""Shared validation for sidebar and AI inputs; no financial calculations."""
from datetime import date
import math
import re
from pydantic import BaseModel, ConfigDict, model_validator


class DashboardInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tickers: list[str]
    weights: list[float] | None
    start_date: date
    end_date: date
    benchmark: str

    @model_validator(mode="after")
    def validate_inputs(self):
        self.tickers = [t.strip().upper() for t in self.tickers]
        self.benchmark = self.benchmark.strip().upper()
        if not 1 <= len(self.tickers) <= 25:
            raise ValueError("Choose between 1 and 25 tickers.")
        if len(set(self.tickers)) != len(self.tickers):
            raise ValueError("Each ticker must appear only once.")
        if any(not re.fullmatch(r"[A-Z0-9^][A-Z0-9.^=\-]{0,19}", t)
               for t in [*self.tickers, self.benchmark]):
            raise ValueError("Enter valid ticker symbols, such as AAPL or BRK-B.")
        if not self.start_date < self.end_date <= date.today():
            raise ValueError("Start must precede end; end cannot be in the future.")
        if self.weights is not None:
            if len(self.weights) != len(self.tickers):
                raise ValueError("Provide one weight per ticker, in the same order.")
            if any(not math.isfinite(w) or w < 0 or w > 1 for w in self.weights):
                raise ValueError("Weights must be finite and between 0% and 100%.")
            if not math.isclose(sum(self.weights), 1, abs_tol=1e-6):
                raise ValueError("Weights must sum to 100%.")
        return self


def manual_inputs(tickers, weights, start, end, benchmark):
    return DashboardInputs(
        tickers=[t for t in re.split(r"[,\s]+", tickers.strip()) if t],
        weights=[float(w.strip().removesuffix("%")) / 100
                 for w in weights.split(",")] if weights.strip() else None,
        start_date=start, end_date=end, benchmark=benchmark,
    )
