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
    # MARKET-SPECIFIC NARRATIVES (HACKATHON FEATURE!)
    # ------------------------------------------------------------------

    def generate_market_narrative(self, event_type: str, current: Mapping[str, Any], history: Mapping[str, Sequence[float]]) -> str:
        """
        Generate narrative for financial market events

        Args:
            event_type: Type of market event (crypto_crash, stock_rally, etc.)
            current: Current metrics including market data
            history: Historical metrics

        Returns:
            Narrative string
        """
        if not self.enabled:
            return self._market_fallback(event_type, current)

        prompt = self._build_market_prompt(event_type, current, history)
        try:
            response = self._call_azure(prompt)
            text = self._extract_content(response)
            if text:
                return text.strip()
            LOGGER.warning("Azure returned empty market narrative; using fallback")
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("Market narrative generation failed: %s", exc, exc_info=True)
        return self._market_fallback(event_type, current)

    def _build_market_prompt(self, event_type: str, current: Mapping[str, Any], history: Mapping[str, Sequence[float]]) -> str:
        """
        Build prompt for market-specific narratives

        Args:
            event_type: Market event type
            current: Current metrics
            history: Historical data

        Returns:
            Prompt string for AI
        """
        # Common economic context
        inflation = current.get("inflation_rate", 0.02) * 100
        interest_rate = current.get("interest_rate", 0.03) * 100
        unemployment = current.get("unemployment_rate", 0.05) * 100

        # Market-specific data
        crypto_price = current.get("crypto_price", 50000)
        stock_index = current.get("stock_index", 100)
        crypto_adoption = current.get("crypto_adoption_rate", 0.01) * 100
        govt_reserve = current.get("govt_crypto_reserve_value", 0)

        if event_type == "crypto_crash":
            crypto_change = current.get("crypto_price_change", -50)
            return (
                f"Write a 2-sentence economic news headline about a {abs(crypto_change):.0f}% cryptocurrency crash. "
                f"Context: Crypto price fell to ${crypto_price:,.0f}. "
                f"Macro environment: {inflation:.1f}% inflation, {interest_rate:.1f}% interest rates. "
                f"Explain how high interest rates or regulatory concerns might be causing the crash. "
                f"Keep it dramatic but professional, like Bloomberg or WSJ."
            )

        elif event_type == "crypto_rally":
            crypto_change = current.get("crypto_price_change", 30)
            return (
                f"Write a 2-sentence economic news headline about a {crypto_change:.0f}% cryptocurrency rally. "
                f"Context: Crypto surged to ${crypto_price:,.0f}, {crypto_adoption:.1f}% population adoption. "
                f"Macro environment: {inflation:.1f}% inflation (inflation hedge narrative). "
                f"Mention institutional adoption, inflation hedge narrative, or regulatory approval. "
                f"Keep it exciting but professional."
            )

        elif event_type == "stock_crash":
            stock_change = current.get("stock_daily_return", -30) * 100
            return (
                f"Write a 2-sentence economic news headline about a {abs(stock_change):.0f}% stock market crash. "
                f"Context: Market index fell to {stock_index:.2f}, {interest_rate:.1f}% interest rates. "
                f"Explain risk-off sentiment, rate fears, or recession concerns. "
                f"Professional tone like Financial Times."
            )

        elif event_type == "stock_rally":
            stock_change = current.get("stock_daily_return", 10) * 100
            return (
                f"Write a 2-sentence economic news headline about a {stock_change:.0f}% stock market rally. "
                f"Context: Market index rose to {stock_index:.2f}. "
                f"Macro: {unemployment:.1f}% unemployment, strong economy. "
                f"Mention earnings growth, low unemployment, or optimism. "
                f"Upbeat but professional tone."
            )

        elif event_type == "govt_crypto_purchase":
            return (
                f"Write a 2-sentence breaking news headline about government establishing strategic cryptocurrency reserve. "
                f"Context: Government now holds ${govt_reserve:,.0f} in crypto. "
                f"THIS IS A MAJOR NARRATIVE EVENT - like US Treasury Bitcoin proposal. "
                f"Emphasize legitimacy, institutional adoption, and market impact. "
                f"Dramatic tone like breaking news."
            )

        elif event_type == "crypto_adoption_surge":
            return (
                f"Write a 2-sentence news headline about cryptocurrency adoption surge. "
                f"Context: {crypto_adoption:.1f}% of population now holds crypto, price ${crypto_price:,.0f}. "
                f"High inflation ({inflation:.1f}%) driving adoption as inflation hedge. "
                f"Network effects and mainstream acceptance theme."
            )

        else:
            # Generic market update
            return (
                f"Write a 2-sentence financial markets update. "
                f"Stock index: {stock_index:.2f}, Crypto: ${crypto_price:,.0f}. "
                f"Macro: {inflation:.1f}% inflation, {interest_rate:.1f}% rates. "
                f"Professional summary of current market conditions."
            )

    def _market_fallback(self, event_type: str, current: Mapping[str, Any]) -> str:
        """
        Fallback narratives when AI is unavailable

        Args:
            event_type: Market event type
            current: Current metrics

        Returns:
            Simple narrative string
        """
        crypto_price = current.get("crypto_price", 50000)
        stock_index = current.get("stock_index", 100)
        inflation = current.get("inflation_rate", 0.02) * 100
        interest_rate = current.get("interest_rate", 0.03) * 100

        if event_type == "crypto_crash":
            return (
                f"Cryptocurrency markets plunge as prices fall to ${crypto_price:,.0f}. "
                f"Analysts cite {interest_rate:.1f}% interest rates and regulatory concerns as risk-off sentiment spreads."
            )

        elif event_type == "crypto_rally":
            return (
                f"Cryptocurrency surges to ${crypto_price:,.0f} as inflation hedge narrative gains traction. "
                f"With inflation at {inflation:.1f}%, investors flock to digital assets seeking protection."
            )

        elif event_type == "stock_crash":
            return (
                f"Stock markets tumble with index falling to {stock_index:.2f} on rate fears. "
                f"The {interest_rate:.1f}% interest rate is weighing on equity valuations as investors turn cautious."
            )

        elif event_type == "stock_rally":
            return (
                f"Stocks rally with market index climbing to {stock_index:.2f} on economic optimism. "
                f"Strong fundamentals and investor confidence drive broad-based gains across sectors."
            )

        elif event_type == "govt_crypto_purchase":
            govt_reserve = current.get("govt_crypto_reserve_value", 0)
            return (
                f"BREAKING: Government establishes strategic cryptocurrency reserve worth ${govt_reserve:,.0f}. "
                f"Historic move legitimizes digital assets and signals mainstream institutional adoption."
            )

        elif event_type == "crypto_adoption_surge":
            adoption = current.get("crypto_adoption_rate", 0.01) * 100
            return (
                f"Cryptocurrency adoption soars to {adoption:.1f}% of population as inflation concerns drive interest. "
                f"Network effects accelerate as digital currency enters mainstream consciousness."
            )

        else:
            return (
                f"Financial markets update: Stock index at {stock_index:.2f}, cryptocurrency trading at ${crypto_price:,.0f}. "
                f"Markets respond to {inflation:.1f}% inflation and {interest_rate:.1f}% policy rate environment."
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
