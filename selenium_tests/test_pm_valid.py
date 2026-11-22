from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver. support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep

def test_PM_2():
    # Initialize Chrome WebDriver.
    driver = webdriver. Chrome()

    # Open the deployed admin dashboard.
    driver.get("http://localhost:4200/login")
    sleep(1)

    def universalWebDriverAction(locator, input_value):
        item = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(locator)
        )
        sleep(1)
        # If given an input, send input to the text box.
        if (input_value is not None):
            for x in range(0, len(input_value)):
                item.send_keys(input_value[x])
                sleep(0.05)
            sleep(1)
        # Otherwise, click on the button.
        else:
            item.click()
            sleep(1)

    # Scrolls down on the messages container.
    def scrollDown():
        item = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "messages-container"))
        )
        for x in range(20):
            item.send_keys(Keys.ARROW_DOWN)
            sleep(0.05)

    # FIND the email field, and ENTER email.
    universalWebDriverAction((By.ID, "email"), "admin@sacramento.org")

    # FIND the password field, and ENTER password.
    universalWebDriverAction((By.ID, "password"), "admin!")

    # FIND the login button, and CLICK login.
    universalWebDriverAction((By.CSS_SELECTOR, "button[type='submit']"), None)

    # FIND the Agent Chat button on the sidebar, and CLICK Agent Chat.
    universalWebDriverAction((By.CSS_SELECTOR, "a[routerLink='/agent-chat']"), None)

    def mode_shortcut(text):
        universalWebDriverAction((By.CSS_SELECTOR, "textarea[placeholder='Enter a message...']"), text)
        sleep(1)
        universalWebDriverAction((By.CLASS_NAME, "sendBtn"), None)
        sleep(25)

    mode_shortcut("How can I report a parking meter? Its coin slot is broken")

    # VALID INPUT
    mode_shortcut("Street is 1826 N ST, and number is PKGS15527")
    scrollDown()
    sleep(5)

    # INVALID INPUT
    mode_shortcut("I have one more. This meter has a frozen screen that I cant interact with. It's on 441 Pine St.")
    scrollDown()
    sleep(5)

    # Close the browser window.
    driver.quit()

if __name__ == "__main__":
    test_PM_2()