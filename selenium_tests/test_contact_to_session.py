
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
#       python test_contact_to_session.py

# To run pytest, run this command from the selenium_tests folder:
#   python -m pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json


def test_contact_to_session():

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
    wait = WebDriverWait(driver, timeout=7)

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
    
    print("Logged in successfully. Going to contacts page...")

    #------------------- navigating to the contacts page ----------------------

    #get nav bar element
    navbar = driver.find_element(By.CLASS_NAME, "sidebar")

    # find the link to the contacts page and follow it
    navbar_link = navbar.find_element(By.LINK_TEXT, "Contacts")
    navbar_link.click()
    wait.until(lambda _: driver.current_url == "http://localhost:4200/contacts")
    print("Contacts page loaded successfully. Going to the sessions page for" \
    " the first contact...")

    #------------- Going to the sessions page for a contact -------------------

    #click on the first contact in the table
    clickable_row = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "clickable-row")))
    clickable_row.click()
    #wait for the sessions page for that contact to load
    wait.until(lambda _: driver.current_url.startswith("http://localhost:4200/sessions/"))
    print("Sessions page for contact loaded successfully. Attempting to load session details" \
    " for the first session...")

    #---------------- Going to a session's contact details --------------------

    clickable_row = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "clickable-row")))
    clickable_row.click()
    wait.until(lambda _: driver.current_url.startswith("http://localhost:4200/session-details/"))
    print("Session details page loaded successfully.")

    #---------------- confirming that messages tab exists ---------------------
    
    tabs = driver.find_element(By.CLASS_NAME, "tabs")
    messages_tab = tabs.find_element(By.LINK_TEXT, "Messages")
    messages_tab.click()
    tab_header = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "title-btn")))
    tab_title = tab_header.find_element(By.TAG_NAME, "h1").text
    assert tab_title == "Session Log"
    print("Messages tab on session details page loaded successfully.")

    #-------------- confirming that service requests tab exists ---------------

    requests_tab = tabs.find_element(By.LINK_TEXT, "Service Requests")
    requests_tab.click()
    tab_header = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "title-btn")))
    tab_title = tab_header.find_element(By.TAG_NAME, "h1").text
    assert tab_title == "Service Requests"
    print("Service Requests tab on session details page loaded successfully.")

    teardown(driver)


def setup():
    # Chrome driver is automatically installed with the newest version of selenium.
    driver = webdriver.Chrome()        
    driver.get("http://localhost:4200")
    return driver


def teardown(driver):
    driver.quit()


if __name__ == "__main__":
    test_contact_to_session()