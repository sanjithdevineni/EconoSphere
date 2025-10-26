"""
Test Financial Markets Simulation for 150 steps
Look for anomalies, weird behavior, crashes, etc.
"""
import sys
import logging
from simulation.financial_markets_model import FinancialMarketsModel
import config

# Set up logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise

def run_test():
    """Run markets simulation for 150 steps and analyze"""

    print("=" * 80)
    print("FINANCIAL MARKETS SIMULATION TEST - 150 Steps")
    print("=" * 80)
    print()

    # Create simulation
    print("Initializing simulation...")
    sim = FinancialMarketsModel(
        num_consumers=config.NUM_CONSUMERS,
        num_firms=config.NUM_FIRMS,
        enable_stock_market=True,
        enable_crypto_market=True,
        enable_govt_crypto_reserve=False,
        seed=42  # For reproducibility
    )

    print(f"[OK] Created with {sim.num_consumers} consumers, {sim.num_firms} firms")
    print()

    # Run simulation
    print("Running 150 steps...")
    errors = []
    warnings = []

    for step in range(150):
        try:
            sim.step()

            # Check for anomalies every 10 steps
            if step % 10 == 0:
                metrics = sim.metrics.latest_metrics

                # Check for NaN or Infinity
                if any(str(v) in ['nan', 'inf', '-inf'] for v in metrics.values() if isinstance(v, (int, float))):
                    warnings.append(f"Step {step}: NaN/Inf detected in metrics")

                # Check for negative prices
                crypto_price = metrics.get('crypto_price', 0)
                stock_index = metrics.get('stock_index', 0)

                if crypto_price <= 0:
                    errors.append(f"Step {step}: Crypto price = {crypto_price} (NEGATIVE/ZERO!)")
                if stock_index <= 0:
                    errors.append(f"Step {step}: Stock index = {stock_index} (NEGATIVE/ZERO!)")

                # Check for extreme values
                if crypto_price > 10_000_000:
                    warnings.append(f"Step {step}: Crypto price exploded to ${crypto_price:,.0f}")
                if stock_index > 10_000:
                    warnings.append(f"Step {step}: Stock index exploded to {stock_index:.1f}")

                # Check for extreme crashes
                if crypto_price < 100:
                    warnings.append(f"Step {step}: Crypto crashed to ${crypto_price:.2f}")
                if stock_index < 10:
                    warnings.append(f"Step {step}: Stock index crashed to {stock_index:.2f}")

                # Progress indicator
                if step % 30 == 0:
                    print(f"  Step {step:3d}: Crypto=${crypto_price:10,.0f} | Stock={stock_index:6.1f} | GDP=${metrics.get('gdp', 0):10,.0f}")

        except Exception as e:
            errors.append(f"Step {step}: CRASH - {type(e).__name__}: {e}")
            print(f"\n SIMULATION CRASHED AT STEP {step}")
            print(f"Error: {e}")
            break

    print()
    print("=" * 80)
    print("SIMULATION COMPLETE")
    print("=" * 80)
    print()

    # Final analysis
    final_metrics = sim.metrics.latest_metrics
    history = sim.market_history

    print(" FINAL STATISTICS:")
    print("-" * 80)

    # Stock market
    if sim.stock_market:
        stock_initial = history[0].get('stock_index', 100)
        stock_final = final_metrics.get('stock_index', 100)
        stock_return = ((stock_final - stock_initial) / stock_initial) * 100
        stock_high = max(h.get('stock_index', 100) for h in history)
        stock_low = min(h.get('stock_index', 100) for h in history)

        print(f"Stock Market:")
        print(f"  Start: {stock_initial:.2f}")
        print(f"  End: {stock_final:.2f}")
        print(f"  Return: {stock_return:+.2f}%")
        print(f"  Range: {stock_low:.2f} - {stock_high:.2f}")
        print(f"  Volatility: {((stock_high - stock_low) / stock_initial * 100):.2f}%")

    print()

    # Crypto market
    if sim.crypto_market:
        crypto_initial = history[0].get('crypto_price', 50000)
        crypto_final = final_metrics.get('crypto_price', 50000)
        crypto_return = ((crypto_final - crypto_initial) / crypto_initial) * 100
        crypto_high = max(h.get('crypto_price', 50000) for h in history)
        crypto_low = min(h.get('crypto_price', 50000) for h in history)

        print(f"Cryptocurrency:")
        print(f"  Start: ${crypto_initial:,.0f}")
        print(f"  End: ${crypto_final:,.0f}")
        print(f"  Return: {crypto_return:+.2f}%")
        print(f"  Range: ${crypto_low:,.0f} - ${crypto_high:,.0f}")
        print(f"  Volatility: {((crypto_high - crypto_low) / crypto_initial * 100):.2f}%")
        print(f"  Adoption: {final_metrics.get('crypto_adoption_rate', 0)*100:.2f}%")

    print()

    # Economic indicators
    inflation_avg = sum(h.get('inflation_rate', 0.02) for h in history) / len(history) * 100
    rate_avg = sum(h.get('interest_rate', 0.03) for h in history) / len(history) * 100
    unemployment_avg = sum(h.get('unemployment_rate', 0.05) for h in history) / len(history) * 100

    print(f"Macro Environment:")
    print(f"  Avg Inflation: {inflation_avg:.2f}%")
    print(f"  Avg Interest Rate: {rate_avg:.2f}%")
    print(f"  Avg Unemployment: {unemployment_avg:.2f}%")

    print()
    print("-" * 80)

    # Report issues
    print()
    print(" ISSUES DETECTED:")
    print("-" * 80)

    if errors:
        print(f" ERRORS ({len(errors)}):")
        for err in errors[:10]:  # Show first 10
            print(f"  {err}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
    else:
        print(" No errors!")

    print()

    if warnings:
        print(f"  WARNINGS ({len(warnings)}):")
        for warn in warnings[:10]:  # Show first 10
            print(f"  {warn}")
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more")
    else:
        print(" No warnings!")

    print()
    print("=" * 80)

    # Behavior analysis
    print()
    print(" BEHAVIOR ANALYSIS:")
    print("-" * 80)

    # Check for realistic correlations
    inflation_series = [h.get('inflation_rate', 0.02) * 100 for h in history]
    crypto_series = [h.get('crypto_price', 50000) for h in history]
    stock_series = [h.get('stock_index', 100) for h in history]

    # Simple correlation check
    if len(history) > 20:
        # Check if crypto responds to inflation
        high_inflation_steps = [i for i, inf in enumerate(inflation_series) if inf > 4]
        if high_inflation_steps:
            crypto_during_inflation = [crypto_series[i] for i in high_inflation_steps if i < len(crypto_series)]
            avg_crypto_during_inflation = sum(crypto_during_inflation) / len(crypto_during_inflation) if crypto_during_inflation else crypto_final

            if avg_crypto_during_inflation > crypto_initial * 1.1:
                print(" Crypto acts as inflation hedge (rises during high inflation)")
            else:
                print("  Crypto NOT acting as inflation hedge")

        # Check stock-crypto correlation
        stock_up_steps = [i for i in range(1, len(stock_series)) if stock_series[i] > stock_series[i-1]]
        if stock_up_steps:
            crypto_when_stocks_up = sum(1 for i in stock_up_steps if i < len(crypto_series) and crypto_series[i] > crypto_series[i-1])
            correlation = crypto_when_stocks_up / len(stock_up_steps)

            if correlation > 0.6:
                print(f" Stock-crypto correlation: {correlation:.1%} (risk-on/risk-off behavior)")
            else:
                print(f"  Weak stock-crypto correlation: {correlation:.1%}")

    # Check for weird patterns
    print()
    print("Checking for weird patterns...")

    # Monotonic trends (always increasing/decreasing)
    crypto_always_up = all(crypto_series[i] >= crypto_series[i-1] for i in range(1, len(crypto_series)))
    crypto_always_down = all(crypto_series[i] <= crypto_series[i-1] for i in range(1, len(crypto_series)))

    if crypto_always_up:
        print("  WEIRD: Crypto ONLY went up (no volatility!)")
    elif crypto_always_down:
        print("  WEIRD: Crypto ONLY went down (death spiral!)")
    else:
        print(" Crypto has realistic volatility (ups and downs)")

    # Check for oscillations
    direction_changes = sum(1 for i in range(2, len(crypto_series))
                           if (crypto_series[i] - crypto_series[i-1]) * (crypto_series[i-1] - crypto_series[i-2]) < 0)

    if direction_changes > len(crypto_series) * 0.8:
        print(f"  WEIRD: Too many direction changes ({direction_changes}/{len(crypto_series)}) - oscillating wildly")
    elif direction_changes < len(crypto_series) * 0.1:
        print(f"  WEIRD: Too few direction changes ({direction_changes}/{len(crypto_series)}) - too stable")
    else:
        print(f" Normal volatility pattern ({direction_changes} direction changes)")

    print()
    print("=" * 80)

    return len(errors) == 0 and len(warnings) < 5


if __name__ == "__main__":
    success = run_test()

    print()
    if success:
        print(" TEST PASSED - Simulation looks healthy!")
        sys.exit(0)
    else:
        print(" TEST FAILED - Issues detected!")
        sys.exit(1)
