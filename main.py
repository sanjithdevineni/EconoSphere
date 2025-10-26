"""
Main entry point for MacroEcon Simulator
"""

import logging
import os
from dashboard.app import create_dashboard
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(name)s: %(message)s'
)

# Create app instance at module level for WSGI servers (Azure, Gunicorn, etc.)
app = create_dashboard()
server = app.server  # Flask server instance for Azure Web Apps


def main():
    """Launch the dashboard"""
    print("=" * 60)
    print("MacroEcon Simulator")
    print("=" * 60)
    print(f"\nInitializing simulation with:")
    print(f"  - {config.NUM_CONSUMERS} consumers")
    print(f"  - {config.NUM_FIRMS} firms")
    print(f"  - VAT rate: {config.INITIAL_VAT_RATE * 100}%")
    print(f"  - Payroll tax: {config.INITIAL_PAYROLL_RATE * 100}%")
    print(f"  - Corporate tax: {config.INITIAL_CORPORATE_RATE * 100}%")
    print(f"  - Interest rate: {config.INITIAL_INTEREST_RATE * 100}%")
    
    # Get port from environment (Azure sets this) or use default
    port = int(os.environ.get('PORT', config.PORT))
    print(f"\nStarting dashboard on http://localhost:{port}")
    print("=" * 60)

    app.run(debug=config.DEBUG_MODE, port=port, host='0.0.0.0')


if __name__ == '__main__':
    main()
