import logging
import signal
import sys

from flask import Flask, jsonify, request
from flask_basicauth import BasicAuth

from . import config, scraper

# Configure logging
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Basic Auth configuration from config.py
app.config['BASIC_AUTH_USERNAME'] = config.BASIC_AUTH_USERNAME
app.config['BASIC_AUTH_PASSWORD'] = config.BASIC_AUTH_PASSWORD
app.config['BASIC_AUTH_FORCE'] = True
basic_auth = BasicAuth(app)


@app.route('/data', methods=['GET'])
@basic_auth.required
def get_data():
    """Endpoint to scrape and return page data."""
    try:
        s = scraper.QbusScraper()
        data = s.scrape_page_data()
        return jsonify(data)

    except scraper.ScrapeError as e:
        logger.error(f"Error scraping data: {e}")
        return jsonify({'error': str(e), 'page_source': e.page_source}), 500
    except Exception as e:
        logger.error(f"Error scraping data: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        s.cleanup()


def run_app():
    """Run the Flask application."""
    logger.info("Starting Flask server...")
    app.run(host='0.0.0.0', port=5000, debug=(config.ENVIRONMENT == 'dev'))
