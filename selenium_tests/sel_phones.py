import re
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

# The canonical phone number format produced by the PhonePipe (frontend/src/pipes/phone.pipe.ts):
# (916) 555-1234
PHONE_PATTERN = re.compile(r"^\(\d{3}\) \d{3}-\d{4}$")

# How long to wait for a page to finish fetching its records from the backend.
# The sessions pages load from Google Agent Engine, so they can be noticeably
# slower than the contacts page.
CONTENT_TIMEOUT = 90

# How many times to reload a page whose backend request failed before giving up.
MAX_RELOADS = 2

# Both pages render this text (inside role="alert") when their backend request fails.
BACKEND_ERROR_PREFIX = "Unable to load"


# helper function for inputs within the SAME driver so it does not look for a global driver.
def uniWebDriverAction(driver, locator, input_value=None):
    item = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(locator)
    )
    sleep(1)

    # if there is no input, it will click a button. If there is input, it will type it out
    if input_value is not None:
        for char in range(0, len(input_value)):
            item.send_keys(input_value[char])
            sleep(0.1)
    else:
        item.click()
    sleep(1)


# Waits for a page to finish fetching its records from the backend, then returns
# its table. Both pages load their data asynchronously; if the backend request
# fails the page renders an error instead of a table, so the page is reloaded
# (which re-issues the request) a few times before the script gives up.
def waitForTable(driver, page_name):
    # The backend failure message is rendered in an element with role="alert".
    error_locator = (By.CSS_SELECTOR, "p.empty-state[role='alert']")

    deadline = time.monotonic() + CONTENT_TIMEOUT
    reloads = 0

    while time.monotonic() < deadline:
        # The backend request succeeded once the table is rendered.
        tables = driver.find_elements(By.TAG_NAME, "table")
        if tables:
            return tables[0]

        # A backend error means the request failed; reload the page to retry it.
        errors = driver.find_elements(*error_locator)
        if errors and errors[0].text.startswith(BACKEND_ERROR_PREFIX):
            if reloads >= MAX_RELOADS:
                break
            reloads += 1
            print(
                f"{page_name}: backend did not return data (retry {reloads}); "
                "reloading the page..."
            )
            driver.refresh()
            sleep(2)
            continue

        # The page settled on a non-error empty state (no records); stop waiting.
        if driver.find_elements(By.CSS_SELECTOR, ".empty-state"):
            break

        sleep(0.5)

    tables = driver.find_elements(By.TAG_NAME, "table")
    assert tables, (
        f"{page_name}: no table was rendered, so phone numbers could not be verified. "
        "Check that the backend is running and that it returned records."
    )
    return tables[0]


# Returns only the data rows of a table, skipping the header row.
def dataRows(table):
    return [
        row for row in table.find_elements(By.TAG_NAME, "tr")
        if row.find_elements(By.TAG_NAME, "td")
    ]


# Returns the header labels of a table, left to right.
def tableHeaders(table):
    return [th.text.strip() for th in table.find_elements(By.TAG_NAME, "th")]


# Returns the displayed value of every row in the column titled header_name.
# Columns are located by their header text instead of a fixed index because the
# sessions page hides the phone number column when it is narrowed to one contact.
def columnValues(table, header_name, page_name):
    headers = tableHeaders(table)

    assert header_name in headers, (
        f"{page_name}: expected a '{header_name}' column, but the table headers were {headers}."
    )

    index = headers.index(header_name)

    values = []
    for row in dataRows(table):
        values.append(row.find_elements(By.TAG_NAME, "td")[index].text.strip())
    return values


# Returns only the digits of a phone number so values can be compared across pages.
def phoneDigits(phone):
    return re.sub(r"\D", "", phone)


# Returns a page's table once it has loaded, or None if the page renders no table
# (for example when a contact has no sessions). Unlike waitForTable this never
# fails, so it can guard an optional check on a page that may be empty. The table
# locator lets callers target a specific table (e.g. the sessions table) so a
# table left over from the previous page is not mistaken for the new page's data.
def findLoadedTable(driver, timeout, table_locator=(By.TAG_NAME, "table")):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.find_elements(*table_locator)
            or d.find_elements(By.CSS_SELECTOR, ".empty-state")
        )
    except TimeoutException:
        return None

    tables = driver.find_elements(*table_locator)
    return tables[0] if tables else None


