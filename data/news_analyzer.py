"""
AI-powered analysis of economic policy news using Azure OpenAI
"""

from __future__ import annotations

import json
import logging
import os
from typing import Dict, Optional
from urllib.parse import urlparse, parse_qs

import requests
from dotenv import load_dotenv

from data.news_client import NewsArticle

# Load environment variables
load_dotenv()

LOGGER = logging.getLogger(__name__)


class NewsAnalyzer:
    """Analyzes economic news articles using Azure OpenAI"""

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
                "Azure OpenAI credentials missing. News analysis will use fallback mode."
            )

    @property
    def enabled(self) -> bool:
        return self._enabled

    def analyze_article(self, article: NewsArticle) -> Dict:
        """
        Analyze a news article for policy impact and simulation parameters

        Returns:
            Dict with keys: sentiment, policy_type, impact, suggested_params, summary
        """
        if not self.enabled:
            return self._fallback_analysis(article)

        prompt = self._build_analysis_prompt(article)

        try:
            response = self._call_azure(prompt)
            analysis = self._extract_analysis(response)
            if analysis:
                return analysis
            LOGGER.warning("Azure returned empty analysis; using fallback")
        except Exception as exc:
            LOGGER.warning("AI news analysis failed: %s", exc, exc_info=True)

        return self._fallback_analysis(article)

    def _build_analysis_prompt(self, article: NewsArticle) -> str:
        """Build analysis prompt for Azure OpenAI"""
        return f"""You are an expert economist analyzing policy news for an economic simulation model.

Analyze this news article and provide structured analysis:

TITLE: {article.title}
DESCRIPTION: {article.description}
CONTENT: {article.content or article.description}

Provide analysis in this exact JSON format:
{{
    "policy_type": "monetary" or "fiscal" or "mixed" or "indicator",
    "sentiment": number between -1.0 (very contractionary) to +1.0 (very expansionary),
    "impact": {{
        "gdp_growth": "positive/negative/neutral",
        "inflation": "increase/decrease/neutral",
        "unemployment": "increase/decrease/neutral"
    }},
    "suggested_params": {{
        "interest_rate": number or null (range 0-10, as percentage),
        "govt_spending": number or null (range 0-50000),
        "welfare_payment": number or null (range 0-2000),
        "tax_rate": number or null (range 0-50, as percentage)
    }},
    "summary": "One sentence summary of policy impact (max 100 words)",
    "confidence": number between 0-1 indicating analysis confidence
}}

Be specific about parameter values. If the news mentions:
- Interest rate changes: suggest exact rate
- Government spending: scale to simulation ($0-50k range)
- Tax changes: suggest tax rate percentage
- If no specific policy change, use null for suggested_params

Return ONLY valid JSON, no other text."""

    def _call_azure(self, prompt: str) -> dict:
        """Call Azure OpenAI API"""
        if self._api_kind == "openai":
            url = f"{self._endpoint}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}",
            }
        else:
            url = (
                f"{self._endpoint}/openai/deployments/{self._deployment}/"
                f"chat/completions?api-version={self._api_version}"
            )
            headers = {
                "Content-Type": "application/json",
                "api-key": self._api_key,
            }

        body = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert economist providing structured policy analysis in JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 500,
        }

        response = requests.post(url, headers=headers, json=body, timeout=30)
        response.raise_for_status()
        return response.json()

    def _extract_analysis(self, response: dict) -> Optional[Dict]:
        """Extract analysis from Azure response"""
        try:
            content = response["choices"][0]["message"]["content"]
            # Try to parse JSON from response
            # Sometimes AI adds markdown code blocks, so clean it
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            analysis = json.loads(content)
            return analysis
        except (KeyError, json.JSONDecodeError, IndexError) as e:
            LOGGER.error(f"Failed to parse Azure response: {e}")
            return None

    def _fallback_analysis(self, article: NewsArticle) -> Dict:
        """Provide simple heuristic-based analysis when AI is unavailable"""
        title_lower = article.title.lower()
        desc_lower = (article.description or "").lower()
        text = title_lower + " " + desc_lower

        # Detect policy type
        policy_type = "indicator"
        if any(word in text for word in ["interest rate", "fed", "federal reserve", "monetary"]):
            policy_type = "monetary"
        elif any(word in text for word in ["spending", "tax", "fiscal", "budget"]):
            policy_type = "fiscal"

        # Simple sentiment detection
        sentiment = 0.0
        if any(word in text for word in ["raise", "hike", "increase", "tighten"]):
            sentiment = -0.3  # Contractionary
        elif any(word in text for word in ["cut", "lower", "reduce", "ease"]):
            sentiment = 0.3  # Expansionary

        # Suggest parameters based on keywords
        suggested_params = {
            "interest_rate": None,
            "govt_spending": None,
            "welfare_payment": None,
            "tax_rate": None
        }

        if "interest rate" in text or "fed" in text:
            if "raise" in text or "hike" in text:
                suggested_params["interest_rate"] = 6.0
            elif "cut" in text or "lower" in text:
                suggested_params["interest_rate"] = 4.0

        if "spending" in text and "infrastructure" in text:
            suggested_params["govt_spending"] = 8000

        return {
            "policy_type": policy_type,
            "sentiment": sentiment,
            "impact": {
                "gdp_growth": "neutral",
                "inflation": "neutral",
                "unemployment": "neutral"
            },
            "suggested_params": suggested_params,
            "summary": f"Policy news regarding {policy_type} policy. " +
                      ("AI analysis unavailable - showing simplified analysis." if not self.enabled else ""),
            "confidence": 0.5 if not self.enabled else 0.7
        }

    def _normalize_config(self) -> None:
        """Normalize Azure endpoint configuration"""
        if self._api_kind == "openai":
            return

        if self._endpoint and "/openai/deployments/" in self._endpoint:
            parts = urlparse(self._endpoint)
            base = f"{parts.scheme}://{parts.netloc}"
            path_segments = parts.path.split("/")
            try:
                dep_idx = path_segments.index("deployments") + 1
                if dep_idx < len(path_segments):
                    self._deployment = path_segments[dep_idx]
            except (ValueError, IndexError):
                pass
            query_params = parse_qs(parts.query)
            if "api-version" in query_params:
                self._api_version = query_params["api-version"][0]
            self._endpoint = base


def get_news_analyzer() -> NewsAnalyzer:
    """Factory function to create a NewsAnalyzer instance"""
    return NewsAnalyzer()
