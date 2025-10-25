# MacroEcon Simulator - Quick Start Guide

## Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Test the simulation**:
   ```bash
   python test_simulation.py
   ```
   This will verify everything is working correctly.

3. **Launch the dashboard**:
   ```bash
   python main.py
   ```

4. **Open your browser** to `http://localhost:8050`

## Using the Dashboard

### Policy Controls

**Fiscal Policy (Government)**:
- **Tax Rate**: Adjust income tax (0-50%)
- **Welfare Payment**: Set unemployment benefits ($0-$2000)
- **Government Spending**: Control direct government expenditure

**Monetary Policy (Central Bank)**:
- **Interest Rate**: Set borrowing costs (0-10%)
- **Auto Policy**: Enable Taylor Rule (automatic rate adjustment)

### Simulation Controls

- **Start**: Begin running the simulation in real-time
- **Pause**: Freeze the simulation
- **Reset**: Return to initial conditions
- **Trigger Recession**: Simulate a demand shock
- **Trigger Inflation**: Simulate inflationary pressure

### Reading the Charts

1. **GDP**: Total economic output (higher = better)
2. **Unemployment**: Percentage of workers unemployed (lower = better)
3. **Inflation**: Rate of price increases (target ~2%)
4. **Gini Coefficient**: Wealth inequality (0 = equal, 1 = unequal)

## Demo Scenarios for Hackathon Presentation

### Scenario 1: Policy Sandbox
**Goal**: Show how policies affect the economy

1. Start with baseline economy
2. **Raise taxes to 40%** → Watch GDP fall, unemployment rise
3. **Lower interest rates to 1%** → See recovery as firms invest more
4. **Increase welfare to $1500** → Observe inequality decrease

### Scenario 2: Crisis Response
**Goal**: Simulate 2008-style recession

1. Click "Trigger Recession"
2. **Watch unemployment spike** (consumers lose wealth, firms fire workers)
3. **Implement crisis response**:
   - Slash interest rates to 0.25%
   - Increase government spending to $40,000
   - Raise welfare to $1200
4. **Show recovery** as economy stabilizes

### Scenario 3: Central Bank Independence
**Goal**: Demonstrate automatic monetary policy

1. Enable "Auto Monetary Policy"
2. Trigger inflation crisis
3. **Watch central bank automatically raise rates** to fight inflation
4. Show how Taylor Rule balances inflation vs. unemployment

### Scenario 4: UBI Experiment
**Goal**: Test universal basic income

1. Set welfare to $1800 (very high)
2. Raise taxes to 35% (to fund it)
3. **Observe**:
   - Unemployment impact (do people still work?)
   - Inequality reduction (Gini coefficient)
   - Inflation pressure (too much money?)

## Hackathon Pitch Tips

### Key Talking Points

1. **Agent-Based Modeling**: "Each consumer and firm is an autonomous agent making decisions"
2. **Real Economic Theory**: "We implemented actual mechanisms like labor markets, price discovery, and the Taylor Rule"
3. **Policy Sandbox**: "Perfect for testing 'what-if' scenarios before implementing real policies"
4. **Business Applications**: "Companies can test pricing strategies in simulated markets"
5. **Educational**: "Visualize complex economic concepts in real-time"

### Technical Highlights

- **Architecture**: Python + Mesa (ABM) + Plotly Dash
- **100+ agents** interacting in real-time
- **Multiple markets**: Labor and goods markets with price discovery
- **Realistic policies**: Fiscal (taxes, spending) + Monetary (interest rates)
- **Data integration**: World Bank API for real-world calibration

### Demo Flow (3-5 minutes)

1. **Intro** (30s): "We built a full economic simulator with autonomous agents"
2. **Show baseline** (30s): Point out the 4 key metrics
3. **Policy demo** (1m): Adjust tax rate, show immediate impact
4. **Crisis demo** (1.5m): Trigger recession, implement response, show recovery
5. **Unique feature** (1m): Show auto-policy or UBI experiment
6. **Wrap up** (30s): "Perfect for policy testing, business strategy, and education"

## Customization

### Adjust Parameters

Edit `config.py` to change:
- Number of agents
- Initial economic conditions
- Policy defaults
- Market parameters

### Add New Scenarios

Edit `utils/scenarios.py` to add pre-configured scenarios.

### Integrate More Data

Use `data/world_bank.py` to fetch real economic indicators and calibrate the simulation.

## Troubleshooting

**Simulation runs too fast/slow?**
- Adjust `UPDATE_INTERVAL` in `config.py` (in milliseconds)

**Want more/fewer agents?**
- Change `NUM_CONSUMERS` and `NUM_FIRMS` in `config.py`
- Note: More agents = slower but more realistic

**Charts not updating?**
- Click "Start Simulation" button
- Check browser console for errors

**Economy crashes (all unemployed, no GDP)?**
- Click "Reset" to restart
- Adjust policies to more moderate values

## Next Steps

**For Hackathon**:
- [ ] Practice your demo scenarios
- [ ] Prepare slides explaining the architecture
- [ ] Test on demo laptop to ensure dependencies work
- [ ] Think of clever use cases to pitch

**Future Enhancements** (if you have time):
- [ ] Add international trade (import/export)
- [ ] Implement banking sector
- [ ] ML-based prediction overlays
- [ ] Export simulation data to CSV
- [ ] Multiplayer mode (multiple users control different policies)

Good luck with your hackathon!
