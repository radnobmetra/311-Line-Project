
# Selenium script that tests that the export button works on the session details page.

# This script uses a chrome driver and tests the deployed app at the following url:
    # https://dashboard-311-537729300096.us-west1.run.app

# Before running this script, you must create a json file, tests/admin_credentials.json,
# that contains username and password values that selenium can use to log in to the 
# dashboard.

# selenium_tests/admin_credentials.json should contain the following:
# {
#     "USERNAME": "admin username goes here", 
#     "PASSWORD": "admin password goes here"
# }

# To run the script, run this command from the selenium_tests folder:
#       python test_session_details_export.py

# To run pytest, run this command from the selenium_tests folder:
#   python -m pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from pathlib import Path

# --------- initialize options and path in order to download files ----------------

# Establish an absolute, valid directory path that works on Windows and Linux/WSL
PROJECT_ROOT = Path(__file__).parent.resolve()
DOWNLOAD_DIR = PROJECT_ROOT / "test_downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)
VALID_PATH = str(DOWNLOAD_DIR)

# Connecting to chrome to see chrome behaviors 
options = webdriver.ChromeOptions()

options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

prefs = {
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": False,              # Disables malicious file blocks on test files
    "safebrowsing.disable_download_protection": True # Stops Chrome from blocking localhost downloads
}
options.add_experimental_option("prefs", prefs)

#helper function for inputs within the SAME driver so it does not look for a global driver. 
def uniWebDriverAction(driver, locator, input_value = None):
    item = WebDriverWait(driver,10).until(
        EC.presence_of_element_located(locator)
    )
    time.sleep(1)


