import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def configurar_driver(user_data_dir=None):
    options = Options()
    if user_data_dir:
        options.add_argument(f"user-data-dir={user_data_dir}")
    else:
        options.add_argument("user-data-dir=default_profile")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    return webdriver.Chrome(options=options)
