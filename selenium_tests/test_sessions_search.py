from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import json
import time
from pathlib import Path


# Resolve the credentials file beside this test so it works from any directory.
CREDENTIALS_PATH = Path(__file__).with_name("admin_credentials.json")

# Sessions are fetched live from Google Agent Engine through the Flask backend,
# which can be slow, so allow a generous window and retry a failed request.
SESSIONS_TIMEOUT = 90
MAX_SESSIONS_RELOADS = 2

# Text the frontend renders when the sessions request to the backend fails.
SESSIONS_ERROR_TEXT = "Unable to load sessions"


# Return every row currently rendered in the sessions table.
def get_session_rows(driver):
    return driver.find_elements(By.XPATH, "//table[@id='session-table']/tbody/tr")


# Return the session ID (first cell) of every row currently rendered.
def get_session_ids(driver):
    return [
        row.find_element(By.XPATH, "./td").text.strip()
        for row in get_session_rows(driver)
    ]


# True once the table shows at least one row and every visible row matches the query.
def only_matching_ids(driver, query):
    session_ids = get_session_ids(driver)
    return bool(session_ids) and all(
        query.lower() in session_id.lower() for session_id in session_ids
    )


# Replace the search bar contents with the query (an empty query just clears it).
# A plain clear() does not update Angular's ngModel, so a real keystroke is used.
def type_in_search(driver, query):
    search_box = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "search"))
    )
    search_box.send_keys(Keys.CONTROL, "a")
    search_box.send_keys(Keys.DELETE)
    if query:
        search_box.send_keys(query)
    return search_box


# Wait until the sessions page has loaded its data from the backend and return
# the loaded session IDs. The page fetches sessions asynchronously; if that
# request fails it shows an error instead of the table, so the page is reloaded
# (which re-issues the request) a few times before the test gives up.
def load_sessions_from_backend(driver):
    # The backend failure message is rendered in an element with role="alert".
    error_locator = (By.CSS_SELECTOR, "p.empty-state[role='alert']")

    deadline = time.monotonic() + SESSIONS_TIMEOUT
    reloads = 0

    while time.monotonic() < deadline:
        # A populated table means the backend request succeeded.
        session_ids = get_session_ids(driver)
        if session_ids:
            return session_ids

        # A backend error means the request failed; reload the page to retry it.
        errors = driver.find_elements(*error_locator)
        if errors and SESSIONS_ERROR_TEXT in errors[0].text:
            if reloads >= MAX_SESSIONS_RELOADS:
                break
            reloads += 1
            print(
                f"Backend did not return sessions (retry {reloads}); "
                "reloading the page..."
            )
            driver.refresh()
            sleep(2)

        sleep(0.5)

    raise AssertionError(
        "Test Failed: sessions data did not load from the backend. "
        "Ensure the Flask backend and Google Agent Engine are reachable."
    )


def test_session_sorting():
    driver = webdriver.Chrome()

    try:
        # Open the login page and sign in.
        driver.get("http://localhost:4200/login")

        email_box = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.NAME, "emailLogin"))
        )

        with open(CREDENTIALS_PATH, "r") as login_credentials:
            login_json = json.load(login_credentials)

        email_box.send_keys(login_json["USERNAME"])
        driver.find_element(By.NAME, "passLogin").send_keys(login_json["PASSWORD"])
        driver.find_element(By.ID, "loginButton").click()

        # Wait for the dashboard to load, then open the Sessions page.
        WebDriverWait(driver, 15).until(EC.url_contains("/overview"))

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[routerLink='/sessions']"))
        ).click()

        # Wait for the page to actually fetch the sessions data from the backend.
        all_session_ids = load_sessions_from_backend(driver)
        assert all_session_ids, "Test Failed: no sessions available to search!"

        # --- Search bar ---
        # Search with a substring of a real session ID to exercise partial matching.
        query = all_session_ids[0][-4:]
        type_in_search(driver, query)

        # Wait until the table only shows rows whose session ID contains the query.
        WebDriverWait(driver, 10).until(lambda d: only_matching_ids(d, query))

        filtered_ids = get_session_ids(driver)
        assert filtered_ids, f"Test Failed: search '{query}' returned no sessions!"

        for session_id in filtered_ids:
            assert query.lower() in session_id.lower(), (
                f"Test Failed: '{session_id}' does not match search '{query}'!"
            )

        print(
            f"Search '{query}' matched {len(filtered_ids)} of "
            f"{len(all_session_ids)} sessions."
        )

        # A query that cannot match anything should show the empty state message.
        type_in_search(driver, "no-such-session-xyz")

        WebDriverWait(driver, 10).until(lambda d: len(get_session_rows(d)) == 0)

        empty_state = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".empty-state"))
        )
        assert "No sessions match the current search" in empty_state.text, (
            "Test Failed: empty state message missing for a non-matching search!"
        )
        print("Non-matching search correctly showed the empty state message.")

        # Clearing the search should bring every session back.
        type_in_search(driver, "")
        WebDriverWait(driver, 10).until(
            lambda d: len(get_session_ids(d)) == len(all_session_ids)
        )
        print(f"Clearing the search restored all {len(all_session_ids)} sessions.")

        # --- Outcome filter (existing coverage) ---
        # The filter stays disabled until the evaluations finish loading.
        outcome_filter = WebDriverWait(driver, SESSIONS_TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "outcome-filter"))
        )

        sessions_selector = Select(outcome_filter)
        sessions_selector.select_by_index(0)
        sessions_selector.select_by_index(1)
        sessions_selector.select_by_index(2)
        sessions_selector.select_by_index(3)

        # Reset the filter to "All Sessions" so the page is left in its default state.
        sessions_selector.select_by_index(0)

    finally:
        # Close the browser once the test finishes, whether it passed or failed.
        driver.quit()
