# 📰 News Insights Feature

## Overview

The **News Insights** page fetches real-time economic policy news and uses AI to analyze potential impacts on the economy. You can then simulate these policies in your model with one click!

## Features

✅ **Real-time News Fetching** - Latest economic policy headlines from NewsAPI
✅ **AI-Powered Analysis** - Azure OpenAI analyzes sentiment, policy type, and impact
✅ **One-Click Simulation** - Automatically set parameters based on news
✅ **Impact Predictions** - See expected effects on GDP, inflation, unemployment
✅ **Smart Categorization** - Monetary policy, fiscal policy, or economic indicators

## How to Use

### 1. Navigate to News Insights
Click **"News Insights"** in the navigation bar

### 2. Adjust Timeframe (Optional)
- Last 24 hours
- Last 3 days
- Last week (default)
- Last 2 weeks

### 3. Refresh News
Click **"🔄 Refresh News"** to fetch latest articles

### 4. Review AI Analysis
Each article shows:
- **Policy Type**: Monetary, Fiscal, Mixed, or Indicator
- **Sentiment**: Expansionary 📈, Contractionary 📉, or Neutral ➡️
- **AI Summary**: One-sentence impact analysis
- **Expected Impact**: Effects on GDP, inflation, unemployment
- **Suggested Parameters**: Specific simulation settings

### 5. Simulate Policy (Optional)
Click **"▶️ Simulate This Policy"** to run the scenario
- Automatically sets interest rate, govt spending, taxes, etc.
- Navigate to Simulation page to see results

## Configuration

### NewsAPI Key (Optional)

The feature works **without an API key** using sample news data.

For **live news**, get a free API key:

1. Go to https://newsapi.org/register
2. Sign up for free (100 requests/day)
3. Copy your API key
4. Add to `.env` file:
   ```bash
   NEWS_API_KEY="your_api_key_here"
   ```

### Azure OpenAI (Required for AI Analysis)

Already configured in your `.env`:
- **AZURE_OPENAI_ENDPOINT**
- **AZURE_OPENAI_API_KEY**
- **AZURE_OPENAI_DEPLOYMENT**

If AI analysis fails, fallback heuristic analysis is used.

## Sample News Sources

Without API key, you'll see curated sample articles about:
- Federal Reserve interest rate decisions
- Unemployment & jobs reports
- Inflation data (CPI)
- Congressional spending bills
- ECB policy signals

## How AI Analysis Works

Azure OpenAI analyzes each article for:

| Analysis Field | Description | Values |
|----------------|-------------|---------|
| **Policy Type** | Category of policy | Monetary, Fiscal, Mixed, Indicator |
| **Sentiment** | Expansionary vs Contractionary | -1.0 to +1.0 |
| **GDP Impact** | Expected GDP growth effect | Positive/Negative/Neutral |
| **Inflation Impact** | Expected price level effect | Increase/Decrease/Neutral |
| **Unemployment Impact** | Expected jobs effect | Increase/Decrease/Neutral |
| **Suggested Parameters** | Simulation settings | Interest rate, spending, taxes |
| **Confidence** | AI certainty | 0% to 100% |

## Example Workflow

**Scenario**: Fed raises rates by 0.75%

1. News article appears: "Federal Reserve Hikes Rates to Combat Inflation"
2. AI analyzes:
   - Policy Type: **Monetary**
   - Sentiment: **Contractionary (-0.7)**
   - Impact: GDP↓, Inflation↓, Unemployment↑
   - Suggested: Interest Rate → **6.0%**
3. Click **"Simulate This Policy"**
4. Model runs with 6% interest rate
5. Compare results to AI predictions

## Limitations

⚠️ **Free API Constraints**
- 100 requests/day on free tier
- News updates daily (cached to avoid spam)

⚠️ **AI Analysis**
- Based on article text, not full economic context
- Confidence scores indicate uncertainty
- Always verify suggestions before major decisions

⚠️ **Sample News Mode**
- Falls back to 5 curated articles without API key
- Sample articles are illustrative, not real-time

## Troubleshooting

**"Loading news..." persists**
- Check internet connection
- Verify NEWS_API_KEY if using live mode
- Check browser console for errors

**AI analysis shows "fallback mode"**
- Azure OpenAI credentials missing/invalid
- Check AZURE_OPENAI_API_KEY in `.env`
- Heuristic analysis still works (lower quality)

**"Simulate This Policy" button disabled**
- No specific parameter suggestions in article
- News is informational only (e.g., jobs report)
- Still shows impact analysis

## Future Enhancements

🚀 **Planned Features**:
- Historical news archive & search
- Policy calendar (upcoming Fed meetings, etc.)
- News-based scenario presets
- Compare simulation to actual outcomes
- Email/Slack alerts for major policy changes

## Technical Details

**Files Added**:
- `data/news_client.py` - NewsAPI integration
- `data/news_analyzer.py` - Azure OpenAI analysis
- `dashboard/pages/news_insights.py` - UI page

**Dependencies**:
- `requests` (already in requirements.txt)
- Azure OpenAI (existing)
- NewsAPI (optional, free tier available)

---

**Questions?** Check the main README or open an issue on GitHub.
