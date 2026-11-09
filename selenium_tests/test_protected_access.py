# - Tests direct access while signed out, running one case for each of seven protected pages: Overview, Profile, Agent Chat, Contacts, Sessions, Session Details, and the Messages tab.
# - Verifies that each URL redirects to `/login` and displays the email and password fields.
# - Logs out from Contacts, then uses the browser’s Back and Forward buttons to verify that the login form is visible after each action.

import pytest
from urllib.parse import urlsplit

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Actual session ID that exist in the Agent Runtime db.
SESSION_ID = "14474520823857152"

PROTECTED_URLS = [
    pytest.param("/overview", id="overview"),
    pytest.param("/profile", id="profile"),
    pytest.param("/agent-chat", id="agent-chat"),
    pytest.param("/contacts", id="contacts"),
    pytest.param("/sessions", id="sessions"),
    pytest.param(f"/sessions/{SESSION_ID}", id="session-details"),
    pytest.param(f"/sessions/{SESSION_ID}?tab=messages", id="messages"),
]


# Helper function to check that the browser reached /login and the login form is visible.
def check_login_page(driver):
    wait = WebDriverWait(driver, 15)
    wait.until(
        lambda browser: urlsplit(browser.current_url).path.rstrip("/") == "/login",
        message="Expected the browser to redirect to /login.",
    )
    wait.until(EC.visibility_of_element_located((By.ID, "email")))
    wait.until(EC.visibility_of_element_located((By.ID, "password")))


# 2 tests defined below:
# Open each protected URL directly in a fresh, signed-out browser.
# @pytest.mark.parametrize makes it run once for each protected URL.
@pytest.mark.parametrize("path", PROTECTED_URLS)
def test_signed_out_user_is_redirected_to_login(driver, base_url, path):
    driver.get(f"{base_url}{path}")  # Open URL
    check_login_page(driver)  # Check that it doesn't open


# Verify that browser history does not reopen the dashboard after logout.
def test_back_and_forward_after_logout(admin_driver, base_url):
    driver = admin_driver
    wait = WebDriverWait(driver, 15)

    # Visit another protected page so the browser has dashboard history.
    driver.get(f"{base_url}/contacts")
    wait.until(EC.element_to_be_clickable((By.ID, "logout-btn"))).click()
    check_login_page(driver)

    driver.back()
    check_login_page(driver)

    driver.forward()
    check_login_page(driver)
