"""Policy recommendation using surrogate modeling of the simulator."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

from simulation.economy_model import EconomyModel


# Policy ranges based on UI sliders (values in model units)
POLICY_RANGES = {
    "tax_rate": (0.0, 0.5),          # 0% - 50%
    "interest_rate": (0.0, 0.1),     # 0% - 10%
    "welfare": (0.0, 2000.0),        # 0 - $2000
    "govt_spending": (0.0, 50000.0), # 0 - $50k
}


@dataclass
class PolicyRecommendation:
    policy: Dict[str, float]
    predicted: Dict[str, float]
    actual: Dict[str, float]
    samples_used: int
    notes: str | None = None


def _sample_policy(rng: random.Random) -> Dict[str, float]:
    return {
        key: rng.uniform(*bounds)
        for key, bounds in POLICY_RANGES.items()
    }


def _sample_near(policy: Dict[str, float], rng: random.Random, scale: float = 0.1) -> Dict[str, float]:
    perturbed = {}
    for key, bounds in POLICY_RANGES.items():
        center = policy[key]
        span = bounds[1] - bounds[0]
        delta = rng.uniform(-scale * span, scale * span)
        perturbed[key] = min(bounds[1], max(bounds[0], center + delta))
    return perturbed


def _simulate_policy(policy: Dict[str, float], steps: int, rng_seed: int | None = None) -> Dict[str, float] | None:
    model = EconomyModel(seed=rng_seed)
    model.set_tax_rate(policy["tax_rate"])
    model.set_interest_rate(policy["interest_rate"])
    model.set_welfare_payment(policy["welfare"])
    model.set_govt_spending(policy["govt_spending"])

    for _ in range(steps):
        model.step()

    metrics = model.get_current_state()
    if not metrics:
        return None
    return {
        "gdp": float(metrics.get("gdp", 0.0)),
        "unemployment": float(metrics.get("unemployment", 0.0)),
        "inflation": float(metrics.get("inflation", 0.0)),
    }


def _prepare_dataset(num_samples: int, steps: int, rng: random.Random) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int]:
    features: List[List[float]] = []
    gdp_targets: List[float] = []
    unemp_targets: List[float] = []
    infl_targets: List[float] = []
    valid_samples = 0

    for _ in range(num_samples):
        policy = _sample_policy(rng)
        metrics = _simulate_policy(policy, steps, rng_seed=rng.randint(0, 1_000_000))
        if metrics is None:
            continue
        features.append([
            policy["tax_rate"],
            policy["interest_rate"],
            policy["welfare"],
            policy["govt_spending"],
        ])
        gdp_targets.append(metrics["gdp"])
        unemp_targets.append(metrics["unemployment"])
        infl_targets.append(metrics["inflation"])
        valid_samples += 1

    if valid_samples < 10:
        raise RuntimeError("Not enough samples to train policy models")

    X = np.array(features)
    return X, np.array(gdp_targets), np.array(unemp_targets), np.array(infl_targets), valid_samples


def _train_models(X: np.ndarray, y: np.ndarray) -> GradientBoostingRegressor:
    model = GradientBoostingRegressor(
        n_estimators=320,
        learning_rate=0.05,
        max_depth=3,
        random_state=0,
        subsample=0.85,
    )
    model.fit(X, y)
    return model


def _score_candidate(predicted: Dict[str, float], targets: Dict[str, float]) -> float:
    gdp_target = max(targets["gdp"], 1.0)
    gdp_penalty = max(0.0, targets["gdp"] - predicted["gdp"]) / gdp_target
    unemp_diff = abs(predicted["unemployment"] - targets["unemployment"])
    infl_diff = abs(predicted["inflation"] - targets["inflation"])
    # weight unemployment and inflation diffs; GDP penalty is already normalized
    return gdp_penalty + 0.5 * unemp_diff + 0.3 * infl_diff


def recommend_policy(
    target_gdp: float,
    target_unemployment: float,
    target_inflation: float,
    training_samples: int = 60,
    candidate_samples: int = 240,
    steps: int = 25,
) -> PolicyRecommendation:
    rng = random.Random()
    X, y_gdp, y_unemp, y_infl, valid_samples = _prepare_dataset(training_samples, steps, rng)

    gdp_model = _train_models(X, y_gdp)
    unemp_model = _train_models(X, y_unemp)
    infl_model = _train_models(X, y_infl)

    candidates: List[Dict[str, float]] = []
    candidate_matrix: List[List[float]] = []
    for _ in range(candidate_samples):
        policy = _sample_policy(rng)
        candidates.append(policy)
        candidate_matrix.append([
            policy["tax_rate"],
            policy["interest_rate"],
            policy["welfare"],
            policy["govt_spending"],
        ])

    X_candidates = np.array(candidate_matrix)
    pred_gdp = gdp_model.predict(X_candidates)
    pred_unemp = unemp_model.predict(X_candidates)
    pred_infl = infl_model.predict(X_candidates)

    targets = {
        "gdp": target_gdp,
        "unemployment": target_unemployment,
        "inflation": target_inflation,
    }

    feasible_indices = [
        idx for idx in range(len(candidates))
        if pred_gdp[idx] >= target_gdp
        and pred_unemp[idx] <= target_unemployment
        and pred_infl[idx] <= target_inflation
    ]

    if feasible_indices:
        best_idx = min(
            feasible_indices,
            key=lambda idx: _score_candidate(
                {
                    "gdp": pred_gdp[idx],
                    "unemployment": pred_unemp[idx],
                    "inflation": pred_infl[idx],
                },
                targets,
            )
        )
    else:
        best_idx = min(
            range(len(candidates)),
            key=lambda idx: _score_candidate(
                {
                    "gdp": pred_gdp[idx],
                    "unemployment": pred_unemp[idx],
                    "inflation": pred_infl[idx],
                },
                targets,
            )
        )

    best_policy = candidates[best_idx]
    best_predicted = {
        "gdp": float(pred_gdp[best_idx]),
        "unemployment": float(pred_unemp[best_idx]),
        "inflation": float(pred_infl[best_idx]),
    }
    best_score = _score_candidate(best_predicted, targets)

    # Local refinement around best candidate
    for _ in range(100):
        neighbor = _sample_near(best_policy, rng, scale=0.05)
        neighbor_vec = np.array([[neighbor["tax_rate"], neighbor["interest_rate"], neighbor["welfare"], neighbor["govt_spending"]]])
        neighbor_pred = {
            "gdp": float(gdp_model.predict(neighbor_vec)[0]),
            "unemployment": float(unemp_model.predict(neighbor_vec)[0]),
            "inflation": float(infl_model.predict(neighbor_vec)[0]),
        }
        candidate_score = _score_candidate(neighbor_pred, targets)
        if candidate_score < best_score:
            best_policy = neighbor
            best_predicted = neighbor_pred
            best_score = candidate_score

    predicted_metrics = best_predicted

    actual_metrics = _simulate_policy(best_policy, steps=steps * 2, rng_seed=rng.randint(0, 1_000_000))
    if actual_metrics is None:
        actual_metrics = predicted_metrics.copy()

    note = None
    if not feasible_indices:
        note = "Could not meet all targets exactly; showing closest match."
    else:
        for metric in ("gdp", "unemployment", "inflation"):
            if metric not in targets:
                continue
            if metric == "gdp" and actual_metrics[metric] < targets[metric]:
                note = "Actual simulation under-delivers on GDP; consider manual tuning."
                break
            if metric != "gdp" and actual_metrics[metric] > targets[metric]:
                note = "Actual simulation exceeds target bounds; consider manual tuning."
                break

    return PolicyRecommendation(
        policy=best_policy,
        predicted=predicted_metrics,
        actual={k: float(v) for k, v in actual_metrics.items()},
        samples_used=valid_samples,
        notes=note,
    )
