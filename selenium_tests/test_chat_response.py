# Tests character limits, message submission, and feedback submission on the agent chat page.
# This test could fail when the application is working correctly if you are reusing an old session,
# if there is a connection error, or if the dashboard doesn't receive a response from the agent
# in less than a minute.

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

long_message = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod" \
" tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud" \
" exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor" \
" in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "

def test_chat_response():
    #create the web driver and log in using admin credentials from json file
    try:
        with open('admin_credentials.json','r') as f:
            credentials = json.load(f)
        USERNAME = credentials['USERNAME']
        PASSWORD = credentials['PASSWORD']
    except: 
        print("error: tests/admin_credentials.json does not exist or is" \
        "incorrectly formatted.")
        assert False

    #create driver and wait object
    driver = setup()
    wait = WebDriverWait(driver, timeout=5)

    #assert that driver is on login page 
    wait.until(lambda _: driver.current_url == "http://localhost:4200/login")

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
        wait.until(lambda _: driver.current_url == "http://localhost:4200/overview")
    except:
        print("Login to the admin dashboard was unsuccessful. Make sure that " \
        "tests/admin_credentials.json contains valid credentials.")
        teardown(driver)
        assert False

    #get nav bar element and navigate to agent chat
    navbar = driver.find_element(By.CLASS_NAME, "sidebar")
    navbar_link = navbar.find_element(By.LINK_TEXT, "Agent Chat")
    navbar_link.click()
    wait.until(lambda _: driver.current_url == "http://localhost:4200/agent-chat")

    #----------------- test upper character limit -------------------
    
    print("Agent chat loaded. Testing character limit...")
    #find textbox and enter message over 300 characters
    textbox = driver.find_element(By.CSS_SELECTOR, "textarea")
    textbox.send_keys(long_message)

    #find send button and send message
    sendBtn = driver.find_element(By.CLASS_NAME, "sendBtn")
    sendBtn.click()

    #confirm that the chat log contains an error message specifying the character limit
    error_msg_container = wait.until(EC.visibility_of_element_located((By.CLASS_NAME,
                                                                        "error-msg-container")))
    error_text = error_msg_container.find_element(By.CLASS_NAME, "msg-contents").text
    assert error_text == "Messages must be between 2 and 300 characters."
    print("Upper character limit works. Testing lower character limit...")

    # ----------------- test lower character limit -------------------

    #reload page to clear message log
    driver.refresh()

    #send a message under 2 characters
    textbox = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "textarea")))
    short_message = "a"
    textbox.send_keys(short_message)
    sendBtn = driver.find_element(By.CLASS_NAME, "sendBtn")
    sendBtn.click()

    #confirm that log dispays error message with character limit
    error_msg_container = wait.until(EC.visibility_of_element_located((By.CLASS_NAME,
                                                                        "error-msg-container")))
    error_text = error_msg_container.find_element(By.CLASS_NAME, "msg-contents").text
    assert error_text == "Messages must be between 2 and 300 characters."
    print("Lower character limit works. Testing that a valid message can be sent...")

    # ----------------- test sending a valid message -------------------

    #reload page to clear message log, then send a valid message
    driver.refresh()
    textbox = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "textarea")))
    message = "hi"
    textbox.send_keys(message)
    sendBtn = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "sendBtn")))
    sendBtn.click()

    #confirm that the user's message to the agent is displayed
    user_msg = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "user-msg-container")))
    user_text = user_msg.find_element(By.CLASS_NAME, "msg-contents")
    assert user_text.text == message
    print("User message successfully sent and displayed.")
    print("Testing that loading message is displayed for agent's response...")

    #find agent message
    agent_msg = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "agent-msg-container")))
    #confirm that agent message text is initially a loading message
    agent_text = agent_msg.find_element(By.CLASS_NAME, "msg-contents")
    assert agent_text.text == "Waiting for response..."
    print("Loading message successfully displayed. Testing that agent's response is displayed...")

    #wait until agent message displays any message containing "311", which should occur if and only 
    #if the page has received and displayed a greeting message from the agent
    agent_text = WebDriverWait(driver, timeout=60).until(EC.text_to_be_present_in_element(
        (By.CLASS_NAME, "agent-msg-container"), "311"
    ))
    print("Agent's response successfully displayed. Testing feedback...")

    # ----------------- test feedback -------------------

    #reload page to clear message log
    driver.refresh()

    #select thumbs up button, enter message, and submit feedback
    thumbsUpBtn = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "thumbsUpBtn")))
    thumbsUpBtn.click()
    textbox = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "textarea")))
    message = "message"
    textbox.send_keys(message)
    sendBtn = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "sendBtn")))
    sendBtn.click()

    #check for message confirming that feedback has been submitted
    user_msg = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "user-msg-container")))
    user_text = user_msg.find_element(By.CLASS_NAME, "msg-contents")
    assert user_text.text == "Sent thumbs up with comment: " + message

    #check that user receives response from server confirming that feedback is saved
    agent_text = WebDriverWait(driver, timeout=60).until(EC.text_to_be_present_in_element(
        (By.CLASS_NAME, "agent-msg-container"), "Feedback"
    ))

    #reload page to clear message log
    driver.refresh()

    #submit negative feedback with no message
    thumbsDownBtn = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "thumbsDownBtn")))
    thumbsDownBtn.click()
    sendBtn = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "sendBtn")))
    sendBtn.click()

    #check for message confirming feedback has been submitted
    user_msg = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "user-msg-container")))
    user_text = user_msg.find_element(By.CLASS_NAME, "msg-contents").text
    assert user_text == "Sent thumbs down."

    #check that user receives response from server confirming that feedback is saved
    agent_text = WebDriverWait(driver, timeout=60).until(EC.text_to_be_present_in_element(
        (By.CLASS_NAME, "agent-msg-container"), "Feedback"
    ))

    print("Feedback submission works.")
    
    teardown(driver)


def setup():
    # Chrome driver is automatically installed with the newest version of selenium.
    driver = webdriver.Chrome()        
    driver.get("http://localhost:4200")
    return driver


def teardown(driver):
    driver.quit()


if __name__ == "__main__":
    test_chat_response()