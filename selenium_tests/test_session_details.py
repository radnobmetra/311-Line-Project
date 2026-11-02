
# Selenium script that tests that:
#   -   selecting a contact displays that contact's sessions
#   -   selecting a row in the contact's sessions displays the session details
#   -   the messages and service requests tabs can be accessed on the session details page

# This script uses a chrome driver.
# Before running this script, you must create a json file, tests/admin_credentials.json,
# that contains username and password values that selenium can use to log in to the 
# dashboard.

# selenium_tests/admin_credentials.json should contain the following:
# {
#     "USERNAME": "admin username goes here", 
#     "PASSWORD": "admin password goes here"
# }

# To run the script, run this command from the selenium_tests folder:
#       python test_session_details.py

# To run pytest, run this command from the selenium_tests folder:
#   python -m pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json


def test_session_details():

    #---------------- creating the web driver and logging in ------------------

    #get admin credentials from json file
    try:
        with open('admin_credentials.json','r') as f:
            credentials = json.load(f)
        USERNAME = credentials['USERNAME']
        PASSWORD = credentials['PASSWORD']
    except: 
        print("error: tests/admin_credentials.json does not exist or is" \
        "incorrectly formatted.")
        assert False

    #create driver and wait
    driver = setup()
    wait = WebDriverWait(driver, timeout=5)

    #assert that driver is on login page 
    wait.until(lambda _: driver.current_url == "http://localhost:4200/login")
    print("On login page. Attempting to log in...")

    #get username and password fields
    usernameField = driver.find_element(By.NAME, "emailLogin")
    passwordField = driver.find_element(By.NAME, "passLogin")

    #enter username and password
    usernameField.send_keys(USERNAME)
    passwordField.send_keys(PASSWORD)

    #click login button
    login_button = driver.find_element(By.TAG_NAME, "button")
    login_button.click()

    #wait until driver is on overview page
    try:
        wait.until(lambda _: driver.current_url == "http://localhost:4200/overview")
    except:
        print("Login to the admin dashboard was unsuccessful. Make sure that " \
        "tests/admin_credentials.json contains valid credentials.")
        teardown(driver)
        assert False
    
    print("Logged in successfully. Going to sessions page...")

    #----------------------- going to the sessions page -----------------------

    #get nav bar element
    navbar = driver.find_element(By.CLASS_NAME, "sidebar")

    # find the link to the sessions page and follow it
    navbar_link = navbar.find_element(By.LINK_TEXT, "Sessions")
    navbar_link.click()
    wait.until(lambda _: driver.current_url == "http://localhost:4200/sessions")
    print("Sessions page loaded successfully. Clicking on the first session...")

    #-------------------- go to the session details page ----------------------

    #click on the first session in the table
    clickable_row = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "clickable-row")))
    clickable_row.click()
    #wait for the session details page to load
    wait.until(lambda _: driver.current_url.startswith("http://localhost:4200/session-details/"))
    print("Session details loaded successfully. Confirming that messages tab works...")

    #----------------------------- go to messages tab -------------------------
    
    tabs = driver.find_element(By.CLASS_NAME, "tabs")
    messages_tab = tabs.find_element(By.LINK_TEXT, "Messages")
    messages_tab.click()

    # ------ confirm that messages page loads and tab title is correct --------

    #find tab title and confirm that we're on the session log tab
    tab_header = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "title-btn")))
    tab_title = tab_header.find_element(By.TAG_NAME, "h1").text
    assert tab_title == "Session Log"

    #confirm that message page loads
    messages_page = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "messages-page")))
    
    print("Messages tab on session details page loaded successfully.")

    #------------- confirm that export button exists on messages tab ----------

    export_btn = tab_header.find_elements(By.CLASS_NAME, "export-btn")
    assert len(export_btn) > 0
    print("Export button exists on messages tab.")

    #-------------- confirm that session log exists on messages tab -----------
    empty_state = None
    try:
        session_log = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "session-log")))
    except:
        session_log = None
    if session_log is None:
        try:
            empty_state = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "empty-state")))
        except: 
            empty_state = None
    assert (session_log is not None) or (empty_state is not None)
    print("Session log or empty state message exists on messages tab.")

    #---------------------- go to service requests tab ------------------------

    requests_tab = tabs.find_element(By.LINK_TEXT, "Service Requests")
    requests_tab.click()

    # ------ confirm that requests page loads and tab title is correct --------

    tab_header = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "title-btn")))
    tab_title = tab_header.find_element(By.TAG_NAME, "h1").text
    assert tab_title == "Service Requests"

    #confirm that service requests page loads
    requests_page = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "service-requests-page")))

    print("Service Requests tab on session details page loaded successfully.")

    #------- confirm that export button exists on service requests tab --------
    
    export_btn = tab_header.find_elements(By.CLASS_NAME, "export-btn")
    assert len(export_btn) > 0

    #---------- list of requests or empty message exists on requests tab ------
    requests_list = None
    try:
        empty_state = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "empty-state")))
    except: 
        empty_state = None
    if empty_state is None:
        try:
            requests_list = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "clickable-row")))
        except:
            requests_list = None
    
    assert (requests_list is not None) or (empty_state is not None)

    print("List of service requests or empty state message exists on service requests tab.")

    # --------------------- "back to sessions" button works -------------------

    back_button = driver.find_element(By.CSS_SELECTOR, '[value="back to sessions"]')
    back_button.click()
    back_button.click()
    wait.until(lambda _: driver.current_url == "http://localhost:4200/sessions")
    print("Back button works.")

    teardown(driver)

def setup():
    # Chrome driver is automatically installed with the newest version of selenium.
    driver = webdriver.Chrome()        
    driver.get("http://localhost:4200")
    return driver


def teardown(driver):
    driver.quit()


if __name__ == "__main__":
    test_session_details()