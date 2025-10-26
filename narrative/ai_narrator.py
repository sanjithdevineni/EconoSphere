"""Generate short economic news summaries using Azure OpenAI."""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Mapping, Optional, Sequence
from urllib.parse import urlparse, parse_qs

import requests

LOGGER = logging.getLogger(__name__)


class AINarrator:
    """Wrapper around Azure OpenAI that produces short economic headlines."""

    def __init__(self) -> None:
        self._endpoint = (os.getenv("AZURE_OPENAI_ENDPOINT") or "").strip()
        self._deployment = (os.getenv("AZURE_OPENAI_DEPLOYMENT") or "").strip()
        self._api_version = (os.getenv("AZURE_OPENAI_API_VERSION") or "2024-02-15-preview").strip()
        self._api_key = (os.getenv("AZURE_OPENAI_API_KEY") or "").strip()
        self._api_kind: Optional[str] = (os.getenv("AZURE_OPENAI_API_KIND") or "").strip().lower() or None

        self._normalize_config()
        self._enabled = bool(self._endpoint and self._deployment and self._api_version and self._api_key)

        if not self._enabled:
            LOGGER.warning(
                "Azure OpenAI credentials are missing (endpoint/deployment/api key). "
                "Set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and optionally AZURE_OPENAI_DEPLOYMENT/"
                "AZURE_OPENAI_API_VERSION."
            )

    @property
    def enabled(self) -> bool:
        return self._enabled

    def generate(self, current: Mapping[str, Any], history: Mapping[ str, Sequence[float]]) -> str:
        """Create a short narrative describing the current macro state."""
        if not self.enabled:
            return self._fallback(current, history)

        prompt = self._build_prompt(current, history)
        try:
            response = self._call_azure(prompt)
            text = self._extract_content(response)
            if text:
                return text.strip()
            LOGGER.warning("Azure returned an empty narrative; using fallback copy")
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("AI narrative generation failed: %s", exc, exc_info=True)
        return self._fallback(current, history)

    # ------------------------------------------------------------------
    # Azure helpers
    # ------------------------------------------------------------------

    def _normalize_config(self) -> None:
        """Support full endpoint URLs and infer API mode when possible."""
        if not self._endpoint:
            return

        parsed = urlparse(self._endpoint)
        # If the endpoint already contains /openai/deployments/<name>, pull out settings
        if parsed.path and "openai" in parsed.path and "deployments" in parsed.path:
            segments = [seg for seg in parsed.path.split("/") if seg]
            if not self._deployment:
                try:
                    idx = segments.index("deployments") + 1
                    self._deployment = segments[idx]
                except (ValueError, IndexError):
                    pass
            if parsed.query and not self._api_version:
                params = parse_qs(parsed.query)
                version = params.get("api-version")
                if version:
                    self._api_version = version[0]
            base = f"{parsed.scheme}://{parsed.netloc}"
            self._endpoint = base.rstrip("/")
        else:
            self._endpoint = parsed.geturl().rstrip("/")

        # Auto-detect API kind if not provided
        if not self._api_kind:
            dep = self._deployment.lower()
            if "gpt-4.1" in dep or "responses" in dep:
                self._api_kind = "responses"
            else:
                self._api_kind = "chat"

    def _call_azure(self, prompt: str) -> Dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "api-key": self._api_key,
        }

        if self._api_kind == "responses":
            url = f"{self._endpoint}/openai/deployments/{self._deployment}/responses?api-version={self._api_version}"
            payload = {
                "input": [
                    {
                        "role": "system",
                        "content": [
                            {"type": "text", "text": "You are a financial news assistant. Summarize economic data succinctly."}
                        ],
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt}
                        ],
                    },
                ]
            }
        else:
            url = f"{self._endpoint}/openai/deployments/{self._deployment}/chat/completions?expression-version={self._api_version}"
            payload = {
                "messages": [
                    {"role": "system", "content": "You are a financial news assistant. Summarize economic indicators."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.7,
                "max_tokens": 120,
            }

        LOGGER.debug("Requesting Azure OpenAI narrative via %s", url)
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=15)
        response.raise_for_status()
        return response.json()

    def _extract_content(self, response: Dict[str, Any]) -> str:
        # Responses API structure
        if "output" in response:
            for chunk in response.get("output", []):
                if not isinstance(chunk, dict):
                    continue
                for item in chunk.get("content", []):
                    if isinstance(item, dict) and item.get("type") == "text":
                        text = item.get("text")
                        if text:
                            return text
            return ""

        # Chat completions structure
        choices = response.get("choices") or []
        if not choices:
            return ""
        message = choices[0].get("message") or {}
        return str(message.get("content", ""))

    # ------------------------------------------------------------------
    # Prompt building and fallback
    # ------------------------------------------------------------------

    def _build_prompt(self, current: Mapping[str, Any], history: Mapping[str, Sequence[float]]) -> str:
        gdp = current.get("gdp", 0.0)
        unemployment = current.get("unemployment", 0.0)
        inflation = current.get("inflation", 0.0)
        interest = current.get("interest_rate", 0.0)
        budget = current.get("budget_balance", 0.0)

        prev_gdp = self._previous(history.get("gdp"))
        prev_unemp = self._previous(history.get("unemployment"))
        prev_infl = self._previous(history.get("inflation"))

        # Calculate changes as strings for display
        gdp_change = self._percentage(prev_gdp, gdp)

        # Calculate raw changes for direction (as floats)
        unemp_raw_change = (unemployment - prev_unemp) if prev_unemp is not None else None
        infl_raw_change = (inflation - prev_infl) if prev_infl is not None else None

        parts = [
            f"Latest data: GDP ${gdp:,.0f}; unemployment {unemployment:.1f}%; inflation {inflation:.2f}%; policy rate {interest:.2f}%.",
            f"Government balance: ${budget:,.0f}.",
            f"Since last period: GDP {gdp_change}, employment {self._direction(unemp_raw_change, invert=True)}, "
            f"inflation {self._direction(infl_raw_change)}.",
        ]
        return " ".join(parts)

    def _fallback(self, current: Mapping[str, Any], history: Mapping[str, Sequence[float]]) -> str:
        gdp = current.get("gdp", 0.0)
        unemployment = current.get("unemployment", 0.0)
        inflation = current.get("inflation", 0.0)
        return (
            f"GDP is approximately ${gdp:,.0f} with unemployment near {unemployment:.1f}% and inflation around {inflation:.2f}%. "
            "Policymakers are monitoring conditions closely."
        )

    # ------------------------------------------------------------------
    # Utility formatting helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _previous(series: Optional[Sequence[float]]) -> Optional[float]:
        if series and len(series) >= 1:
            return series[-1]
        return None

    @staticmethod
    def _percentage(previous: Optional[float], current: float) -> str:
        if previous is None or previous == 0:
            return "steady"
        change = ((current - previous) / abs(previous)) * 100
        sign = "up" if change > 0 else "down"
        return f"{sign} {abs(change):.1f}%"

    @staticmethod
    def _direction(change: Optional[float], invert: bool = False) -> str:
        if change is None:
            return "steady"
        direction_positive = change > 0
        if invert:
            direction_positive = not direction_positive
        word = "higher" if direction_positive else "lower"
        magnitude = abs(change)
        if magnitude < 0.1:
            qualifier = "slightly "
        elif magnitude > 2:
            qualifier = "sharply "
        else:
            qualifier = ""
        return f"{qualifier}{word}"
