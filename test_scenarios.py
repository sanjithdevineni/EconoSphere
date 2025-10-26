"""
Test various scenarios to identify bugs in financial markets
"""
from simulation.financial_markets_model import FinancialMarketsModel
import config

def test_govt_reserve():
    """Test government crypto reserve purchase"""
    print("\n" + "="*80)
    print("TEST 1: Government Crypto Reserve")
    print("="*80)

    sim = FinancialMarketsModel(
        num_consumers=50,
        num_firms=5,
        enable_govt_crypto_reserve=False,
        seed=42
    )

    # Run baseline
    for _ in range(10):
        sim.step()

    price_before = sim.crypto_market.price
    govt_holdings_before = sim.government.crypto_reserve

    print(f"BEFORE Reserve:")
    print(f"  Crypto Price: ${price_before:,.0f}")
    print(f"  Govt Holdings: {govt_holdings_before:.2f} coins")

    # Enable reserve and make purchase
    print("\nEnabling government crypto reserve with $100k budget...")
    sim.enable_government_crypto_reserve(annual_budget=100000)

    price_after = sim.crypto_market.price
    govt_holdings_after = sim.government.crypto_reserve

    print(f"\nAFTER Reserve:")
    print(f"  Crypto Price: ${price_after:,.0f}")
    print(f"  Govt Holdings: {govt_holdings_after:.2f} coins")
    print(f"  Price Change: {((price_after - price_before) / price_before * 100):+.1f}%")

    if price_after > price_before:
        print("  [OK] Price increased!")
    else:
        print("  [FAIL] Price did NOT increase!")

    if govt_holdings_after > 0:
        print("  [OK] Government bought crypto!")
    else:
        print("  [FAIL] Government holdings still ZERO!")


def test_interest_rate_effect():
    """Test interest rate changes affecting markets"""
    print("\n" + "="*80)
    print("TEST 2: Interest Rate Effects")
    print("="*80)

    sim = FinancialMarketsModel(
        num_consumers=50,
        num_firms=5,
        seed=42
    )

    # Baseline with low rates
    print("\nPhase 1: Low Interest Rates (3%)")
    sim.central_bank.set_interest_rate(0.03)

    for _ in range(20):
        sim.step()

    crypto_low_rate = sim.crypto_market.price
    stock_low_rate = sim.stock_market.index

    print(f"  Crypto: ${crypto_low_rate:,.0f}")
    print(f"  Stock: {stock_low_rate:.2f}")

    # High rates
    print("\nPhase 2: HIGH Interest Rates (8%)")
    sim.central_bank.set_interest_rate(0.08)

    for _ in range(20):
        sim.step()

    crypto_high_rate = sim.crypto_market.price
    stock_high_rate = sim.stock_market.index

    print(f"  Crypto: ${crypto_high_rate:,.0f}")
    print(f"  Stock: {stock_high_rate:.2f}")

    crypto_change = ((crypto_high_rate - crypto_low_rate) / crypto_low_rate * 100)
    stock_change = ((stock_high_rate - stock_low_rate) / stock_low_rate * 100)

    print(f"\nChanges from rate hike:")
    print(f"  Crypto: {crypto_change:+.1f}%")
    print(f"  Stock: {stock_change:+.1f}%")

    if crypto_change < -5:
        print("  [OK] Crypto fell with higher rates!")
    else:
        print(f"  [FAIL] Crypto should fall with higher rates (got {crypto_change:+.1f}%)")

    if stock_change < -5:
        print("  [OK] Stocks fell with higher rates!")
    else:
        print(f"  [FAIL] Stocks should fall with higher rates (got {stock_change:+.1f}%)")


def test_inflation_crypto_correlation():
    """Test if crypto responds to inflation"""
    print("\n" + "="*80)
    print("TEST 3: Inflation Hedge Behavior")
    print("="*80)

    sim = FinancialMarketsModel(
        num_consumers=50,
        num_firms=5,
        seed=42
    )

    # Baseline
    for _ in range(10):
        sim.step()

    crypto_baseline = sim.crypto_market.price

    print(f"\nBaseline crypto: ${crypto_baseline:,.0f}")

    # Manually inject high inflation scenario
    print("\nInjecting HIGH INFLATION (8%)...")

    # Run with high inflation state
    for _ in range(20):
        sim.step()
        # Check what inflation actually is
        inflation = sim.metrics.latest_metrics.get('inflation_rate', 0.02)

    current_inflation = sim.metrics.latest_metrics.get('inflation_rate', 0.02) * 100
    crypto_after_inflation = sim.crypto_market.price

    print(f"Actual inflation in sim: {current_inflation:.2f}%")
    print(f"Crypto after inflation: ${crypto_after_inflation:,.0f}")
    print(f"Change: {((crypto_after_inflation - crypto_baseline) / crypto_baseline * 100):+.1f}%")

    if current_inflation < 4:
        print("  [WARNING] Inflation is not high enough to test!")