def test_session_details_export():

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
    wait.until(lambda _: driver.current_url == "https://dashboard-311-537729300096.us-west1.run.app/login")
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
        wait.until(lambda _: driver.current_url == "https://dashboard-311-537729300096.us-west1.run.app/overview")
    except:
        print("Login to the admin dashboard was unsuccessful. Make sure that " \
        "selenium_tests/admin_credentials.json exists and contains valid credentials.")
        teardown(driver)
        assert False
    
    print("Logged in successfully. Going to session details...")

    #----------------------- going to the session details page -----------------------

    #get nav bar element
    navbar = driver.find_element(By.CLASS_NAME, "sidebar")

    # find the link to the sessions page and follow it
    navbar_link = navbar.find_element(By.LINK_TEXT, "Sessions")
    navbar_link.click()
    wait.until(lambda _: driver.current_url == "https://dashboard-311-537729300096.us-west1.run.app/sessions")

    #click on the first session in the table
    clickable_row = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "clickable-row")))
    clickable_row.click()

    #wait for the session details page to load
    wait.until(lambda _: driver.current_url.startswith("https://dashboard-311-537729300096.us-west1.run.app/session-details/"))

    # on session details page, click on messages tab
    tabs = driver.find_element(By.CLASS_NAME, "tabs")
    messages_tab = tabs.find_element(By.LINK_TEXT, "Messages")
    messages_tab.click()

    print("Session details loaded successfully. Confirming that export button works...")

    #----------------------- test export button on messages tab --------------------
    # determine if messages/session log is empty or not depending on whether the session-log or 
    # empty-state class is present.

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

    # find export button
    tab_header = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "title-btn")))
    export_btn = tab_header.find_elements(By.CLASS_NAME, "export-btn")

    # test export button
    try:
        # Enable the browser download behavior via CDP command to grant permission to track download progress events
        driver.execute_cdp_cmd("Browser.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": VALID_PATH, # Must specify a path, but will rely on events instead
            "eventsEnabled": True   # turns on the background events we need
        })

        driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": VALID_PATH
        })

        # Clear stale background events and click export button
        driver.get_log("performance")
        export_btn[0].click()

        # Poll our event log to ensure chrome reports the download action
        max_wait = 10
        start_time = time.time()
        filename = None
        fileDownloaded = False

        while time.time() - start_time < max_wait:
            # Fetch background system logs produced since our last check
            logs = driver.get_log("performance")
            for entry in logs:
                log_data = json.loads(entry["message"])["message"]
                method = log_data.get("method")
            
                # Look for chrome's native "download is starting" signal
                if method in ["Browser.downloadWillBegin", "Page.downloadWillBegin"]:
                    filename = log_data["params"]["suggestedFilename"]
                    print(f"Download works. File: {filename}")
                    fileDownloaded = True
                    break
                
            if fileDownloaded:
                break
            time.sleep(0.5)
    except:
        fileDownloaded = False

    # determine whether the result of clicking the export button was correct. A file should not 
    # have been downloaded if the empty_state class exists (there is no data to download) and a
    #  file should always be downloaded if the session_log class exists 
    # (there are events/messages to download)

    if (empty_state is not None):
        assert (fileDownloaded == False), "Test Failed: Export button downloaded file for empty session log."
        print("Export button works on empty session log.")

    if (session_log is not None):
        assert (fileDownloaded == True), "Test Failed: Export button did not download file for session log."
        # check filename that was downloaded is correct by checking name and suffix
        assert filename.startswith("messages"), f"Expected prefix 'messages', got: {filename}"
        assert filename.endswith(".csv"), f"Expected a CSV file format, got: {filename}"
        print("Export button works on session log.")

    # ========================= test export button on requests tab ==================================

    # click on requests tab
    requests_tab = tabs.find_element(By.LINK_TEXT, "Service Requests")
    requests_tab.click()

    #find export button
    tab_header = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "title-btn")))
    export_btn = tab_header.find_elements(By.CLASS_NAME, "export-btn")

    #determine if requests tab is empty or not based on whether tab contains empty-state or clickable-row class
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

    try:
        # Enable the browser download behavior via CDP command to grant permission to track download progress events
        driver.execute_cdp_cmd("Browser.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": VALID_PATH, # Must specify a path, but will rely on events instead
            "eventsEnabled": True   # turns on the background events we need
        })

        driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": VALID_PATH
        })

        # Clear out stale background events, click export button
        driver.get_log("performance")
        export_btn[0].click()

        # Poll our event log to ensure chrome reports the download action
        max_wait = 10
        start_time = time.time()
        filename = None
        fileDownloaded = False

        while time.time() - start_time < max_wait:
            # Fetch background system logs produced since our last check
            logs = driver.get_log("performance")
            for entry in logs:
                log_data = json.loads(entry["message"])["message"]
                method = log_data.get("method")
            
                # Look for chrome's native "download is starting" signal
                if method in ["Browser.downloadWillBegin", "Page.downloadWillBegin"]:
                    filename = log_data["params"]["suggestedFilename"]
                    success = True
                    break
                
            if success:
                break
            time.sleep(0.5)
    except:
        fileDownloaded = False

    # determine whether the result of clicking the export button was correct.
    # A file should not have been downloaded if the empty_state
    # class exists (there is no data to download) and a file should always be downloaded if the 
    # requests class exists (there is request data to download)

    if (empty_state is not None):
        assert (fileDownloaded == False), "Test Failed: Export button downloaded file for empty request log."
        print("Export button works on empty request log.")

    if (requests_list is not None):
            assert (fileDownloaded == True), "Test Failed: Export button did not download file for request log."
            # check filename that was downloaded is correct by checking name and suffix
            assert filename.startswith("service-requests"), f"Expected prefix 'service-requests', got: {filename}"
            assert filename.endswith(".csv"), f"Expected a CSV file format, got: {filename}"
            print("Export button works on request log.")

    teardown(driver)


def setup():
    # Chrome driver is automatically installed with the newest version of selenium.
    driver = webdriver.Chrome(options=options)
    driver.get("https://dashboard-311-537729300096.us-west1.run.app/login")
    return driver


def teardown(driver):
    driver.quit()


if __name__ == "__main__":
    test_session_details_export()