from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver. support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep

# Initialize Chrome WebDriver.
driver = webdriver. Chrome()

# Open the login page.
driver.get("http://localhost:4200/login")
sleep(1)

# This function automates the process of finding an element, waiting-
# -for it to be present, and either sending an input or clicking on-
# -the component based on the provided parameters.
def universalWebDriverAction(locator, input_value):
    # WebDriverWait takes a driver instance and the maximum number of-
    # -seconds to wait for the element to show before timing out
    item = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(locator)
    )
    sleep(1)
    # If an input value is provided, send the input to the element.
    if (input_value is not None):
        # Instead of sending the entire input at once, send it character by character with-
        # -a 0.1-second delay in-between to simulate typing.
        for x in range(0, len(input_value)):
            item.send_keys(input_value[x])
            sleep(0.1)
        sleep(1)
    # Otherwise, click on the element.
    else:
        item.click()
        sleep(1)

# Will clear the search bar input by sending backspace keys to the input field.
def clearSearchBar():
    # Select the search bar.
    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "search"))
    )
    search_input.click()
    # Extract current value of the search bar input field, if any.
    input_value = search_input.get_attribute("value")
    # Backspace repeatedly.
    for x in range(0, len(input_value)):
        search_input.send_keys(Keys.BACKSPACE)
        sleep(0.1)
    sleep(1)

# Will clear the date filter input by sending backspace keys to the input field.
def clearDateFilter(locator):
    # Select the date filter input field.
    date_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(locator)
    )
    date_input.click()
    date_input.send_keys(Keys.BACKSPACE)
    sleep(0.5)
    date_input.send_keys(Keys.ARROW_LEFT)
    sleep(0.5)
    date_input.send_keys(Keys.BACKSPACE)
    sleep(0.5)
    date_input.send_keys(Keys.ARROW_LEFT)
    sleep(0.5)
    date_input.send_keys(Keys.BACKSPACE)
    sleep(1)

# << SCRIPT STARTS HERE >>

# FIND the email field, and ENTER email.
universalWebDriverAction((By.ID, "email"), "admin@sacramento.org")

# FIND the password field, and ENTER password.
universalWebDriverAction((By.ID, "password"), "admin!")

# FIND the login button, and CLICK login.
universalWebDriverAction((By.ID, "loginButton"), None)

# FIND the requests button on the sidebar, and CLICK requests.
universalWebDriverAction((By.CSS_SELECTOR, "a[routerLink='/requests']"), None)

# << SEARCH BAR FILTERING >>

# FIND the search bar input field, and ENTER search term.
# Will clear the previous input before entering a new search term.
universalWebDriverAction((By.ID, "search"), "123")
sleep(2)
clearSearchBar()

universalWebDriverAction((By.ID, "search"), "ticket")
sleep(2)
clearSearchBar()

universalWebDriverAction((By.ID, "search"), "just something random")
sleep(2)
clearSearchBar()

# << SORT BY DATE FILTERING >>

# FIND the "Sort by date" filters, and CLICK "newest".
universalWebDriverAction((By.CSS_SELECTOR, "input[value='newest']"), None)
sleep(2)

# FIND the "Sort by date" filters, and CLICK "oldest".
universalWebDriverAction((By.CSS_SELECTOR, "input[value='oldest']"), None)
sleep(2)

# FIND the "Sort by date" filters, and CLICK "don't sort by date".
universalWebDriverAction((By.ID, "sortDateNone"), None)
sleep(2)

# << FILTER BY DATE >>

universalWebDriverAction((By.ID, "filterAfterDate"), "11032018")
sleep(2)
clearDateFilter((By.ID, "filterAfterDate"))

universalWebDriverAction((By.ID, "filterBeforeDate"), "10012019")
sleep(2)
clearDateFilter((By.ID, "filterBeforeDate"))

# << FILTER BY TOPIC >>

# FIND the "Filter by topic" filters, and CLICK "ticket", "general", "both", "none", and "Don't filter".
universalWebDriverAction((By.CSS_SELECTOR, "input[value='ticket']"), None)
sleep(2)

universalWebDriverAction((By.CSS_SELECTOR, "input[value='general']"), None)
sleep(2)

universalWebDriverAction((By.CSS_SELECTOR, "input[value='both']"), None)
sleep(2)

universalWebDriverAction((By.CSS_SELECTOR, "input[value='none']"), None)
sleep(2)

universalWebDriverAction((By.ID, "filterTopicNone"), None)
sleep(2)

# << EXPORT DATA >>

# Export all rows, unfiltered.
universalWebDriverAction((By.ID, "exportBtn"), None)
sleep(2)

# Export only the first, third, and sixth rows, unfiltered.
universalWebDriverAction((By.XPATH, "(//input[@type='checkbox'])[1]"), None)
universalWebDriverAction((By.XPATH, "(//input[@type='checkbox'])[3]"), None)
universalWebDriverAction((By.XPATH, "(//input[@type='checkbox'])[6]"), None)
sleep(2)
universalWebDriverAction((By.ID, "exportBtn"), None)
# Unselect the previously selected rows.
universalWebDriverAction((By.XPATH, "(//input[@type='checkbox'])[1]"), None)
universalWebDriverAction((By.XPATH, "(//input[@type='checkbox'])[3]"), None)
universalWebDriverAction((By.XPATH, "(//input[@type='checkbox'])[6]"), None)

# A mix of filters, and export the filtered rows.
universalWebDriverAction((By.ID, "search"), "890")
sleep(1)
universalWebDriverAction((By.CSS_SELECTOR, "input[value='newest']"), None)
sleep(1)
universalWebDriverAction((By.ID, "filterAfterDate"), "05102015")
sleep(1)
universalWebDriverAction((By.ID, "filterBeforeDate"), "01012026")
sleep(1)
universalWebDriverAction((By.CSS_SELECTOR, "input[value='both']"), None)
sleep(1)
universalWebDriverAction((By.ID, "filterTopicNone"), None)
sleep(1)
universalWebDriverAction((By.XPATH, "(//input[@type='checkbox'])[1]"), None)
sleep(1)
universalWebDriverAction((By.XPATH, "(//input[@type='checkbox'])[2]"), None)
sleep(1)
universalWebDriverAction((By.ID, "exportBtn"), None)

sleep(2)

# Clean up.
universalWebDriverAction((By.XPATH, "(//input[@type='checkbox'])[2]"), None)
sleep(1)
clearSearchBar()
sleep(1)
universalWebDriverAction((By.ID, "sortDateNone"), None)
sleep(1)
clearDateFilter((By.ID, "filterAfterDate"))
sleep(1)
clearDateFilter((By.ID, "filterBeforeDate"))
sleep(1)
universalWebDriverAction((By.CSS_SELECTOR, "input[value='ticket']"), None)
sleep(1)
universalWebDriverAction((By.ID, "filterTopicNone"), None)

sleep(2)
# Close the browser window.
driver.quit()