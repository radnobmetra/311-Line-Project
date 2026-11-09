from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver. support import expected_conditions as EC
from time import sleep

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

# Log in credentials  and logging in
uniWebDriverAction(driver, (By.ID, "email"), "admin@sacramento.org")
uniWebDriverAction(driver, (By.ID, "password"), "admin!")
uniWebDriverAction(driver, (By.ID, "loginButton"), None)

# Loads up session page
uniWebDriverAction(driver, (By.CSS_SELECTOR, "a[routerLink='/sessions']"), None)

WebDriverWait(driver,5).until(EC.url_contains("/session"))

session_id_xpath = "//tr[contains(., '14474520823857152')]"

uniWebDriverAction(driver, (By.XPATH, session_id_xpath), None)

# Checks for the session ID in URL 
WebDriverWait(driver,5).until(EC.url_contains("/14474520823857152/"))

assert "/14474520823857152/" in driver.current_url, "Test Failed: Sesssion Detail Page Wrong!"

# Return back to sessions page
uniWebDriverAction(driver, (By.ID, "back_to_session"), None)

WebDriverWait(driver,5).until(EC.url_contains("/session"))

assert "session" in driver.current_url, "Test Failed: return button does not works!"

WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.XPATH, "//table//td"))
)

# Checking that mandatory boxes in table are not empty 

session_id = "470041770630053888"
phone_number = "(916) 555-5555"
status = "Stored"
started_at = "11/4/26, 4:51 PM "
last_message_at = "11/4/26, 8:16 PM "

mandatory_boxes_xpath = f"//tr[contains(., '{session_id}')]"

row_element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, mandatory_boxes_xpath))
)

cell_phone       = row_element.find_element(By.XPATH, "./td[2]").text
cell_status      = row_element.find_element(By.XPATH, "./td[3]").text
cell_started     = row_element.find_element(By.XPATH, "./td[7]").text
cell_last_msg    = row_element.find_element(By.XPATH, "./td[8]").text

# Extract and print the row text to verify mandatory boxes are filled out
row_text = row_element.text
print(f"Discovered row text: {row_text}")

# Explicitly verify every expected value is present in the text string
assert cell_phone == phone_number, f"Expected {phone_number}, but got {cell_phone}"
assert cell_status == status, f"Expected {status}, but got {cell_status}"

# Look strictly for text to not have whitespaces mess up the test
assert "11/4/26" in cell_started and "4:51" in cell_started, f"Start time mismatch: {cell_started}"
assert "11/4/26" in cell_last_msg and "8:16" in cell_last_msg, f"End time mismatch: {cell_last_msg}"


# Go into session details for 470041770630053888
uniWebDriverAction(driver, (By.XPATH, mandatory_boxes_xpath), None)

# Checks for the session ID in URL 
WebDriverWait(driver,5).until(EC.url_contains("470041770630053888"))

assert "470041770630053888" in driver.current_url, "Test Failed: Sesssion Detail Page Wrong!"

# Return back to sessions page
uniWebDriverAction(driver, (By.ID, "back_to_session"), None)

WebDriverWait(driver,5).until(EC.url_contains("/session"))

assert "session" in driver.current_url, "Test Failed: return button does not works!"