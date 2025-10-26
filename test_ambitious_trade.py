"""
Test the ambitious trade model with all new features
"""
from simulation.trade_economy_model import TradeEconomyModel

print('Testing AMBITIOUS Trade Model with:')
print('- Reduced import propensities (17% total vs 50% before)')
print('- Dynamic export capacity growth')
print('- Capital flows and financial account')
print('- Central bank FX intervention')
print('- Trade deficit dampening feedback')
print()

sim = TradeEconomyModel()
sim.set_interest_rate(0.08)  # High interest rate

print('Step | GDP    | Prod  | Exports | Imports | Trade Bal | Cap Flows | Reserves | China E | EU E  | Export Cap')
print('-' * 115)

for i in range(200):
    result = sim.step()

    gdp = result.get('gdp', 0)
    prod = sum(f.production for f in sim.firms)
    exports = result.get('total_exports', 0)
    imports = result.get('total_imports', 0)
    balance = result.get('trade_balance', 0)
    cap_flow = result.get('capital_flows', 0)
    reserves = result.get('foreign_reserves', 0)
    china_e = sim.foreign_sectors['China'].exchange_rate
    eu_e = sim.foreign_sectors['EU'].exchange_rate
    export_cap = result.get('export_capacity', 0)

    # Print every 20 steps
    if (i + 1) % 20 == 0 or i == 0:
        print(f'{i+1:4d} | {gdp:6.0f} | {prod:5.1f} | {exports:7.0f} | {imports:7.0f} | {balance:9.0f} | {cap_flow:9.0f} | {reserves:8.0f} | {china_e:7.3f} | {eu_e:5.3f} | {export_cap:10.1f}')

print()
print('=' * 115)
print('FINAL ANALYSIS:')
print(f'Final Trade Balance: ${balance:,.0f}')
print(f'Final Exports: ${exports:,.0f}')
print(f'Final Imports: ${imports:,.0f}')
ratio = (exports/imports*100) if imports > 0 else 0
print(f'Export/Import Ratio: {ratio:.1f}%')
print()
china_dev = (china_e-7.0)/7.0*100
eu_dev = (eu_e-0.9)/0.9*100
print(f'China E-rate: {china_e:.3f} (started 7.000, baseline deviation: {china_dev:+.1f}%)')
print(f'EU E-rate: {eu_e:.3f} (started 0.900, baseline deviation: {eu_dev:+.1f}%)')
print(f'Foreign Reserves: ${reserves:,.0f} (started $100,000)')
print(f'Export Capacity: {export_cap:.1f} units (started 1000)')
print()
print(f'Capital Flows (final): ${cap_flow:,.0f}')
saturation = result.get('import_saturation', 0)*100
print(f'Import Saturation: {saturation:.1f}% of GDP')