# Asserts that every value in a page's Phone Number column is a valid phone number.
# Anything that is not displayed as (XXX) XXX-XXXX fails the test, so an invalid
# number (for example a raw user id the PhonePipe could not format) is not ignored.
def assertPhoneFormats(driver, page_name):
    table = waitForTable(driver, page_name)
    phones = columnValues(table, "Phone Number", page_name)

    assert phones, f"{page_name}: the Phone Number column had no rows to verify."

    invalid = [phone for phone in phones if not PHONE_PATTERN.match(phone)]

    assert not invalid, (
        f"{page_name}: found {len(invalid)} invalid phone number(s) that are not "
        f"displayed as (XXX) XXX-XXXX: {invalid}. The PhonePipe formats 10-digit US "
        "numbers and 11-digit numbers that start with 1; every other value is invalid."
    )

    print(
        f"Passed! All {len(phones)} phone number(s) on the {page_name} "
        "use the (XXX) XXX-XXXX format."
    )
    return phones


# pytest entry point: verifies the PhonePipe displays real phone numbers as
# (XXX) XXX-XXXX on both the contacts page and the sessions pages. This is also
# runnable as a script through main() below.
def test_phone_number_formats():
    # Initialize Chrome WebDriver.
    driver = webdriver.Chrome()

    try:
        # Open the login page.
        driver.get("http://localhost:4200/login")
        sleep(1)

        # Log in credentials and logging in
        uniWebDriverAction(driver, (By.ID, "email"), "admin@sacramento.org")
        uniWebDriverAction(driver, (By.ID, "password"), "admin!")
        uniWebDriverAction(driver, (By.ID, "loginButton"), None)

        # << CONTACTS PAGE PHONE FORMATS >>

        # Going to contacts page
        uniWebDriverAction(driver, (By.CSS_SELECTOR, "a[routerLink='/contacts']"), None)
        sleep(2)

        contacts_phones = assertPhoneFormats(driver, "contacts page")

        # << SESSIONS PAGE PHONE FORMATS FOR A SINGLE CONTACT >>

        # Clicking a contact row opens that contact's sessions page, where the phone number
        # is shown in the page heading instead of in a table column.
        first_contact_row = dataRows(waitForTable(driver, "contacts page"))[0]
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(first_contact_row)).click()
        sleep(2)

        heading = WebDriverWait(driver, CONTENT_TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".sessions-page h1"))
        ).text.strip()

        assert heading.startswith("Sessions for "), (
            f"Expected the single contact sessions heading to start with 'Sessions for ', but it was '{heading}'."
        )

        heading_phone = heading[len("Sessions for "):].strip()

        # The heading must show a valid phone number too.
        assert PHONE_PATTERN.match(heading_phone), (
            f"single contact sessions page: the heading shows '{heading_phone}', "
            "which is not a valid (XXX) XXX-XXXX phone number."
        )

        # The same contact must render the same number on both pages.
        assert phoneDigits(heading_phone) == phoneDigits(contacts_phones[0]), (
            f"The contacts table showed '{contacts_phones[0]}', but the sessions heading showed "
            f"'{heading_phone}'. Both should display the same phone number."
        )

        print(f"Passed! The single contact sessions heading displays '{heading}'.")

        # The phone number column is intentionally hidden when viewing a single
        # contact's sessions. Wait for that page's table to load from the backend
        # before checking, and only check when a table was actually rendered
        # (the contact may have no sessions).
        single_contact_table = findLoadedTable(
            driver, CONTENT_TIMEOUT, (By.CSS_SELECTOR, "table#session-table")
        )
        if single_contact_table is not None:
            assert "Phone Number" not in tableHeaders(single_contact_table), (
                "The Phone Number column should be hidden on a single contact's sessions page."
            )
            print("Passed! The phone number column is hidden on a single contact's sessions page.")

        # << ALL SESSIONS PAGE PHONE FORMATS >>

        # Going to sessions page
        uniWebDriverAction(driver, (By.CSS_SELECTOR, "a[routerLink='/sessions']"), None)
        sleep(2)

        session_phones = assertPhoneFormats(driver, "all sessions page")

        # Contacts are derived from sessions, so a contact's phone number must also appear in
        # the sessions table, formatted the same way.
        session_phone_digits = {phoneDigits(phone) for phone in session_phones}
        assert phoneDigits(contacts_phones[0]) in session_phone_digits, (
            f"The contacts page showed '{contacts_phones[0]}', but that number was not found among the "
            f"phone numbers on the all sessions page: {session_phones}."
        )

        print("Passed!")

    finally:
        # Close the browser once the run finishes, whether it passed or failed.
        driver.quit()


# Allows running this file directly (python sel_phones.py). Under pytest the
# test_phone_number_formats() function is collected and called automatically.
def main():
    test_phone_number_formats()


if __name__ == "__main__":
    main()
