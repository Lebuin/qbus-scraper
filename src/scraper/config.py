import logging
import os
from datetime import timedelta

from selenium.webdriver.common.by import By, ByType

LOG_LEVEL = os.environ.get('LOG_LEVEL', logging.INFO)
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'prod')

BASIC_AUTH_USERNAME = os.environ['BASIC_AUTH_USERNAME']
BASIC_AUTH_PASSWORD = os.environ['BASIC_AUTH_PASSWORD']

# Qbus login credentials
QBUS_USERNAME = os.environ.get('QBUS_USERNAME', '')
QBUS_PASSWORD = os.environ.get('QBUS_PASSWORD', '')

# How to reach selenium. If developing outside the docker container you will want to override this
# in your .env file.
SELENIUM_HOST = os.environ.get('SELENIUM_HOST', 'selenium:4444')

# The URL of the Qbus page
QBUS_URL = 'https://qbuscontrol.com/app/tabs/dashboard'

# The Qbus page gets live updates over websockets. We keep the page open permanently and scrape its
# content whenever we get a request. To avoid things like memory leaks, we periodically reload the
# page.
RELOAD_INTERVAL = timedelta(hours=1)

# Cookie persistence
COOKIE_JAR_PATH = os.environ.get('COOKIE_JAR_PATH', '/tmp/qbus_cookies.json')

# All the selectors used to scrape the page
SELECTORS: dict[str, dict[str, tuple[ByType, str]]] = {
    'cookie_consent': {
        'accept': (By.CSS_SELECTOR, 'ccl-cookie-consent .button'),
    },
    'login': {
        'username': (By.CSS_SELECTOR, 'ion-input[formcontrolname="username"] input'),
        'password': (By.CSS_SELECTOR, 'ion-input[formcontrolname="password"] input'),
        'submit': (By.CSS_SELECTOR, 'ion-button[type="submit"]'),
    },
    'main': {
        'section_title': (By.CSS_SELECTOR, 'ccl-segment-button'),
        'section': (By.CSS_SELECTOR, 'ccl-dashboard-group'),
        'tile': (By.CSS_SELECTOR, 'ccl-icon1x1, ccl-icon2x2'),
        'tile_name': (By.CSS_SELECTOR, '.name, .text-container > :not(.status-to-show)'),
        'tile_value': (By.CSS_SELECTOR, '.value, .text-container > .status-to-show'),
    }
}
