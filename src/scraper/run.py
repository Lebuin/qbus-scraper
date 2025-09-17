#!/usr/bin/env python3
"""
Startup script for the Qbus scraper application.
"""

import logging
import os
import sys

# Add the parent directory to the Python path so we can import from scraper
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scraper.app import run_app


def main():
    """Main entry point for the application."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)

    # Start the application
    logger.info("Starting Qbus scraper application...")

    run_app()

if __name__ == '__main__':
    main()
