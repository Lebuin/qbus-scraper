import json
import logging
import os
import re
import threading
import time
from datetime import datetime
from typing import Any, Dict, Optional

from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from . import config

logger = logging.getLogger(__name__)

class ScrapeError(Exception):
    """Exception raised when a scrape operation fails."""
    def __init__(self, message: str | Exception, page_source: str):
        super().__init__(message)
        soup = bs(page_source, 'html.parser')
        self.page_source = soup.prettify()


class QbusScraper:
    """Handles browser management and scraping of the Qbus dashboard."""

    def __init__(self):
        self.browser: Optional[WebDriver] = None


    def __del__(self):
        self.cleanup()


    def cleanup(self):
        """Clean up resources."""
        self.quit_browser()


    def initialize_browser(self):
        if self.browser is not None:
            raise Exception('Browser already initialized')

        """Initialize the browser and load the Qbus page."""
        try:
            logger.info('Initializing browser...')
            options = FirefoxOptions()
            self.browser = webdriver.Remote(
                command_executor=f'http://{config.SELENIUM_HOST}/wd/hub',
                options=options
            )

            logger.info(f'Loading Qbus page: {config.QBUS_URL}')
            self.browser.get(config.QBUS_URL)


            logger.info('Browser initialized successfully')

        except Exception as e:
            logger.error(f'Failed to initialize browser: {e}')
            self.quit_browser()
            raise


    def quit_browser(self):
        if self.browser is not None:
            self.browser.quit()
            self.browser = None


    def get_browser(self) -> WebDriver:
        """Get the browser instance."""
        if self.browser is None:
            self.initialize_browser()
        assert self.browser is not None, 'Browser not initialized'
        return self.browser


    def raise_scrape_error(self, e: Exception):
        try:
            browser = self.get_browser()
            e = ScrapeError(e, browser.page_source)
        except Exception as inner_e:
            logger.error(f'Error raising scrape error: {inner_e}')
        raise e


    def wait_for_page_to_be_ready(self):
        browser = self.get_browser()

        """Wait for the page to be ready."""
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'ion-app'))
        )


    def check_and_handle_cookie_consent(self):
        """Check if cookie consent is required and handle it if necessary."""
        try:
            browser = self.get_browser()
            self.wait_for_page_to_be_ready()
            cookie_consent_selector = config.SELECTORS['cookie_consent']['accept']
            cookie_consent_element = WebDriverWait(browser, 1).until(
                EC.presence_of_element_located(cookie_consent_selector)
            )
            cookie_consent_element.click()
        except TimeoutException:
            pass


    def check_and_handle_login(self):
        """Check if login is required and handle it if necessary."""

        try:
            browser = self.get_browser()
            self.wait_for_page_to_be_ready()

            # Check if login form is present
            username_selector = config.SELECTORS['login']['username']
            username_element = WebDriverWait(browser, 1).until(
                EC.presence_of_element_located(username_selector)
            )

            logger.info('Login form detected, attempting to log in...')

            # Fill in username
            username_element.clear()
            username_element.send_keys(config.QBUS_USERNAME)

            # Fill in password
            password_selector = config.SELECTORS['login']['password']
            password_element = browser.find_element(*password_selector)
            password_element.clear()
            password_element.send_keys(config.QBUS_PASSWORD)

            # Submit the form
            submit_selector = config.SELECTORS['login']['submit']
            submit_button = browser.find_element(*submit_selector)
            submit_button.click()

            # Wait for login to complete (either success or failure)
            WebDriverWait(browser, 10).until(
                lambda driver: not self.is_login_form_present(browser)
            )

            logger.info('Login completed successfully')

        except TimeoutException:
            # Login form not present, we're already logged in
            logger.debug('No login form found, already logged in')


    def is_login_form_present(self, browser: WebDriver):
        """Check if the login form is still present on the page."""

        try:
            username_selector = config.SELECTORS['login']['username']
            browser.find_element(*username_selector)
            return True
        except:
            return False


    def scrape_page_data(self) -> Dict[str, Any]:
        """Scrape data from the currently loaded page."""
        try:
            self.check_and_handle_cookie_consent()
            self.check_and_handle_login()
            browser = self.get_browser()

            # Wait for the page to load
            logger.info('Waiting for page to load...')
            time.sleep(2)

            logger.info('Scraping page data...')
            data = self.do_scrape_page_data(browser)
            return data

        except TimeoutException:
            self.raise_scrape_error(Exception('Page load timeout'))
        except WebDriverException as e:
            self.raise_scrape_error(e)


    def do_scrape_page_data(self, browser: WebDriver):
        selectors = config.SELECTORS['main']

        section_titles = WebDriverWait(browser, 5).until(
            EC.presence_of_all_elements_located(selectors['section_title'])
        )
        sections = browser.find_elements(*selectors['section'])


        tiles_data = {}
        for (section_title, section) in zip(section_titles, sections):
            section_title.click()
            time.sleep(1)

            tiles = section.find_elements(*selectors['tile'])
            for tile in tiles:
                try:
                    elem_name = tile.find_element(*selectors['tile_name'])
                    elems_value = tile.find_elements(*selectors['tile_value'])
                    elems_binary_true = tile.find_elements(*selectors['tile_binary_true'])
                    elems_binary_false = tile.find_elements(*selectors['tile_binary_false'])

                    name = elem_name.text
                    value = None
                    if len(elems_value) > 0:
                        value_str = elems_value[0].text
                        match = re.search(r'[\d.]+', value_str)
                        if match:
                            value = float(match.group(0))
                    elif len(elems_binary_true) > 0:
                        value = True
                    elif len(elems_binary_false) > 0:
                        value = False

                    if value is not None:
                        tiles_data[name] = value
                except WebDriverException:
                    pass

        return {
            'timestamp': datetime.now().isoformat(),
            'values': tiles_data,
        }


# Global scraper instance
scraper = QbusScraper()
