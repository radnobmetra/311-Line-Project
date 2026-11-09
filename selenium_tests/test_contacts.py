import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

with open('admin_credentials.json') as f:
    creds = json.load(f)

driver = webdriver.Chrome()
driver.get("http://localhost:4200/login")

email_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "email"))
)
email_input.send_keys(creds["USERNAME"])
sleep(2)

password_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "password"))
)
password_input.send_keys(creds["PASSWORD"])
sleep(2)

login_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
)
login_button.click()

contacts_link = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Contacts')]"))
)
contacts_link.click()

contacts_header = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.TAG_NAME, "h1")) 
)

assert "contacts" in driver.current_url.lower(), "error?"
print("Passed! Got through Contacts page.")
sleep(5)
driver.quit()