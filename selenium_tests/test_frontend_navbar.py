# Selenium script to test the nav bar using a chrome driver. 

# Before running this script, you must create a json file, tests/admin_credentials.json,
# that contains username and password values that selenium can use to log in to the 
# dashboard.

# selenium_tests/admin_credentials.json should contain the following:
# {
#     "USERNAME": "admin username goes here", 
#     "PASSWORD": "admin password goes here"
# }

# To run the script, run this command from the project root:
#       python selenium_tests/test_frontend_navbar.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json


def run_navbar_test():
    #get admin credentials from json file
    try:
        with open('selenium_tests/admin_credentials.json','r') as f:
            credentials = json.load(f)
        USERNAME = credentials['USERNAME']
        PASSWORD = credentials['PASSWORD']
    except: 
        print("error: tests/admin_credentials.json does not exist or is" \
        "incorrectly formatted.")
        assert False

    #create driver and wait
    driver = setup()
    wait = WebDriverWait(driver, timeout=3)

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
    
    print("Logged in successfully. Testing navbar links...")

    #get nav bar element
    navbar = driver.find_element(By.CLASS_NAME, "sidebar")

    #test contacts link
    navbar_link = navbar.find_element(By.LINK_TEXT, "Contacts")     #get link
    navbar_link.click()         #follow link
    #wait until the new page is loaded
    wait.until(lambda _: driver.current_url == "http://localhost:4200/contacts")
    print("Contacts link works.")

    #test sessions link
    navbar_link = navbar.find_element(By.LINK_TEXT, "Sessions")     #get link
    navbar_link.click()         #follow link
    wait.until(lambda _: driver.current_url == "http://localhost:4200/sessions")
    print("Sessions link works.")

    #test requests link
    navbar_link = navbar.find_element(By.LINK_TEXT, "Requests")     #get link
    navbar_link.click()         #follow link
    wait.until(lambda _: driver.current_url == "http://localhost:4200/requests")
    print("Requests link works.")

    #test service requests link
    navbar_link = navbar.find_element(By.LINK_TEXT, "Service Requests")     #get link
    navbar_link.click()         #follow link
    wait.until(lambda _: driver.current_url == "http://localhost:4200/service-requests")
    print("Service requests link works.")

    #test agent chat link
    navbar_link = navbar.find_element(By.LINK_TEXT, "Agent Chat")     #get link
    navbar_link.click()         #follow link
    wait.until(lambda _: driver.current_url == "http://localhost:4200/agent-chat")
    print("Agent chat link works.")

    #test profile link
    navbar_link = navbar.find_element(By.LINK_TEXT, "Profile")     #get link
    navbar_link.click()         #follow link
    wait.until(lambda _: driver.current_url == "http://localhost:4200/profile")
    print("Profile link works.")

    #test analytics link
    navbar_link = navbar.find_element(By.LINK_TEXT, "Analytics")     #get link
    navbar_link.click()         #follow link
    wait.until(lambda _: driver.current_url == "http://localhost:4200/analytics")
    print("Analytics link works.")

    #test flagged conversations link
    navbar_link = navbar.find_element(By.LINK_TEXT, "Flagged Conversations")     #get link
    navbar_link.click()         #follow link
    wait.until(lambda _: driver.current_url == "http://localhost:4200/flagged-convo")
    print("Flagged conversations link works.")

    #test messages link
    navbar_link = navbar.find_element(By.LINK_TEXT, "Messages")     #get link
    navbar_link.click()         #follow link
    wait.until(lambda _: driver.current_url == "http://localhost:4200/messages")
    print("Messages link works.")

    #test settings link
    navbar_link = navbar.find_element(By.LINK_TEXT, "Settings")     #get link
    navbar_link.click()         #follow link
    wait.until(lambda _: driver.current_url == "http://localhost:4200/settings")
    print("Settings link works.")

    #test overview link
    navbar_link = navbar.find_element(By.LINK_TEXT, "Overview")     #get overview link
    navbar_link.click()         #follow overview link
    wait.until(lambda _: driver.current_url == "http://localhost:4200/overview")
    print("Overview link works.")

    teardown(driver)


def setup():
    # Chrome driver is automatically installed with the newest version of selenium.
    driver = webdriver.Chrome()        
    driver.get("http://localhost:4200")
    return driver


def teardown(driver):
    driver.quit()


if __name__ == "__main__":
    run_navbar_test()