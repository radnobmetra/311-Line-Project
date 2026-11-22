from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver. support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep

def test_PM_1():
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

    # Conducts all five subtests for each parking meter damage.
    def mode_shortcut(text):
        universalWebDriverAction((By.CSS_SELECTOR, "textarea[placeholder='Enter a message...']"), text)
        sleep(1)
        universalWebDriverAction((By.CLASS_NAME, "sendBtn"), None)
        sleep(25)

    # COIN
    mode_shortcut("What do I do if a parking meter's coin door is damaged")

    # CARD
    mode_shortcut("Pls help, parking meter can't scan my debit card")
    scrollDown()
    sleep(5)

    # PAYMENT
    mode_shortcut("I've tried all payment options, but this parking meter can't take anything")
    scrollDown()
    sleep(5)

    # SCREEN
    mode_shortcut("This meters screen is still blank and wont turn on")
    scrollDown()
    sleep(5)

    # UNKNOWN
    mode_shortcut("I'm having some trouble with a parking meter, but dunno what's wrong with it")
    scrollDown()
    sleep(10)

    # Close the browser window.
    driver.quit()

if __name__ == "__main__":
    test_PM_1()