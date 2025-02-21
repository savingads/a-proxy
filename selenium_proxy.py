from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_vpn_browser(language="en-US"):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument(f'--lang={language}')
    options.binary_location = "/usr/bin/google-chrome"

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver
