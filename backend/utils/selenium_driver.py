"""
Selenium WebDriver management for Comparekart.
Provides a singleton pattern for WebDriver with anti-detection measures.
"""

import logging
import random
import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)


class SeleniumDriver:
    """Manages Selenium WebDriver with singleton pattern."""

    _instance: Optional["SeleniumDriver"] = None
    _driver: Optional[webdriver.Chrome] = None
    _consecutive_failures: int = 0
    _disabled_until_ts: float = 0.0
    _disable_seconds: int = 90

    def __new__(cls) -> "SeleniumDriver":
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(SeleniumDriver, cls).__new__(cls)
        return cls._instance

    def get_driver(self) -> webdriver.Chrome:
        """
        Get or create Chrome WebDriver with anti-detection measures.

        Returns:
            Configured Chrome WebDriver instance
        """
        if self._disabled_until_ts > time.time():
            raise RuntimeError("Selenium temporarily disabled due to recent failures")

        if self._driver is None:
            self._driver = self._create_driver()
        return self._driver

    def _create_driver(self) -> webdriver.Chrome:
        """
        Create Chrome WebDriver with stealth configurations.

        Returns:
            Configured Chrome WebDriver
        """
        options = Options()
        options.page_load_strategy = "eager"

        # Headless mode for faster performance
        options.add_argument("--headless=new")

        # Anti-detection measures
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # Additional performance options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        # Disable unnecessary features
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-extensions")

        # User agent rotation
        user_agent = self._get_random_user_agent()
        options.add_argument(f"user-agent={user_agent}")

        try:
            # Prefer Selenium Manager (bundled with Selenium 4.6+) for reliable
            # driver resolution on Windows architecture variants.
            try:
                driver = webdriver.Chrome(options=options)
                logger.info("Selenium WebDriver initialized via Selenium Manager")
            except Exception as selenium_manager_error:
                logger.warning(
                    f"Selenium Manager init failed, falling back to webdriver-manager: {selenium_manager_error}"
                )
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                logger.info("Selenium WebDriver initialized via webdriver-manager")

            # Best-effort anti-detection tweaks
            try:
                driver.execute_cdp_cmd(
                    "Page.addScriptToEvaluateOnNewDocument",
                    {
                        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
                    },
                )
            except Exception as e:
                logger.debug(f"Could not apply webdriver masking script: {e}")

            # Set timeouts
            driver.set_page_load_timeout(15)
            driver.implicitly_wait(10)

            logger.info("Selenium WebDriver initialized successfully")
            self._consecutive_failures = 0
            return driver

        except Exception as e:
            logger.error(f"Failed to create WebDriver: {str(e)}")
            raise

    @staticmethod
    def _get_random_user_agent() -> str:
        """
        Get a random user agent string.

        Returns:
            Random user agent string
        """
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
        ]
        return random.choice(user_agents)

    def close(self) -> None:
        """Close WebDriver if open."""
        if self._driver:
            try:
                self._driver.quit()
                self._driver = None
                logger.info("Selenium WebDriver closed")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {str(e)}")

    def get_page_source(
        self, url: str, wait_for_element: Optional[tuple[By, str]] = None, timeout: int = 10
    ) -> Optional[str]:
        """
        Get page source with optional wait for element.

        Args:
            url: URL to fetch
            wait_for_element: Tuple of (By, selector) to wait for
            timeout: Timeout in seconds

        Returns:
            Page source HTML or None
        """
        try:
            driver = self.get_driver()

            # Random delay to mimic human behavior
            time.sleep(random.uniform(0.5, 1.5))

            driver.get(url)
            logger.info(f"Page loaded: {url}")

            # Wait for specific element if provided
            if wait_for_element:
                try:
                    WebDriverWait(driver, timeout).until(
                        EC.presence_of_all_elements_located(wait_for_element)
                    )
                    logger.info(f"Element found: {wait_for_element[1]}")
                except TimeoutException:
                    logger.warning(f"Timeout waiting for element {wait_for_element[1]}: {url}")
                    # Still try to return page source even if element not found
                    # (it might be dynamically loaded or structure changed)

            # Wait for dynamic content
            time.sleep(random.uniform(1, 2))

            page_source = driver.page_source
            logger.info(f"Page source retrieved, length: {len(page_source) if page_source else 0}")
            self._consecutive_failures = 0
            return page_source

        except TimeoutException:
            logger.warning(f"Page load timeout: {url}")
            # Try to return partial page source
            try:
                return driver.page_source
            except:
                return None
        except Exception as e:
            logger.error(f"Error fetching page {url}: {str(e)}")

            self._consecutive_failures += 1
            lowered = str(e).lower()
            if "invalid session id" in lowered:
                self.close()

            if self._consecutive_failures >= 3:
                self._disabled_until_ts = time.time() + self._disable_seconds
                logger.warning(
                    "Selenium temporarily disabled for %s seconds after repeated failures",
                    self._disable_seconds,
                )
            return None

    def __del__(self) -> None:
        """Clean up WebDriver on deletion."""
        self.close()


def get_selenium_driver() -> SeleniumDriver:
    """
    Get singleton Selenium driver instance.

    Returns:
        SeleniumDriver instance
    """
    return SeleniumDriver()
