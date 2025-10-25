"""
Quick test script to verify simulation works
Run this before launching the dashboard to check everything is working
"""

from simulation.economy_model import EconomyModel
import config


def _print_narrative(metrics):
    narrative = metrics.get("narrative") if isinstance(metrics, dict) else None
    if narrative:
        try:
            print(f"      [NEWS] {narrative}")
        except UnicodeEncodeError:
            print(f"      [NEWS] {narrative.encode('ascii', 'ignore').decode('ascii')}")


def test_basic_simulation():
    """Test basic simulation functionality."""
    print("=" * 60)
    print("Testing MacroEcon Simulator")
    print("=" * 60)

    # Create model
    print("\n1. Creating economy model...")
    model = EconomyModel()
    print(f"   [OK] Created {config.NUM_CONSUMERS} consumers")
    print(f"   [OK] Created {config.NUM_FIRMS} firms")
    print(f"   [OK] Created government and central bank")

    # Run simulation for a few steps
    print("\n2. Running simulation for 10 steps...")
    for i in range(10):
        metrics = model.step()
        print(
            f"   Step {i + 1}: GDP=${metrics['gdp']:,.0f}, "
            f"Unemployment={metrics['unemployment']:.1f}%, "
            f"Inflation={metrics['inflation']:.2f}%"
        )
        _print_narrative(metrics)

    print("\n3. Testing policy changes...")

    # Test tax change
    model.set_tax_rate(0.30)
    print("   [OK] Increased VAT rate to 30%")

    # Test interest rate change
    model.set_interest_rate(0.08)
    print("   [OK] Increased interest rate to 8%")

    # Run a few more steps
    print("\n4. Running 5 more steps with new policies...")
    for i in range(5):
        metrics = model.step()
        print(
            f"   Step {i + 1}: GDP=${metrics['gdp']:,.0f}, "
            f"Unemployment={metrics['unemployment']:.1f}%"
        )
        _print_narrative(metrics)

    print("\n5. Testing crisis scenario...")
    model.trigger_crisis('recession')
    print("   [OK] Triggered recession")

    metrics = model.step()
    print(
        f"   After crisis: Unemployment={metrics['unemployment']:.1f}%, "
        f"Interest Rate={metrics['interest_rate']:.2f}%"
    )
    _print_narrative(metrics)

    print("\n" + "=" * 60)
    print("All tests passed! [OK]")
    print("You can now run: python main.py")
    print("=" * 60)


if __name__ == '__main__':
    test_basic_simulation()
