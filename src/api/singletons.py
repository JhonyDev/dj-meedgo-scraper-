from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class WebDriverCache:
    _cached_webdriver = None

    @classmethod
    def get_webdriver(cls):
        if cls._cached_webdriver is None:
            options = Options()
            options.add_argument('--headless')
            options.add_argument("--force-device-scale-factor=0.5")
            cls._cached_webdriver = webdriver.Chrome(options=options)
        return cls._cached_webdriver
