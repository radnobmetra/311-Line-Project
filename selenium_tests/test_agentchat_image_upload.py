# Tests the "Choose File" (image upload) control on the dashboard's Agent Chat page.
#
# The file input in frontend/src/app/agent-chat/agent-chat.html
# (accept="image/png, image/jpg, image/jpeg", (change)="uploadImage($event)")
# should, once a file is chosen:
#   * accept images only,
#   * put the page into image mode ("You are sending an image.") without sending,
#   * and, when the message is sent, log "Sent an image: <file name>" and return to
#     normal messaging mode.
#
# Selenium cannot click the browser's native "Choose File" dialog, so the file is
# supplied by sending its path to the input

import atexit
from pathlib import Path
import tempfile

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Locators for the agent chat page (frontend/src/app/agent-chat/agent-chat.html).
AGENT_CHAT_LINK = (By.CSS_SELECTOR, "a[routerLink='/agent-chat']")
MESSAGE_BOX = (By.CSS_SELECTOR, "textarea")
SEND_BUTTON = (By.CSS_SELECTOR, "button.sendBtn")
INFO_TEXT = (By.CSS_SELECTOR, ".userInputSection .info")
MESSAGES_CONTAINER = (By.CSS_SELECTOR, ".messages-container")
FILE_INPUT = (By.CSS_SELECTOR, "input[type='file']")

# Text the page shows for each input mode.
MESSAGING_MODE = "Messaging mode"
IMAGE_MODE = "sending an image"


# Log in (through the admin_driver fixture) and open the Agent Chat page.
def open_agent_chat(driver, base_url):
    wait = WebDriverWait(driver, 15)
    wait.until(EC.element_to_be_clickable(AGENT_CHAT_LINK)).click()
    wait.until(EC.url_to_be(f"{base_url}/agent-chat"))
    wait.until(EC.visibility_of_element_located(MESSAGE_BOX))
    return driver


def info_text(driver):
    return driver.find_element(*INFO_TEXT).text


def send_button_text(driver):
    return driver.find_element(*SEND_BUTTON).text.strip()


def messages_text(driver):
    return driver.find_element(*MESSAGES_CONTAINER).text


def file_input_value(driver):
    return driver.find_element(*FILE_INPUT).get_attribute("value")


# A throwaway file used to trigger the page's image-upload handler. The page only
# reads the chosen file's name, so the file's contents do not matter.
def create_temp_image():
    handle = tempfile.NamedTemporaryFile(
        prefix="agent-chat-upload-", suffix=".png", delete=False
    )
    handle.write(b"\x89PNG\r\n\x1a\n")
    handle.close()

    path = Path(handle.name)
    atexit.register(remove_temp_image, path)
    return path


# Removes the throwaway image. It is called right after the test and again when the
# interpreter exits, because the in-flight upload keeps the file open for the rest of
# the run. The file lives in the OS temp directory, so a leftover is harmless.
def remove_temp_image(path):
    try:
        path.unlink()
    except OSError:
        pass


def test_choose_file_button_starts_an_image_upload(admin_driver, base_url):
    driver = open_agent_chat(admin_driver, base_url)
    wait = WebDriverWait(driver, 15)

    file_input = driver.find_element(*FILE_INPUT)

    # The control is set up to accept images only.
    accept = file_input.get_attribute("accept")
    assert "image/png" in accept and "image/jpeg" in accept

    # Nothing has been chosen yet, so the page is in normal messaging mode.
    assert MESSAGING_MODE in info_text(driver)
    assert file_input_value(driver) == ""

    image = create_temp_image()
    try:
        # --- Choosing a file ---
        # send_keys supplies the file where the native "Choose File" dialog would.
        driver.find_element(*FILE_INPUT).send_keys(str(image))

        # The page enters image mode, remembers the file, and sends nothing yet.
        wait.until(lambda d: IMAGE_MODE in info_text(d))
        assert image.name in file_input_value(driver)
        assert "No messages yet" in messages_text(driver)
        print(
            "Passed! Choosing a file put the page into image mode "
            "without sending it."
        )

        # --- Sending uses the chosen file ---
        driver.find_element(*SEND_BUTTON).click()

        wait.until(lambda d: f"Sent an image: {image.name}" in messages_text(d))
        wait.until(lambda d: MESSAGING_MODE in info_text(d))
        assert send_button_text(driver) == "Send message"
        print("Passed! Sending logged the chosen file and returned to messaging mode.")
    finally:
        remove_temp_image(image)

    print("Passed! The Choose File button works as intended.")
