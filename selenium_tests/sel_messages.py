from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver. support import expected_conditions as EC
from time import sleep
import time
import json
from pathlib import Path

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

# Initialize Chrome WebDriver.
driver = webdriver.Chrome(options=options)


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

# Log in credentials  and logging in
uniWebDriverAction(driver, (By.ID, "email"), "admin@sacramento.org")
uniWebDriverAction(driver, (By.ID, "password"), "admin!")
uniWebDriverAction(driver, (By.ID, "loginButton"), None)

# Loads up session page
uniWebDriverAction(driver, (By.CSS_SELECTOR, "a[routerLink='/sessions']"), None)

# Checks that URL is correct and user is in session page
WebDriverWait(driver,5).until(EC.url_contains("/session"))
# If URL is wrong, shows test failed
assert "/session" in driver.current_url, "Test Failed: URL does not match!"

session_id_xpath = "//tr[contains(., '14474520823857152')]"

uniWebDriverAction(driver, (By.XPATH, session_id_xpath), None)

# Checks for the session ID in URL 
WebDriverWait(driver,5).until(EC.url_contains("/14474520823857152/"))

assert "/14474520823857152/" in driver.current_url, "Test Failed: Sesssion Detail Page Wrong!"

# Checks for messages tag in URL
WebDriverWait(driver,5).until(EC.url_contains("/messages"))

assert "messages" in driver.current_url, "Test Failed: URL does not match!"

WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, "log-entry-body")))

message_divs = driver.find_elements(By.ID, "log-entry-body")

# Assuming the agent responds back to user, there should be minimum 2 msgs. 
# User first prompts (1) then agent responds (2)
assert len(message_divs) >= 2, "Test Failed: Not all messages show!"

print(f"Number of divs inside this area: {len(message_divs)}")

# Print each message to see that a proper convo was logged
for index, text in enumerate (message_divs, start=1):
    msg_texts = text.text

    print (f"Message #{index}: {msg_texts}")


# Checking export button works
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

    # Clear out any stale background events that happened during page loading
    driver.get_log("performance")

    # Click export button
    uniWebDriverAction(driver, (By.CLASS_NAME, "export-btn"), None)

    # Poll our event log to ensure chrome reports the download action
    max_wait = 10
    start_time = time.time()
    filename = None
    success = False

    while time.time() - start_time < max_wait:
        # Fetch background system logs produced since our last check
        logs = driver.get_log("performance")
        for entry in logs:
            log_data = json.loads(entry["message"])["message"]
            method = log_data.get("method")
            
            # Look for chrome's native "download is starting" signal
            if method in ["Browser.downloadWillBegin", "Page.downloadWillBegin"]:
                filename = log_data["params"]["suggestedFilename"]
                print(f"Download Works! File: {filename}")
                success = True
                break
                
        if success:
            break
        time.sleep(0.5)

    assert success, "Test Failed: Chrome did not trigger a native download event when the button was clicked."

    # check filename that was downloaded is correct by checking name and suffix
    assert filename.startswith("messages-"), f"Expected prefix 'messages', got: {filename}"
    assert filename.endswith(".csv"), f"Expected a CSV file format, got: {filename}"

finally:
    # Return back to sessions page and check back to session button works
    uniWebDriverAction(driver, (By.ID, "back_to_session"), None)

    WebDriverWait(driver,5).until(EC.url_contains("/session"))

    assert "session" in driver.current_url, "Test Failed: return button does not works!"

driver.quit()