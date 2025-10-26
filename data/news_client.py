"""
Client for fetching economic policy news from various sources
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class NewsArticle:
    """Represents a single news article"""
    title: str
    description: str
    url: str
    published_at: str
    source: str
    content: Optional[str] = None


class NewsClient:
    """Fetches economic policy news from NewsAPI"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2/everything"

    def fetch_economic_policy_news(
        self,
        days_back: int = 7,
        max_articles: int = 10
    ) -> List[NewsArticle]:
        """
        Fetch recent economic policy news

        Args:
            days_back: How many days back to search
            max_articles: Maximum number of articles to return

        Returns:
            List of NewsArticle objects
        """
        # If no API key, return sample data
        if not self.api_key:
            return self._get_sample_news()

        try:
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days_back)

            # Economic policy keywords
            query = (
                '("interest rate" OR "federal reserve" OR "central bank" OR '
                '"fiscal policy" OR "monetary policy" OR "inflation" OR '
                '"GDP" OR "unemployment" OR "economic policy")'
            )

            params = {
                'q': query,
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d'),
                'language': 'en',
                'sortBy': 'relevancy',
                'pageSize': max_articles,
                'apiKey': self.api_key
            }

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('status') != 'ok':
                return self._get_sample_news()

            articles = []
            for article in data.get('articles', []):
                articles.append(NewsArticle(
                    title=article.get('title', 'No title'),
                    description=article.get('description', ''),
                    url=article.get('url', ''),
                    published_at=article.get('publishedAt', ''),
                    source=article.get('source', {}).get('name', 'Unknown'),
                    content=article.get('content', '')
                ))

            return articles

        except Exception as e:
            print(f"Error fetching news: {e}")
            return self._get_sample_news()

    def _get_sample_news(self) -> List[NewsArticle]:
        """Return sample news articles when API is unavailable"""
        return [
            NewsArticle(
                title="Federal Reserve Holds Interest Rates Steady at 5.25-5.50%",
                description="The Federal Reserve maintained its benchmark interest rate, signaling a cautious approach to inflation management while monitoring economic data.",
                url="https://www.federalreserve.gov",
                published_at=datetime.now().isoformat(),
                source="Federal Reserve",
                content="The Federal Reserve announced it will hold interest rates at the current 5.25-5.50% range, citing progress on inflation but concerns about economic growth."
            ),
            NewsArticle(
                title="US Unemployment Rate Falls to 3.7%, Labor Market Remains Strong",
                description="Latest jobs report shows continued strength in the labor market with unemployment ticking down and steady wage growth.",
                url="https://www.bls.gov",
                published_at=(datetime.now() - timedelta(days=2)).isoformat(),
                source="Bureau of Labor Statistics",
                content="The unemployment rate dropped to 3.7% in the latest report, with the economy adding 180,000 jobs. Wage growth remains at 4.2% year-over-year."
            ),
            NewsArticle(
                title="Inflation Moderates to 3.2%, Still Above Fed Target",
                description="Consumer prices rose 3.2% annually, showing continued moderation but remaining above the Federal Reserve's 2% target.",
                url="https://www.bls.gov",
                published_at=(datetime.now() - timedelta(days=3)).isoformat(),
                source="Bureau of Labor Statistics",
                content="CPI data shows inflation cooling to 3.2% year-over-year, down from 3.7% last month. Core inflation remains sticky at 4.0%."
            ),
            NewsArticle(
                title="Congress Debates $1.5T Infrastructure Investment Package",
                description="Lawmakers consider major infrastructure spending bill that could boost economic growth but raise deficit concerns.",
                url="https://www.congress.gov",
                published_at=(datetime.now() - timedelta(days=5)).isoformat(),
                source="Congressional Budget Office",
                content="A bipartisan infrastructure bill proposing $1.5 trillion in spending over 10 years is under consideration, focusing on roads, bridges, and clean energy."
            ),
            NewsArticle(
                title="ECB Signals Potential Rate Cuts in 2024",
                description="European Central Bank hints at possible monetary easing as eurozone inflation shows signs of sustained decline.",
                url="https://www.ecb.europa.eu",
                published_at=(datetime.now() - timedelta(days=6)).isoformat(),
                source="European Central Bank",
                content="ECB President Christine Lagarde suggested that interest rate cuts could be on the table in 2024 if inflation continues its downward trajectory."
            ),
        ]


def get_news_client() -> NewsClient:
    """Factory function to create a NewsClient instance"""
    return NewsClient()
