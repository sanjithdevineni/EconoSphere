"""Behavioral tests for the economy simulation."""

import pytest

from simulation.economy_model import EconomyModel


def advance(model: EconomyModel, steps: int):
    """Advance the model and collect metrics for each step."""
    return [model.step() for _ in range(steps)]


def rolling_average(values, window):
    window = min(window, len(values))
    if window == 0:
        return 0
    tail = values[-window:]
    return sum(tail) / len(tail)


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


def test_recession_crisis_raises_unemployment_and_hits_gdp():
    model = EconomyModel(seed=11)
    advance(model, 25)
    history = model.metrics.get_history()
    pre_unemployment = rolling_average(history['unemployment'], 5)
    pre_gdp = rolling_average(history['gdp'], 5)

    model.trigger_crisis('recession')
    advance(model, 6)
    history = model.metrics.get_history()
    recent_unemployment = history['unemployment'][-6:]
    recent_gdp = history['gdp'][-6:]
    max_unemployment = max(recent_unemployment)
    min_gdp = min(recent_gdp)

    assert max_unemployment >= pre_unemployment + 7, "Recession should materially raise unemployment"
    assert min_gdp <= pre_gdp * 0.85, "Recession should push GDP lower"


def test_inflation_crisis_spikes_price_growth():
    model = EconomyModel(seed=19)
    advance(model, 20)
    history = model.metrics.get_history()
    pre_inflation = rolling_average(history['inflation'], 5)

    model.trigger_crisis('inflation')
    advance(model, 5)
    history = model.metrics.get_history()
    post_inflation = rolling_average(history['inflation'], 5)

    assert post_inflation >= pre_inflation + 2, "Inflation crisis should lift price growth"


def test_latest_metrics_match_history_tail():
    model = EconomyModel(seed=5)
    advance(model, 10)
    current = model.get_current_state()
    history = model.metrics.get_history()

    assert abs(current['gdp'] - history['gdp'][-1]) < 1e-6
    assert abs(current['unemployment'] - history['unemployment'][-1]) < 1e-6
    assert abs(current['inflation'] - history['inflation'][-1]) < 1e-6
