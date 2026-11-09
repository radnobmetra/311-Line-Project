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

# Waits for table to load before trying to find all table elements
WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.ID, "session-table")))

# Finds table and counts rows
rows = driver.find_elements(By.XPATH, "//table[@id='session-table']/tbody/tr")

assert len(rows) > 1, "Test Failed: table not loading properly!"

print(len(rows))

# After verifying that table does have multiple rows, check to see proper values are inputted
print(f"Retrieved {len(rows[:5])} values from the table:")

# Lists values for first 5 rows
for index, val in enumerate(rows[:5], start=1): # remove [:5] to view all rows or change to see more or less rows
    cells = val.find_elements(By.XPATH, "./td")

    cell_val = [cell.text for cell in cells] 

    print (f"Row {index} Values: {cell_val}")


# Checking for export button function
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
    assert filename.startswith("sessions-"), f"Expected prefix 'sessions_export', got: {filename}"
    assert filename.endswith(".csv"), f"Expected a CSV file format, got: {filename}"

finally:
    driver.quit()