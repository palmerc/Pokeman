import requests
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth

class Browser(object):
    def __new__(cls):
        if not hasattr(cls, 'shared_instance'):
            cls.shared_instance = super(Browser, cls).__new__(cls)
        return cls.shared_instance

    def __init__(self):
        options = Options()
        options.add_argument('--headless=new')

        service = Service()
        self._driver = webdriver.Chrome(chrome_options=options, service=service)
        stealth(self._driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,)

    def get(self, url) -> str:
        self._driver.get(url)
        return self._driver.page_source

    def get_file(self, url):
        return requests.get(url).content
