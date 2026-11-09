import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

# The canonical phone number format produced by the PhonePipe (frontend/src/pipes/phone.pipe.ts):
# (916) 555-1234
PHONE_PATTERN = re.compile(r"^\(\d{3}\) \d{3}-\d{4}$")

# How long to wait for a page to finish fetching its records. The sessions page
# loads from Google Agent Engine, so it can be noticeably slower than contacts.
CONTENT_TIMEOUT = 30

# Initialize Chrome WebDriver.
driver = webdriver. Chrome()

# Open the login page.
driver.get("http://localhost:4200/login")
sleep(1)

#helper function for inputs within the SAME driver so it does not look for a global driver. 
def uniWebDriverAction(driver, locator, input_value = None):
    item = WebDriverWait(driver,10).until(
        EC.presence_of_element_located(locator)
    )
    sleep(1)

# if there is no input, it will click a button. If there is input, it will type it out
    if (input_value is not None):
        for char in range(0, len(input_value)):
            item.send_keys(input_value[char])
            sleep(0.1)
    else:
        item.click()
    sleep(1)


# Waits for a page to finish loading, then returns its table.
# Both pages show a loading spinner before the table appears, so the empty state
# and the error state are accepted as valid end states and reported as a missing table.
def waitForTable(driver, page_name):
    WebDriverWait(driver, CONTENT_TIMEOUT).until(
        lambda d: d.find_elements(By.TAG_NAME, "table")
        or d.find_elements(By.CSS_SELECTOR, ".empty-state")
    )

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


# Asserts that every value in a page's Phone Number column uses the (XXX) XXX-XXXX format.
def assertPhoneFormats(driver, page_name):
    table = waitForTable(driver, page_name)
    phones = columnValues(table, "Phone Number", page_name)

    assert phones, f"{page_name}: the Phone Number column had no rows to verify."

    for phone in phones:
        assert phone, f"{page_name}: a Phone Number cell was empty."

        assert PHONE_PATTERN.match(phone), (
            f"{page_name}: '{phone}' is not displayed as (XXX) XXX-XXXX. "
            "The PhonePipe formats 10-digit US numbers, and 11-digit numbers that start with 1, "
            "while every other value is shown unchanged."
        )

        # The pipe strips the country code, so a leading '+' means it was not applied.
        assert not phone.startswith("+"), (
            f"{page_name}: '{phone}' still has a leading '+' instead of being formatted."
        )

        # The backend stores user ids such as 9165551234-sms; the suffix must not reach the table.
        assert "-sms" not in phone, (
            f"{page_name}: '{phone}' still contains the raw '-sms' user id suffix."
        )

    print(f"Passed! {len(phones)} phone number(s) on the {page_name} use the (XXX) XXX-XXXX format.")
    return phones


# Log in credentials  and logging in
uniWebDriverAction(driver, (By.ID, "email"), "admin@sacramento.org")
uniWebDriverAction(driver, (By.ID, "password"), "admin!")
uniWebDriverAction(driver, (By.ID, "loginButton"), None)

# << CONTACTS PAGE PHONE FORMATS >>

# Going to contacts page
uniWebDriverAction(driver, (By.CSS_SELECTOR, "a[routerLink='/contacts']"), None)
sleep(2)

contact_phones = assertPhoneFormats(driver, "contacts page")

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

assert PHONE_PATTERN.match(heading_phone), (
    f"single contact sessions page: the heading shows '{heading_phone}', "
    "which is not the (XXX) XXX-XXXX format."
)

# The same contact must render the same number on both pages.
assert phoneDigits(heading_phone) == phoneDigits(contact_phones[0]), (
    f"The contacts table showed '{contact_phones[0]}', but the sessions heading showed "
    f"'{heading_phone}'. Both should display the same phone number."
)

print(f"Passed! The single contact sessions heading displays '{heading}'.")

# The phone number column is intentionally hidden when viewing a single contact's sessions.
session_tables = driver.find_elements(By.TAG_NAME, "table")
if session_tables:
    assert "Phone Number" not in tableHeaders(session_tables[0]), (
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
assert phoneDigits(contact_phones[0]) in session_phone_digits, (
    f"The contacts page showed '{contact_phones[0]}', but that number was not found among the "
    f"phone numbers on the all sessions page: {session_phones}."
)

print("Passed!")

# Kill process
driver.quit()