# Pytest automatically discovers conftest.py and makes its fixtures available to tests in the same directory and its subdirectories.
# A test requests a fixture by naming it as a parameter, such as def test_overview(admin_driver), without importing it.

import os
import json
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Get the dashboard URL, defaulting to localhost, and remove any trailing slash.
# To set the enviroment variable for the dashboard URL, run this command below before running the test:
# $env:DASHBOARD_URL = "https://dashboard-311-537729300096.us-west1.run.app/"
@pytest.fixture
def base_url():
    return os.getenv("DASHBOARD_URL", "http://localhost:4200").rstrip("/")


# Load admin credentials from the JSON file beside conftest.py once per test session.
@pytest.fixture(scope="session")
def admin_credentials():
    path = Path(__file__).with_name("admin_credentials.json")
    with path.open(encoding="utf-8") as file:
        return json.load(file)


# Open a fresh Chrome browser for the test and close it during teardown.
@pytest.fixture
def driver():
    browser = webdriver.Chrome()
    try:
        yield browser
    finally:
        browser.quit()


# Sign in with the admin credentials and return the browser after it reaches Overview.
@pytest.fixture
def admin_driver(driver, base_url, admin_credentials):
    driver.get(f"{base_url}/login")
    wait = WebDriverWait(driver, 15)

    email = (By.ID, "email")
    password = (By.ID, "password")
    submit = (By.CSS_SELECTOR, 'button[type="submit"]')

    wait.until(EC.visibility_of_element_located(email)).send_keys(
        admin_credentials["USERNAME"]
    )
    wait.until(EC.visibility_of_element_located(password)).send_keys(
        admin_credentials["PASSWORD"]
    )
    wait.until(EC.element_to_be_clickable(submit)).click()

    wait.until(
        EC.url_to_be(f"{base_url}/overview"),
        message="Expected the dashboard to open /overview after sign-in.",
    )
    return driver


# pytest only collects files that match its python_files pattern (test_*.py by
# default), which would skip the script-style Selenium suite in sel_phones.py
# during a plain `pytest` run. Collect it explicitly in that case; when the file
# is passed on the command line pytest already collects it, so skip it then to
# avoid registering the test twice.
def pytest_collect_file(file_path, parent):
    is_phones_suite = (
        file_path.name == "sel_phones.py"
        and file_path.parent == Path(__file__).parent
    )
    if is_phones_suite and not parent.session.isinitpath(file_path):
        return pytest.Module.from_parent(parent, path=file_path)
    return None
