from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import json






driver = webdriver.Chrome()





def test_request_filtering():
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

	requests_box = driver.find_element(by=By.XPATH, value="//*[contains(text(), 'Requests')]")
	requests_box.click()

	topic_filter_ticket = driver.find_element(by=By.ID, value="topicTicket")
	topic_filter_ticket.click()

	topic_filter_generalQuestion = driver.find_element(by=By.ID, value="topicGeneralQuestion")
	topic_filter_generalQuestion.click()

	topic_filter_ticketQuestion = driver.find_element(by=By.ID, value="topicTicketQuestion")
	topic_filter_ticketQuestion.click()

	topic_filter_none = driver.find_element(by=By.ID, value="topicNone")
	topic_filter_none.click()

	topic_filter_noFilter = driver.find_element(by=By.ID, value="topicNoFilter")
	topic_filter_noFilter.click()


