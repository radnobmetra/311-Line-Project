# Tests the Clear button on the dashboard's Agent Chat page.
#
# The Clear button (button[aria-label="Clear"], which calls agentChat.clear()) should:
#   * empty the message box without sending the message,
#   * leave feedback / image mode and return to normal messaging mode,
#   * deselect the Thumbs Up and Thumbs Down buttons.

from pathlib import Path
import tempfile

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Locators for the agent chat page (frontend/src/app/agent-chat/agent-chat.html).
AGENT_CHAT_LINK = (By.CSS_SELECTOR, "a[routerLink='/agent-chat']")
MESSAGE_BOX = (By.CSS_SELECTOR, "textarea")
CLEAR_BUTTON = (By.CSS_SELECTOR, "button[aria-label='Clear']")
THUMBS_UP = (By.CSS_SELECTOR, "button[aria-label='Like']")
THUMBS_DOWN = (By.CSS_SELECTOR, "button[aria-label='Dislike']")
SEND_BUTTON = (By.CSS_SELECTOR, "button.sendBtn")
INFO_TEXT = (By.CSS_SELECTOR, ".userInputSection .info")
MESSAGES_CONTAINER = (By.CSS_SELECTOR, ".messages-container")
FILE_INPUT = (By.CSS_SELECTOR, "input[type='file']")

# Text the page shows for each input mode.
MESSAGING_MODE = "Messaging mode"
FEEDBACK_MODE = "Feedback mode"
IMAGE_MODE = "sending an image"

# Classes agentChat applies to the thumbs buttons when selected / not selected.
THUMBS_UP_SELECTED = "thumbsUpBtn_selected"
THUMBS_DOWN_SELECTED = "thumbsDownBtn_selected"
THUMBS_UP_DEFAULT = "thumbsUpBtn"
THUMBS_DOWN_DEFAULT = "thumbsDownBtn"


# Log in (through the admin_driver fixture) and open the Agent Chat page.
def open_agent_chat(driver, base_url):
    wait = WebDriverWait(driver, 15)
    wait.until(EC.element_to_be_clickable(AGENT_CHAT_LINK)).click()
    wait.until(EC.url_to_be(f"{base_url}/agent-chat"))
    wait.until(EC.visibility_of_element_located(MESSAGE_BOX))
    return driver


def info_text(driver):
    return driver.find_element(*INFO_TEXT).text


def message_box_value(driver):
    return driver.find_element(*MESSAGE_BOX).get_attribute("value")


def send_button_text(driver):
    return driver.find_element(*SEND_BUTTON).text.strip()


def button_class(driver, locator):
    return driver.find_element(*locator).get_attribute("class")


def messages_text(driver):
    return driver.find_element(*MESSAGES_CONTAINER).text


# A throwaway file used to trigger the page's image-upload handler. The page only
# reads the chosen file's name, so the file's contents do not matter.
def create_temp_image():
    handle = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    handle.write(b"\x89PNG\r\n\x1a\n")
    handle.close()
    return handle.name


def test_clear_button_resets_the_agent_chat_input(admin_driver, base_url):
    driver = open_agent_chat(admin_driver, base_url)
    wait = WebDriverWait(driver, 15)

    # The page opens in normal messaging mode with nothing in the log.
    assert MESSAGING_MODE in info_text(driver)
    assert send_button_text(driver) == "Send message"
    assert "No messages yet" in messages_text(driver)

    # --- Clear empties the message box without sending the text ---
    driver.find_element(*MESSAGE_BOX).send_keys("hello agent")
    assert message_box_value(driver) == "hello agent"

    driver.find_element(*CLEAR_BUTTON).click()
    wait.until(lambda d: message_box_value(d) == "")
    assert "No messages yet" in messages_text(driver)
    print("Passed! Clear emptied the message box without sending it.")

    # --- Clear leaves Thumbs Up feedback mode and deselects the buttons ---
    driver.find_element(*THUMBS_UP).click()
    wait.until(lambda d: FEEDBACK_MODE in info_text(d))
    assert send_button_text(driver) == "Send feedback"
    assert button_class(driver, THUMBS_UP) == THUMBS_UP_SELECTED

    driver.find_element(*CLEAR_BUTTON).click()
    wait.until(lambda d: MESSAGING_MODE in info_text(d))
    assert send_button_text(driver) == "Send message"
    assert button_class(driver, THUMBS_UP) == THUMBS_UP_DEFAULT
    assert button_class(driver, THUMBS_DOWN) == THUMBS_DOWN_DEFAULT
    print("Passed! Clear left Thumbs Up feedback mode.")

    # --- Clear leaves Thumbs Down feedback mode ---
    driver.find_element(*THUMBS_DOWN).click()
    wait.until(lambda d: FEEDBACK_MODE in info_text(d))
    assert button_class(driver, THUMBS_DOWN) == THUMBS_DOWN_SELECTED

    driver.find_element(*CLEAR_BUTTON).click()
    wait.until(lambda d: MESSAGING_MODE in info_text(d))
    assert button_class(driver, THUMBS_DOWN) == THUMBS_DOWN_DEFAULT
    print("Passed! Clear left Thumbs Down feedback mode.")

    # --- Clear leaves image mode ---
    image_path = create_temp_image()
    try:
        driver.find_element(*FILE_INPUT).send_keys(image_path)
        wait.until(lambda d: IMAGE_MODE in info_text(d))

        driver.find_element(*CLEAR_BUTTON).click()
        wait.until(lambda d: MESSAGING_MODE in info_text(d))
        assert send_button_text(driver) == "Send message"
        print("Passed! Clear left image mode.")
    finally:
        Path(image_path).unlink(missing_ok=True)

    print("Passed! The Clear button resets the agent chat input.")
