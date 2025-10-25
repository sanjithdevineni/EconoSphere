"""
Main entry point for MacroEcon Simulator
"""

from dashboard.app import create_dashboard
import config


def main():
    """Launch the dashboard"""
    print("=" * 60)
    print("MacroEcon Simulator")
    print("=" * 60)
    print(f"\nInitializing simulation with:")
    print(f"  - {config.NUM_CONSUMERS} consumers")
    print(f"  - {config.NUM_FIRMS} firms")
    print(f"  - Tax rate: {config.INITIAL_TAX_RATE * 100}%")
    print(f"  - Interest rate: {config.INITIAL_INTEREST_RATE * 100}%")
    print(f"\nStarting dashboard on http://localhost:{config.PORT}")
    print("=" * 60)

    app = create_dashboard()
    app.run_server(debug=config.DEBUG_MODE, port=config.PORT)


if __name__ == '__main__':
    main()