def test_scenario_buttons():
    """Test crash/rally scenarios"""
    print("\n" + "="*80)
    print("TEST 4: Scenario Buttons")
    print("="*80)

    sim = FinancialMarketsModel(
        num_consumers=50,
        num_firms=5,
        seed=42
    )

    for _ in range(10):
        sim.step()

    # Stock crash
    print("\n--- Stock Crash Scenario ---")
    stock_before = sim.stock_market.index
    print(f"Before: {stock_before:.2f}")

    sim.trigger_stock_crash(severity=0.3)

    stock_after = sim.stock_market.index
    print(f"After: {stock_after:.2f}")
    print(f"Change: {((stock_after - stock_before) / stock_before * 100):+.1f}%")

    if stock_after < stock_before * 0.75:
        print("[OK] Stock crashed!")
    else:
        print("[FAIL] Stock did not crash enough!")

    # Crypto crash
    print("\n--- Crypto Crash Scenario ---")
    crypto_before = sim.crypto_market.price
    print(f"Before: ${crypto_before:,.0f}")

    sim.trigger_crypto_crash(severity=0.5)

    crypto_after = sim.crypto_market.price
    print(f"After: ${crypto_after:,.0f}")
    print(f"Change: {((crypto_after - crypto_before) / crypto_before * 100):+.1f}%")

    if crypto_after < crypto_before * 0.55:
        print("[OK] Crypto crashed!")
    else:
        print("[FAIL] Crypto did not crash enough!")

    # Crypto rally
    print("\n--- Crypto Rally Scenario ---")
    crypto_before = sim.crypto_market.price
    print(f"Before: ${crypto_before:,.0f}")

    sim.trigger_crypto_rally(magnitude=0.3)

    crypto_after = sim.crypto_market.price
    print(f"After: ${crypto_after:,.0f}")
    print(f"Change: {((crypto_after - crypto_before) / crypto_before * 100):+.1f}%")

    if crypto_after > crypto_before * 1.25:
        print("[OK] Crypto rallied!")
    else:
        print("[FAIL] Crypto did not rally enough!")


def test_parameter_persistence():
    """Test if parameter changes persist across steps"""
    print("\n" + "="*80)
    print("TEST 5: Parameter Persistence")
    print("="*80)

    sim = FinancialMarketsModel(
        num_consumers=50,
        num_firms=5,
        seed=42
    )

    # Set interest rate
    print("\nSetting interest rate to 7%...")
    sim.central_bank.set_interest_rate(0.07)

    # Run multiple steps and check if rate persists
    rates = []
    for i in range(10):
        sim.step()
        rate = sim.central_bank.interest_rate
        rates.append(rate)

    print(f"Rates over 10 steps: {[f'{r*100:.1f}%' for r in rates[:5]]}")

    if all(abs(r - 0.07) < 0.001 for r in rates):
        print("[OK] Interest rate persisted!")
    else:
        print("[FAIL] Interest rate changed unexpectedly!")
        print(f"  Expected: 7.0%, Got: {[f'{r*100:.1f}%' for r in rates]}")


def check_economic_state_propagation():
    """Check if economic state is correctly passed to markets"""
    print("\n" + "="*80)
    print("TEST 6: Economic State Propagation")
    print("="*80)

    sim = FinancialMarketsModel(
        num_consumers=50,
        num_firms=5,
        seed=42
    )

    # Run a few steps
    for _ in range(5):
        sim.step()

    # Check economic state
    metrics = sim.metrics.latest_metrics

    print("\nEconomic Metrics:")
    print(f"  Inflation: {metrics.get('inflation_rate', 0) * 100:.2f}%")
    print(f"  Interest Rate: {metrics.get('interest_rate', 0) * 100:.2f}%")
    print(f"  Unemployment: {metrics.get('unemployment_rate', 0) * 100:.2f}%")
    print(f"  GDP: ${metrics.get('gdp', 0):,.0f}")

    print("\nMarket Metrics:")
    print(f"  Stock Index: {metrics.get('stock_index', 0):.2f}")
    print(f"  Crypto Price: ${metrics.get('crypto_price', 0):,.0f}")
    print(f"  Crypto Adoption: {metrics.get('crypto_adoption_rate', 0) * 100:.2f}%")

    # Check if stock market actually received the parameters
    print("\nDirect Market Check:")
    print(f"  Stock market exists: {sim.stock_market is not None}")
    print(f"  Crypto market exists: {sim.crypto_market is not None}")

    if sim.stock_market:
        print(f"  Stock market has {len(sim.stock_market.firms)} firms")
        print(f"  Stock sentiment: {sim.stock_market.sentiment:.2f}")

    if sim.crypto_market:
        print(f"  Crypto inflation hedge belief: {sim.crypto_market.inflation_hedge_belief:.2f}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("FINANCIAL MARKETS COMPREHENSIVE TESTING")
    print("="*80)

    try:
        test_govt_reserve()
    except Exception as e:
        print(f"\n[ERROR in test_govt_reserve]: {e}")
        import traceback
        traceback.print_exc()

    try:
        test_interest_rate_effect()
    except Exception as e:
        print(f"\n[ERROR in test_interest_rate_effect]: {e}")
        import traceback
        traceback.print_exc()

    try:
        test_inflation_crypto_correlation()
    except Exception as e:
        print(f"\n[ERROR in test_inflation_crypto_correlation]: {e}")
        import traceback
        traceback.print_exc()

    try:
        test_scenario_buttons()
    except Exception as e:
        print(f"\n[ERROR in test_scenario_buttons]: {e}")
        import traceback
        traceback.print_exc()

    try:
        test_parameter_persistence()
    except Exception as e:
        print(f"\n[ERROR in test_parameter_persistence]: {e}")
        import traceback
        traceback.print_exc()

    try:
        check_economic_state_propagation()
    except Exception as e:
        print(f"\n[ERROR in check_economic_state_propagation]: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)
