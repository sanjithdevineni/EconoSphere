# EconoSphere - Quick Start Guide

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. (Optional) Set Up API Keys

Create a `.env` file in the project root:

```bash
# NewsAPI (optional - for real-time news)
NEWS_API_KEY=your_newsapi_key_here

# Azure OpenAI (required for AI features)
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Optional: Custom calibration file
ECON_CALIBRATION_FILE=config/calibrated/usa_2023.json
```

**Note**: The simulator works without API keys using sample data and fallback modes.

### 3. Launch the Dashboard

```bash
python main.py
```

Open your browser to **http://localhost:8050**

## Dashboard Pages

### 🏠 Simulation (Main Page)

The core economic simulator with policy controls.

**Controls Available:**
- **Tax Rates**: VAT, Payroll, Corporate (0-50%)
- **Interest Rate**: Central bank lending rate (0-10%)
- **Government Spending**: Direct fiscal stimulus ($0-$50k)
- **Welfare Payments**: Unemployment benefits ($0-$2000)
- **Auto-Policy**: Enable Taylor Rule (automatic monetary policy)

**Charts:**
- GDP (economic output)
- Unemployment Rate
- Inflation Rate
- Gini Coefficient (inequality)

**Scenario Buttons:**
- **Trigger Recession**: Simulate demand shock
- **Trigger Inflation**: Simulate supply shock
- **Reset**: Return to initial state

### 📰 News Insights

AI-powered analysis of real economic news.

**How to Use:**
1. Click "🔄 Refresh News" to fetch latest articles
2. Review AI analysis for each article:
   - Policy type (Monetary, Fiscal, Mixed, Indicator)
   - Sentiment (Expansionary, Contractionary, Neutral)
   - Expected impacts on GDP, inflation, unemployment
3. Click "▶️ Simulate This Policy" to test in simulator
4. Navigate to Simulation page to see results

**Features:**
- Real-time news from NewsAPI (with key) or sample articles (without)
- Azure OpenAI analysis of policy impacts
- One-click policy parameter extraction
- Confidence scores on predictions

### 📊 Validation

Compare simulation output to real-world economic data.

**Features:**
- Time-series charts: Simulation vs Actual data
- Trend forecasting with ML models
- Diagnostic metrics (R², MAE, RMSE)
- ML-calibrated parameters display

**Data Sources:**
- World Bank API (GDP, unemployment, inflation, etc.)
- Machine learning parameter fitting
- Historical scenario validation

### 🌍 International Trade

Multi-country trade simulation with tariffs and FX.

**Trading Partners:**
- 🇨🇳 China (large manufacturing economy)
- 🇪🇺 European Union (advanced economy)
- 🌏 Rest of World (aggregate)

**Controls:**
- **Import Tariff Rate**: 0-100% on all imports
- **Interest Rate**: Affects capital flows and FX rates
- **Government Spending**: Fiscal policy impact

**Trade Scenarios:**
- **⚔️ Trigger Trade War**: Impose tariffs, watch retaliation
- **🤝 Sign FTA with China**: Free trade agreement
- **🇪🇺 Sign FTA with EU**: European free trade

**Charts:**
- Trade Balance (exports - imports)
- Import/Export flows
- Exchange Rates (Yuan, Euro, ROW currency)
- Country-specific trade volumes
- Retaliatory tariff tracking

**Advanced Features:**
- Capital flows (financial account balancing)
- Central bank FX intervention
- Dynamic export capacity
- Trade deficit dampening

## Usage Examples

### Example 1: Test Fiscal Policy

**Goal**: See how tax changes affect the economy

1. Go to **Simulation** page
2. Start the simulation (click "Start Simulation")
3. Raise **VAT Rate** from 20% to 40%
4. **Observe:**
   - GDP decreases (less consumer spending)
   - Unemployment rises (firms hire less)
   - Inflation may decrease (lower demand)

5. **Counter with stimulus:**
   - Increase **Government Spending** to $40,000
   - **Observe** partial recovery

### Example 2: Test Monetary Policy

**Goal**: Use interest rates to control inflation

1. Click **"Trigger Inflation"** scenario
2. **Observe** inflation spike
3. Raise **Interest Rate** to 8%
4. **Observe:**
   - Inflation stabilizes/decreases
   - Unemployment may rise (firms borrow less)
   - GDP growth slows

### Example 3: Trade War Simulation

**Goal**: See effects of tariff policies

1. Go to **International Trade** page
2. Start simulation
3. Set **Import Tariff** to 60%
4. Click **"⚔️ Trigger Trade War"**
5. **Observe:**
   - China & EU retaliate with their own tariffs
   - Trade balance changes
   - Exchange rates shift
   - Domestic prices affected

### Example 4: News-Based Policy Test

**Goal**: Simulate real-world policy from news

1. Go to **News Insights** page
2. Click **"🔄 Refresh News"**
3. Find article about Fed rate decision
4. Review AI analysis predictions
5. Click **"▶️ Simulate This Policy"**
6. Go to **Simulation** to see scenario run

### Example 5: Real-World Validation

**Goal**: Compare to actual economic data

1. **Calibrate with real data:**
   ```bash
   python scripts/calibrate_economy.py --country USA --year 2023
   export ECON_CALIBRATION_FILE=config/calibrated/usa_2023.json
   python main.py
   ```

