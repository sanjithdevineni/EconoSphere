"""Behavioral tests for the economy simulation."""

import statistics

from simulation.economy_model import EconomyModel


def advance(model: EconomyModel, steps: int):
    """Advance the model and collect metrics for each step."""
    return [model.step() for _ in range(steps)]


def rolling_average(values, window):
    return statistics.mean(values[-window:])


def test_policy_tightening_increases_unemployment():
    model = EconomyModel(seed=42)
    advance(model, 20)
    baseline = model.metrics.get_history()['unemployment']
    baseline_avg = rolling_average(baseline, 5)

    model.set_interest_rate(0.12)
    model.set_tax_rate(0.4)
    advance(model, 20)
    tightened = model.metrics.get_history()['unemployment']
    tightened_avg = rolling_average(tightened, 5)

    assert tightened_avg >= baseline_avg + 5, "Tighter policy should raise unemployment"


def test_gdp_growth_stabilises_after_initial_ramp():
    model = EconomyModel(seed=7)
    series = [step['gdp'] for step in advance(model, 40)]

    assert min(series) > 0, "GDP should stay positive"

    # Ignore first five transitory steps when checking growth stability
    deltas = [abs(series[i + 1] - series[i]) / max(series[i], 1)
              for i in range(5, len(series) - 1)]
    assert max(deltas) < 0.25, "GDP swings should dampen after initial ramp-up"


def test_inflation_stays_within_reasonable_bounds():
    model = EconomyModel(seed=3)
    advance(model, 40)
    inflation = model.metrics.get_history()['inflation']
    assert inflation, "Inflation history should not be empty"
    max_abs_inflation = max(abs(value) for value in inflation)
    assert max_abs_inflation < 20, "Inflation should remain below 20% per period"
