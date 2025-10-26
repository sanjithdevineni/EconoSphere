"""
Test script to debug NewsAPI connection
"""

import os
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_newsapi():
    """Test NewsAPI connection with detailed debugging"""

    api_key = os.getenv('NEWS_API_KEY')

    print("=" * 60)
    print("NewsAPI Connection Test")
    print("=" * 60)
    print()

    # Check if API key exists
    print(f"1. API Key Check:")
    if api_key:
        print(f"   [OK] API key found: {api_key[:10]}...{api_key[-4:]}")
    else:
        print(f"   [FAIL] API key NOT found in environment")
        print(f"   Available env vars: {list(os.environ.keys())}")
        return

    print()

    # Test API endpoint
    print(f"2. Testing NewsAPI Endpoint:")

    base_url = "https://newsapi.org/v2/everything"

    # Calculate date range
    to_date = datetime.now()
    from_date = to_date - timedelta(days=7)

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
        'pageSize': 5,
        'apiKey': api_key
    }

    print(f"   URL: {base_url}")
    print(f"   Query: {query[:50]}...")
    print(f"   Date Range: {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}")
    print()

    try:
        print(f"3. Making API Request...")
        response = requests.get(base_url, params=params, timeout=10)

        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        print()

        # Check if request was successful
        response.raise_for_status()

        # Parse JSON
        data = response.json()

        print(f"4. API Response:")
        print(f"   Status: {data.get('status')}")
        print(f"   Total Results: {data.get('totalResults', 0)}")
        print()

        # Check for errors
        if data.get('status') != 'ok':
            print(f"   [ERROR] API Error!")
            print(f"   Error Code: {data.get('code')}")
            print(f"   Error Message: {data.get('message')}")
            print()

            # Common error codes
            if data.get('code') == 'apiKeyInvalid':
                print("   [TIP] Solution: Your API key is invalid. Check if it's correct.")
            elif data.get('code') == 'rateLimited':
                print("   [TIP] Solution: You've hit the rate limit. Wait or upgrade plan.")
            elif data.get('code') == 'apiKeyDisabled':
                print("   [TIP] Solution: Your API key is disabled. Check NewsAPI dashboard.")

            return

        # Display articles
        articles = data.get('articles', [])

        if not articles:
            print(f"   [WARNING] No articles found!")
            print(f"   This might mean:")
            print(f"   - No matching news in the last 7 days")
            print(f"   - Try broader search terms")
            return

        print(f"5. Articles Found: {len(articles)}")
        print()

        for idx, article in enumerate(articles[:5], 1):
            print(f"   Article {idx}:")
            print(f"   Title: {article.get('title', 'No title')}")
            print(f"   Source: {article.get('source', {}).get('name', 'Unknown')}")
            print(f"   Published: {article.get('publishedAt', 'Unknown')}")
            print(f"   URL: {article.get('url', 'No URL')[:60]}...")
            print()

        print("=" * 60)
        print("[SUCCESS] NewsAPI is working correctly!")
        print("=" * 60)

    except requests.exceptions.HTTPError as e:
        print(f"   [FAIL] HTTP Error: {e}")
        print(f"   Response Text: {response.text}")

    except requests.exceptions.Timeout:
        print(f"   [FAIL] Request timed out")
        print(f"   Solution: Check your internet connection")

    except requests.exceptions.RequestException as e:
        print(f"   [FAIL] Request failed: {e}")

    except Exception as e:
        print(f"   [FAIL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_newsapi()
