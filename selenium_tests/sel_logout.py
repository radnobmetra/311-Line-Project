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

# Creating JS script to read token in IndexedDB 
indexdb_script = """
var callback = arguments[0]; //used as a callback 

var request = indexedDB.open('firebaseLocalStorageDb');

request.onerror = function(event) {
    callback(null); // return null if failed to open
};

request.onsuccess = function(event) {
    var db = event.target.result;

    try {
        // open read only transaction on object store
        var transaction = db.transaction(['firebaseLocalStorage'], 'readonly')
        var objectstore = transaction.objectStore('firebaseLocalStorage');

        // request all keys dynamically
        var getAllKeysRequest = objectstore.getAllKeys();

        getAllKeysRequest.onsuccess = function(event) {
            var keys = event.target.result;
            //find firebase key
            var firebaseKey = keys.find(function(key) {
                return typeof key === 'string' && key.startsWith('firebase:authUser');
            });
            
            if (firebaseKey) {
                // get value of key
                var getRequest = objectstore.get(firebaseKey);
                getRequest.onsuccess = function(e) {
                    callback(e.target.result); // send token back to python
                };
                getRequest.onerror = function() {
                    callback(null);
                };
            } else {
                callback(null); //no firebase token was found
            }
        };

        getAllKeysRequest.onerror = function() {
            callback(null);
        };

    }   catch(e) {
          callback(null); // Return null if the store or key doesn't exist
    }
};

"""

# Log in credentials  and logging in
uniWebDriverAction(driver, (By.ID, "email"), "admin@sacramento.org")
uniWebDriverAction(driver, (By.ID, "password"), "admin!")
uniWebDriverAction(driver, (By.ID, "loginButton"), None)

# Getting firebase auth token to check that user credentials is needed to view pages
driver.set_script_timeout(5)
token = driver.execute_async_script(indexdb_script)
print("Retrieved Token Data:", token)

# Find logout button and use it
uniWebDriverAction(driver, (By.ID, "logout"), None)

# Check if logout went through and user is redirected to login page
WebDriverWait(driver, 5).until(EC.url_contains("/login"))

# Check if auth token is wiped after logging out
driver.set_script_timeout(5)
token = driver.execute_async_script(indexdb_script)
print("Retrieved Token Data:", token)

# Check if user is able to force through to another page
driver.get("http://localhost:4200/overview")

WebDriverWait(driver, 5).until(EC.url_contains("/login"))

# Checks url if overview is found or if login is found in it
assert "overview" not in driver.current_url, "Not in overview"
assert "login" in driver.current_url, "On login page"

# Kill process
driver.quit()