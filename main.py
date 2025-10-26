"""
Main entry point for MacroEcon Simulator
"""

import logging
import os
import sys
import traceback
from flask import Flask

# Configure logging - explicitly to stdout for Azure
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(name)s: %(message)s',
    stream=sys.stdout,
    force=True
)

logger = logging.getLogger(__name__)

# Create fallback Flask app in case of errors
fallback_app = Flask(__name__)

@fallback_app.route('/')
def fallback():
    return "<h1>EconoSphere is initializing...</h1><p>If you see this, check the application logs.</p>"

try:
    logger.info("="*60)
    logger.info("Initializing EconoSphere...")
    logger.info("="*60)
    
    import config
    logger.info("✓ Config imported")
    
    from dashboard.app import create_dashboard
    logger.info("✓ Dashboard module imported")
    
    # Create app instance at module level for WSGI servers (Azure, Gunicorn, etc.)
    app = create_dashboard()
    logger.info("✓ Dashboard created successfully!")
    
    server = app.server  # Flask server instance for Azure Web Apps
    logger.info("✓ Server ready")
    
except Exception as e:
    logger.error("="*60)
    logger.error("FATAL ERROR DURING STARTUP!")
    logger.error("="*60)
    logger.error(f"Error: {type(e).__name__}: {str(e)}")
    logger.error("Full traceback:")
    for line in traceback.format_exc().split('\n'):
        logger.error(line)
    logger.error("="*60)
    
    # Use fallback app so container doesn't crash
    app = None
    server = fallback_app
    logger.error("Using fallback server - app will show error page")


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
