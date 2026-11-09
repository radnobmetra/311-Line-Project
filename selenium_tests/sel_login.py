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

# Testing leaving email & password blank
uniWebDriverAction(driver, (By.ID, "loginButton"), None)

# Check if user is still logged out
WebDriverWait(driver, 5).until(EC.url_contains("/login"))

# Check if user is able to force through to another page
driver.get("http://localhost:4200/overview")

# Testing wrong email and password
uniWebDriverAction(driver, (By.ID, "email"), "wrong email!")
uniWebDriverAction(driver, (By.ID, "password"), "wrong password!")
uniWebDriverAction(driver, (By.ID, "loginButton"), None)

# Check if user is still logged out
WebDriverWait(driver, 5).until(EC.url_contains("/login"))

# Check if user is able to force through to another page
driver.get("http://localhost:4200/overview")

# Checks url if overview is found or if login is found in it
assert "overview" not in driver.current_url, "Not in overview"
assert "login" in driver.current_url, "On login page"

# Kill process
driver.quit()