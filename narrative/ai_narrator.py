"""Generate short economic narratives using Azure OpenAI (optional)."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Mapping, Sequence
from urllib.parse import parse_qs, urlparse

import requests
from dotenv import load_dotenv

load_dotenv()

LOGGER = logging.getLogger(__name__)


class AINarrator:
    """Lightweight helper that calls Azure OpenAI to craft news-style blurbs."""

    def __init__(self) -> None:
        self.endpoint = (os.getenv("AZURE_OPENAI_ENDPOINT") or "").strip()
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment = (os.getenv("AZURE_OPENAI_DEPLOYMENT") or "").strip()
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self._normalize_config()
        self._enabled = bool(self.endpoint and self.api_key and self.deployment)
        if not self._enabled:
            LOGGER.debug("AI narrator disabled (missing Azure OpenAI configuration)")

    def _normalize_config(self) -> None:
        """Allow combined Azure URL input by extracting deployment and API version."""
        if not self.endpoint:
            return
        combined = self.endpoint.strip()
        if (not self.deployment) and "/deployments/" in combined:
            parsed = urlparse(combined)
            path_parts = [part for part in parsed.path.split("/") if part]
            if "deployments" in path_parts:
                idx = path_parts.index("deployments")
                if idx + 1 < len(path_parts):
                    self.deployment = self.deployment or path_parts[idx + 1]
            if parsed.query and not self.api_version:
                params = parse_qs(parsed.query)
                version = params.get("api-version")
                if version:
                    self.api_version = version[0]
            self.endpoint = f"{parsed.scheme}://{parsed.netloc}"
        else:
            self.endpoint = combined.rstrip("/")

    @property
    def enabled(self) -> bool:
        return self._enabled

    def generate(self, current: Mapping[str, Any], history: Mapping[str, Sequence[float]]) -> str:
        """Return a short narrative for the current step."""
        if not self.enabled:
            return self._fallback(current, history)

        try:
            prompt = self._build_prompt(current, history)
            response = self._call_azure(prompt)
            content = self._extract_content(response)
            if content:
                return content.strip()
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("AI narrative generation failed: %s", exc, exc_info=True)

        return self._fallback(current, history)

    def _call_azure(self, prompt: str) -> Dict[str, Any]:
        url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions"
        params = {"api-version": self.api_version}
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key,
        }
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an economic journalist for a real-time markets news feed. "
                        "Write two short, vivid sentences: the first on business activity "
                        "(growth, firms, demand); the second on policy or sentiment."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0.7,
            "max_tokens": 120,
        }
        response = requests.post(url, params=params, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _extract_content(response: Dict[str, Any]) -> str:
        try:
            choices = response.get("choices") or []
            if not choices:
                return ""
            message = choices[0].get("message") or {}
            return str(message.get("content", "")).strip()
        except Exception:  # noqa: BLE001
            return ""

    def _build_prompt(self, current: Mapping[str, Any], history: Mapping[str, Sequence[float]]) -> str:
        gdp = current.get("gdp", 0.0)
        unemployment = current.get("unemployment", 0.0)
        inflation = current.get("inflation", 0.0)
        interest = current.get("interest_rate", 0.0)
        budget = current.get("budget_balance", 0.0)

        prev_gdp = self._previous(history.get("gdp"))
        prev_unemp = self._previous(history.get("unemployment"))
        prev_infl = self._previous(history.get("inflation"))

        gdp_change = self._percent_change(prev_gdp, gdp)
        unemp_change = self._percentage_point_change(prev_unemp, unemployment)
        infl_change = self._percentage_point_change(prev_infl, inflation)

        direction_gdp = self._describe_change(gdp_change, "growth")
        direction_jobs = self._describe_change(unemp_change, "jobs", inverse=True)
        direction_prices = self._describe_change(infl_change, "inflation")

        prompt = f"Latest data: GDP ${gdp:,.0f}, unemployment {unemployment:.1f}%, inflation {inflation:.2f}%, policy rate {interest:.2f}%."
        prompt += f" Budget balance is {budget:,.0f}. "
        prompt += (
            "Compare against the prior step. Highlight the most notable move using press-style framing. "
            "Summaries must fit in two sentences and feel like a market-news alert."
        )
        prompt += f" GDP trend: {direction_gdp}. Labour trend: {direction_jobs}. Price trend: {direction_prices}."
        return prompt

    @staticmethod
    def _previous(series: Sequence[float] | None) -> float | None:
        if series and len(series) >= 2:
            return series[-2]
        return None

    @staticmethod
    def _percent_change(previous: float | None, current: float) -> float | None:
        if previous is None or previous == 0:
            return None
        return (current - previous) / previous * 100.0


    @staticmethod
    def _percentage_point_change(previous: float | None, current: float) -> float | None:
        if previous is None:
            return None
        return current - previous

    @staticmethod
    def _describe_change(change: float | None, label: str, inverse: bool = False) -> str:
        if change is None:
            return f"{label} steady"
        magnitude = abs(change)
        if magnitude < 0.2:
            qualifier = "steady"
        elif magnitude < 1.0:
            qualifier = "edging"
        elif magnitude < 3.0:
            qualifier = "moving"
        else:
            qualifier = "surging" if (change > 0) ^ inverse else "sliding"
        direction = "higher" if (change > 0) ^ inverse else "lower"
        if qualifier == "steady":
            return f"{label} steady"
        return f"{label} {qualifier} {direction}"

    @staticmethod
    def _fallback(current: Mapping[str, Any], history: Mapping[str, Sequence[float]]) -> str:
        gdp = current.get("gdp", 0.0)
        unemployment = current.get("unemployment", 0.0)
        inflation = current.get("inflation", 0.0)
        interest = current.get("interest_rate", 0.0)
        prev_unemployment = AINarrator._previous(history.get("unemployment"))
        jobs_direction = "holds" if prev_unemployment is None else (
            "eases" if unemployment < prev_unemployment else "ticks up"
        )
        lines = [
            f"Firms navigate a GDP print near ${gdp:,.0f} as unemployment {jobs_direction} to {unemployment:.1f}%.",
            f"The central bank keeps policy at {interest:.2f}% while inflation runs {inflation:.2f}%.",
        ]
        return ' '.join(lines)

