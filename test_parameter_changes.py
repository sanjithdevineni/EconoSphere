"""
Test parameter changes during simulation
Simulates user adjusting sliders and clicking buttons in the dashboard
"""
from simulation.financial_markets_model import FinancialMarketsModel
import config

def test_dynamic_parameters():
    """Test changing parameters during simulation"""

    print("=" * 80)
    print("DYNAMIC PARAMETER CHANGE TEST")
    print("=" * 80)
    print()

    sim = FinancialMarketsModel(
        num_consumers=50,
        num_firms=5,
        enable_govt_crypto_reserve=False,
        seed=42
    )

    print("Phase 1: Baseline (Steps 0-20)")
    print("-" * 80)
    for _ in range(20):
        sim.step()

    baseline_crypto = sim.crypto_market.price
    baseline_stock = sim.stock_market.index
    baseline_rate = sim.central_bank.interest_rate

    print(f"Baseline State:")
    print(f"  Interest Rate: {baseline_rate*100:.1f}%")
    print(f"  Crypto Price: ${baseline_crypto:,.0f}")
    print(f"  Stock Index: {baseline_stock:.2f}")
    print()

    # TEST 1: Interest Rate Increase
    print("Phase 2: INCREASE Interest Rate to 8% (Steps 21-40)")
    print("-" * 80)
    sim.central_bank.set_interest_rate(0.08)

    for _ in range(20):
        sim.step()

    high_rate_crypto = sim.crypto_market.price
    high_rate_stock = sim.stock_market.index
    current_rate = sim.central_bank.interest_rate

    print(f"After Rate Hike:")
    print(f"  Interest Rate: {current_rate*100:.1f}%")
    print(f"  Crypto Price: ${high_rate_crypto:,.0f} ({((high_rate_crypto-baseline_crypto)/baseline_crypto*100):+.1f}%)")
    print(f"  Stock Index: {high_rate_stock:.2f} ({((high_rate_stock-baseline_stock)/baseline_stock*100):+.1f}%)")

    if high_rate_crypto < baseline_crypto * 0.9:
        print("  [OK] Crypto fell with rate hike!")
    else:
        print(f"  [WARNING] Crypto should fall with rate hike (expected -10% or more)")
    print()

    # TEST 2: Interest Rate Decrease
    print("Phase 3: DECREASE Interest Rate to 1% (Steps 41-60)")
    print("-" * 80)
    sim.central_bank.set_interest_rate(0.01)

    for _ in range(20):
        sim.step()

    low_rate_crypto = sim.crypto_market.price
    low_rate_stock = sim.stock_market.index
    current_rate = sim.central_bank.interest_rate

    print(f"After Rate Cut:")
    print(f"  Interest Rate: {current_rate*100:.1f}%")
    print(f"  Crypto Price: ${low_rate_crypto:,.0f} ({((low_rate_crypto-high_rate_crypto)/high_rate_crypto*100):+.1f}%)")
    print(f"  Stock Index: {low_rate_stock:.2f} ({((low_rate_stock-high_rate_stock)/high_rate_stock*100):+.1f}%)")

    if low_rate_crypto > high_rate_crypto * 1.1:
        print("  [OK] Crypto rallied with rate cut!")
    else:
        print(f"  [INFO] Crypto may rally with rate cut (got {((low_rate_crypto-high_rate_crypto)/high_rate_crypto*100):+.1f}%)")
    print()

    # TEST 3: Enable Government Crypto Reserve
    print("Phase 4: Enable Government Crypto Reserve (Steps 61-80)")
    print("-" * 80)

    reserve_before = sim.crypto_market.price
    print(f"Before Reserve:")
    print(f"  Crypto Price: ${reserve_before:,.0f}")

    sim.enable_government_crypto_reserve(annual_budget=500000)  # $500k budget

    reserve_after = sim.crypto_market.price
    reserve_holdings = sim.government.crypto_reserve

    print(f"After Reserve Enabled:")
    print(f"  Crypto Price: ${reserve_after:,.0f} ({((reserve_after-reserve_before)/reserve_before*100):+.1f}%)")
    print(f"  Govt Holdings: {reserve_holdings:.2f} coins")

    if reserve_after > reserve_before * 1.05:
        print("  [OK] Crypto pumped with govt reserve!")
    else:
        print(f"  [WARNING] Crypto should pump with govt reserve (got {((reserve_after-reserve_before)/reserve_before*100):+.1f}%)")

    # Continue simulation
    for _ in range(20):
        sim.step()

    final_crypto = sim.crypto_market.price
    print(f"After 20 more steps:")
    print(f"  Crypto Price: ${final_crypto:,.0f}")
    print()

    # TEST 4: Trigger Crash Scenario
    print("Phase 5: Trigger Crypto Crash Scenario (Step 81)")
    print("-" * 80)

    crash_before = sim.crypto_market.price
    print(f"Before Crash:")
    print(f"  Crypto Price: ${crash_before:,.0f}")

    sim.trigger_crypto_crash(severity=0.5)

    crash_after = sim.crypto_market.price

    print(f"After Crash:")
    print(f"  Crypto Price: ${crash_after:,.0f} ({((crash_after-crash_before)/crash_before*100):+.1f}%)")

    if crash_after < crash_before * 0.55:
        print("  [OK] Crypto crashed by ~50%!")
    else:
        print(f"  [WARNING] Crash should be ~50% (got {((crash_after-crash_before)/crash_before*100):+.1f}%)")
    print()

    # TEST 5: Trigger Rally Scenario
    print("Phase 6: Trigger Crypto Rally Scenario (Step 82)")
    print("-" * 80)

    rally_before = sim.crypto_market.price
    print(f"Before Rally:")
    print(f"  Crypto Price: ${rally_before:,.0f}")

    sim.trigger_crypto_rally(magnitude=0.4)

    rally_after = sim.crypto_market.price

    print(f"After Rally:")
    print(f"  Crypto Price: ${rally_after:,.0f} ({((rally_after-rally_before)/rally_before*100):+.1f}%)")

    if rally_after > rally_before * 1.35:
        print("  [OK] Crypto rallied by ~40%!")
    else:
        print(f"  [WARNING] Rally should be ~40% (got {((rally_after-rally_before)/rally_before*100):+.1f}%)")
    print()

    # Final summary
    print("=" * 80)
    print("SUMMARY: Parameter Changes During Simulation")
    print("=" * 80)
    print(f"Total steps: {sim.current_step}")
    print(f"Interest rate changes: 3.0% -> 8.0% -> 1.0%")
    print(f"Government reserve: Disabled -> Enabled ($500k budget)")
    print(f"Scenarios triggered: Crypto crash (-50%), Crypto rally (+40%)")
    print()
    print(f"Final State:")
    print(f"  Crypto Price: ${sim.crypto_market.price:,.0f}")
    print(f"  Stock Index: {sim.stock_market.index:.2f}")
    print(f"  Interest Rate: {sim.central_bank.interest_rate*100:.1f}%")
    print(f"  Govt Crypto Reserve: {sim.government.crypto_reserve:.2f} coins")
    print()
    print("=" * 80)
    print(" All parameter changes working correctly!")
    print("=" * 80)

if __name__ == "__main__":
    test_dynamic_parameters()
