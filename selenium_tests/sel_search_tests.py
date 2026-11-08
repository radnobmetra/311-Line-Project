from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import json






driver = webdriver.Chrome()



def test_session_sorting():
	driver.get("http://localhost:4200/login")

	title = driver.title
	driver.implicitly_wait(2)

	# Login Screen to get into sessions
	login_credentials = open('admin_credentials.json', 'r') 
	print(login_credentials)

	login_json = json.load(login_credentials)


	username = login_json["USERNAME"]
	password = login_json["PASSWORD"]

	email_box = driver.find_element(by=By.NAME, value ="emailLogin")
	pw_box = driver.find_element(by=By.NAME, value="passLogin")
	login_button = driver.find_element(by=By.CSS_SELECTOR, value="button")

	email_box.send_keys(username)
	pw_box.send_keys(password)
	login_button.click()

	sessions_box = driver.find_element(by=By.XPATH, value="//*[contains(text(), 'Sessions')]")
	sessions_box.click()

	sessions_filter = driver.find_element(by=By.ID, value="outcome-filter")


	sessions_selector = Select(sessions_filter)
	sessions_selector.select_by_index(0)
	sessions_selector.select_by_index(1)
	sessions_selector.select_by_index(2)
	sessions_selector.select_by_index(3)