2. Go to **Validation** page
3. View calibration parameters and diagnostics
4. Compare simulation trends to actual data
5. Check R² scores for accuracy

## Advanced Features

### Auto-Policy Mode (Taylor Rule)

Enable automatic monetary policy:

1. On Simulation page, check **"Auto Monetary Policy"**
2. Central bank automatically adjusts interest rates:
   - **High inflation** → Raise rates
   - **High unemployment** → Lower rates
3. Watch central bank respond to economic conditions

### Real-World Calibration

Fit model to actual country data:

```bash
# Calibrate to USA 2023
python scripts/calibrate_economy.py --country USA --year 2023

# Calibrate to Japan with recession scenario
python scripts/calibrate_economy.py --country JPN --year 2020 --scenario recession

# Use calibrated parameters
export ECON_CALIBRATION_FILE=config/calibrated/usa_2023.json
python main.py
```

View calibrated parameters on **Validation** page.

### AI Narrative System

Real-time economic news generation (if Azure OpenAI is configured):

1. Run simulation
2. AI monitors for significant events:
   - Unemployment spikes
   - Inflation surges
   - GDP crashes/booms
   - Trade imbalances
3. Generates news-style narratives
4. Appears in dashboard (if narrative display enabled)

## Configuration

### Adjust Simulation Parameters

Edit `config.py`:

```python
# Agent counts
NUM_CONSUMERS = 100  # Number of workers
NUM_FIRMS = 10       # Number of businesses

# Initial conditions
INITIAL_VAT_RATE = 0.20      # 20% VAT
INITIAL_INTEREST_RATE = 0.03 # 3% interest
INITIAL_WELFARE_PAYMENT = 800

# Update speed
UPDATE_INTERVAL = 1000  # Milliseconds between updates
```

### Change Dashboard Port

In `config.py`:

```python
PORT = 8050  # Change to different port if needed
DEBUG_MODE = True  # Set to False for production
```

## Troubleshooting

### Dashboard Won't Load

**Problem**: Browser shows "can't reach page"

**Solutions:**
- Check terminal for errors
- Ensure port 8050 isn't in use
- Try different port in `config.py`
- Check firewall settings

### Charts Not Updating

**Problem**: Graphs frozen after starting simulation

**Solutions:**
- Click "Reset" and restart
- Check browser console for JavaScript errors
- Refresh page (F5)
- Reduce `UPDATE_INTERVAL` in config.py

### News Insights Shows "Loading..."

**Problem**: News page stuck loading

**Solutions:**
- Check internet connection
- Verify `NEWS_API_KEY` in `.env` (or use sample mode)
- Check NewsAPI quota (100 requests/day on free tier)
- Sample news works without API key

### AI Analysis Not Working

**Problem**: News shows "fallback heuristic analysis"

**Solutions:**
- Verify Azure OpenAI credentials in `.env`
- Check API key is valid
- Ensure deployment name is correct
- Heuristic fallback still provides basic analysis

### Simulation Crashes

**Problem**: All agents unemployed, GDP = 0

**Solutions:**
- Click **"Reset"** to restart
- Use more moderate policy values
- Avoid extreme combinations (100% tax + 0% spending)
- Reduce agent count in `config.py` if too slow

### Trade Page Issues

**Problem**: Exchange rates collapsing or exploding

**Solutions:**
- Check if central bank intervention is enabled
- Use moderate tariff rates (< 50%)
- Trade model includes stabilization mechanisms
- Large deficits/surpluses are expected initially

## Tips & Best Practices

### For Policy Testing

1. **Start with baseline**: Let simulation run stable before changes
2. **Change one thing**: Isolate policy effects
3. **Wait for effects**: Policy impacts take 10-20 steps to fully manifest
4. **Compare scenarios**: Reset and try alternative policies

### For Presentations

1. **Have scenarios ready**: Practice 2-3 demo paths
2. **Use Reset button**: Start fresh for each demo
3. **Explain the "why"**: Show causal chains (tax ↑ → spending ↓ → GDP ↓)
4. **Show trade-offs**: Higher rates fight inflation but raise unemployment

### For Education

1. **Show agent interactions**: Explain how consumers/firms respond
2. **Visualize feedback loops**: Tax → spending → production → employment
3. **Test economic theories**: Phillips curve, fiscal multiplier, etc.
4. **Use validation page**: Connect to real-world data

### For Research

1. **Calibrate to real data**: Use `calibrate_economy.py`
2. **Export data**: Record history for analysis
3. **Test hypotheses**: Systematically vary parameters
4. **Validate results**: Check against actual economic patterns

## Next Steps

**Explore Features:**
- [ ] Try each dashboard page
- [ ] Test all scenario buttons
- [ ] Simulate a news article
- [ ] Run a calibrated simulation
- [ ] Experiment with trade policies

**Learn the System:**
- [ ] Read [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- [ ] Read [INTERNATIONAL_TRADE.md](INTERNATIONAL_TRADE.md) for trade model
- [ ] Check [NEWS_INSIGHTS_README.md](NEWS_INSIGHTS_README.md) for AI features
- [ ] Review agent code in `agents/` directory

**Customize:**
- [ ] Adjust parameters in `config.py`
- [ ] Add your own crisis scenarios
- [ ] Modify agent behaviors
- [ ] Extend with new features

---

**Questions?** Check the main [README.md](README.md) or open an issue on GitHub.
