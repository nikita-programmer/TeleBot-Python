import threading
import signal
from webdriver_manager.chrome import ChromeDriverManager
import curses
from selenium.common.exceptions import StaleElementReferenceException
from collections import deque
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import os
import pyautogui
import base64
import socket
from time import sleep
import time
import sys
from urllib.parse import urljoin
import requests
selling = 'https://www.facebook.com/marketplace/you/selling'
# Function to perform the Facebook posting
def post(name, descriptionn, price, condition, photopath):
    global driver
    
    try:
        # Setting up preferences and options for the Chrome WebDriver
        url = 'https://www.facebook.com/marketplace'
        prefs = {
            "profile.default_content_setting_values.notifications": 2
        }
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", prefs)
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-site-isolation-trials')
        options.add_argument('--allow-file-access-from-files')
        options.add_argument("--disable-features=NetworkService,NetworkServiceInProcess")
        options.add_argument("--disable-extensions")
        
        # Initializing the Chrome WebDriver
        driver_path = ChromeDriverManager().install()
        DRIVER_PATH = '/Users/alexey/Downloads/chromedriver-mac-x64/chromedriver'
        driver = webdriver.Chrome(options=options)

        # Navigating to Facebook Marketplace and handling login
        actions = ActionChains(driver)
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        password_str = 'Tomcat21!'
        allow_cookies_button = driver.find_element(By.XPATH, "//button[@title='Allow all cookies']")
        allow_cookies_button.click()
        username = driver.find_element(By.ID, 'email')
        password_input = driver.find_element(By.ID, 'pass')
        username.send_keys('oliverfoben')
        password_input.send_keys(password_str)
        try:
            login_button = wait.until(EC.element_to_be_clickable((By.NAME, 'login')))
            login_button.click()
            # Add a short delay to allow the page to respond
            sleep(2)
            # Check if login was successful by looking for a known element on the next page
            success_element = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'x1i10hfl') and contains(@class, 'xjbqb8w') and contains(@class, 'x6umtig') and contains(@class, 'x1b1mbwd') and contains(@class, 'xaqea5y') and contains(@class, 'xav7gou') and contains(@class, 'x1ypdohk') and contains(@class, 'xe8uvvx') and contains(@class, 'xdj266r') and contains(@class, 'x11i5rnm') and contains(@class, 'xat24cr') and contains(@class, 'x1mh8g0r') and contains(@class, 'xexx8yu') and contains(@class, 'x4uap5') and contains(@class, 'x18d9i69') and contains(@class, 'xkhd6sd') and contains(@class, 'x16tdsg8') and contains(@class, 'x1hl2dhg') and contains(@class, 'xggy1nq') and contains(@class, 'x1o1ewxj') and contains(@class, 'x3x9cwd') and contains(@class, 'x1e5q0jg') and contains(@class, 'x13rtm0m') and contains(@class, 'x87ps6o') and contains(@class, 'x1lku1pv') and contains(@class, 'x1a2a7pz') and contains(@class, 'x9f619') and contains(@class, 'x3nfvp2') and contains(@class, 'xdt5ytf') and contains(@class, 'xl56j7k') and contains(@class, 'x1n2onr6') and contains(@class, 'xh8yej3') and contains(@aria-label, 'Create new listing') and contains(@href, '/marketplace/create/') and contains(@role, 'link') and contains(@tabindex, '0')]")))
            print("Login successful!")
        except NoSuchElementException:
            # Handle the case where the login button or success element is not found
            print("Login failed. Incorrect email or password.")
        except Exception as e:
            print("Login failed. Incorrect email or password.", str(e))
                
        
        xpath_pics = "//div[contains(@class, 'x6s0dn4') and contains(@class, 'x78zum5') and contains(@class, 'xdt5ytf') and contains(@class, 'x1iyjqo2') and contains(@class, 'xl56j7k') and contains(@class, 'x1jx94hy') and contains(@class, 'x1ymw6g') and contains(@class, 'x1n2xptk') and contains(@class, 'xkbpzyx') and contains(@class, 'xdppsyt') and contains(@class, 'x1rr5fae') and contains(@class, 'x1lcm9me') and contains(@class, 'x1yr5g0i') and contains(@class, 'xrt01vj') and contains(@class, 'x10y3i5r')]"
        xpath_expression = "// *[contains(@aria-label, 'Title')]"
        xpath_expression2 = "//a[contains(@class, 'x1i10hfl') and contains(@class, 'xjbqb8w') and contains(@class, 'x6umtig') and contains(@class, 'x1b1mbwd') and contains(@class, 'xaqea5y') and contains(@class, 'xav7gou') and contains(@class, 'x1ypdohk') and contains(@class, 'xe8uvvx') and contains(@class, 'xdj266r') and contains(@class, 'x11i5rnm') and contains(@class, 'xat24cr') and contains(@class, 'x1mh8g0r') and contains(@class, 'xexx8yu') and contains(@class, 'x4uap5') and contains(@class, 'x18d9i69') and contains(@class, 'xkhd6sd') and contains(@class, 'x16tdsg8') and contains(@class, 'x1hl2dhg') and contains(@class, 'xggy1nq') and contains(@class, 'x1o1ewxj') and contains(@class, 'x3x9cwd') and contains(@class, 'x1e5q0jg') and contains(@class, 'x13rtm0m') and contains(@class, 'x87ps6o') and contains(@class, 'x1lku1pv') and contains(@class, 'x1a2a7pz') and contains(@class, 'x9f619') and contains(@class, 'x3nfvp2') and contains(@class, 'xdt5ytf') and contains(@class, 'xl56j7k') and contains(@class, 'x1n2onr6') and contains(@class, 'xh8yej3') and contains(@aria-label, 'Create new listing') and contains(@href, '/marketplace/create/') and contains(@role, 'link') and contains(@tabindex, '0')]"
        item_xpath = "//a[contains(@class, 'x1i10hfl') and contains(@class, 'x1qjc9v5') and contains(@class, 'xjbqb8w') and contains(@class, 'xjqpnuy') and contains(@class, 'xa49m3k') and contains(@class, 'xqeqjp1') and contains(@class, 'x2hbi6w') and contains(@class, 'x13fuv20') and contains(@class, 'xu3j5b3') and contains(@class, 'x1q0q8m5') and contains(@class, 'x26u7qi') and contains(@class, 'x972fbf') and contains(@class, 'xcfux6l') and contains(@class, 'x1qhh985') and contains(@class, 'xm0m39n') and contains(@class, 'x9f619') and contains(@class, 'x1ypdohk') and contains(@class, 'xdl72j9') and contains(@class, 'x2lah0s') and contains(@class, 'xe8uvvx') and contains(@class, 'xdj266r') and contains(@class, 'x11i5rnm') and contains(@class, 'xat24cr') and contains(@class, 'x1mh8g0r') and contains(@class, 'xeuugli') and contains(@class, 'xexx8yu') and contains(@class, 'x4uap5') and contains(@class, 'x18d9i69') and contains(@class, 'xkhd6sd') and contains(@class, 'x1n2onr6') and contains(@class, 'x16tdsg8') and contains(@class, 'x1hl2dhg') and contains(@class, 'xggy1nq') and contains(@class, 'x1ja2u2z') and contains(@class, 'x1t137rt') and contains(@class, 'x1o1ewxj') and contains(@class, 'x3x9cwd') and contains(@class, 'x1e5q0jg') and contains(@class, 'x13rtm0m') and contains(@class, 'x87ps6o') and contains(@class, 'x1lku1pv') and contains(@class, 'x1a2a7pz') and contains(@class, 'x78zum5') and contains(@class, 'x1us19tq') and contains(@class, 'xh8yej3')]"
        price_xpath = "//*[contains(@aria-label, 'Price')]"

        createb = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath_expression2)))
        createb.click()
        item = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, item_xpath)))
        item.click()
        wait = WebDriverWait(driver, 10)

        image_folder_path = photopath
        video_folder_path = photopath

        image_files = [os.path.join(root, file) for root, dirs, files in os.walk(image_folder_path) for file in files if file.lower().endswith(('.png', '.jpg', '.jpeg'))]

        video_files = [os.path.join(root, file) for root, dirs, files in os.walk(video_folder_path) for file in files if file.lower().endswith(('.mp4', '.mov', '.avi'))]

        image_input_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[class="x1s85apg"][accept^="image/"]')))

        video_input_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[class="x1s85apg"][accept^="video/"]')))

        for image_file in image_files:
            image_input_element.send_keys(image_file)

        for video_file in video_files:
            video_input_element.send_keys(video_file)
        title = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath_expression)))
        title.send_keys(name)
        print(type(price), price)
        yes = int(price)
        price = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, price_xpath)))
        price.send_keys(yes)
        dropdown_label = driver.find_element(By.XPATH, "//label[@aria-label='Condition']")
        dropdown_label.click()
        options_locator = '//div[@role="option"]'
        options = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, options_locator)))
        desired_option = condition
        for option in options:
            if option.text == condition:
                option.click()
                break
        category = driver.find_element(By.XPATH, "//label[@aria-label='Category']")
        category.send_keys('yeesyesyes')
        mored = driver.find_element(By.XPATH, '//div[@aria-expanded="false" and contains(@class, "x1i10hfl") and contains(@class, "x1qjc9v5") and contains(@class, "xjbqb8w") and contains(@class, "xjqpnuy") and contains(@class, "xa49m3k") and contains(@class, "xqeqjp1") and contains(@class, "x2hbi6w") and contains(@class, "x13fuv20") and contains(@class, "xu3j5b3") and contains(@class, "x1q0q8m5") and contains(@class, "x26u7qi") and contains(@class, "x972fbf") and contains(@class, "xcfux6l") and contains(@class, "x1qhh985") and contains(@class, "xm0m39n") and contains(@class, "x9f619") and contains(@class, "x1ypdohk") and contains(@class, "xdl72j9") and contains(@class, "x2lah0s") and contains(@class, "xe8uvvx") and contains(@class, "xdj266r") and contains(@class, "x11i5rnm") and contains(@class, "xat24cr") and contains(@class, "x1mh8g0r") and contains(@class, "x2lwn1j") and contains(@class, "xeuugli") and contains(@class, "xexx8yu") and contains(@class, "x4uap5") and contains(@class, "x18d9i69") and contains(@class, "xkhd6sd") and contains(@class, "x1n2onr6") and contains(@class, "x16tdsg8") and contains(@class, "x1hl2dhg") and contains(@class, "xggy1nq")]')
        mored.click()
        description = driver.find_element(By.XPATH, '//label[@aria-label="Description"]')
        driver.execute_script("arguments[0].scrollIntoView();", mored)
        print(description)
        yes = str(descriptionn)
        description.send_keys(yes)
        sleep(1000)
        next = driver.find_element(By.XPATH, '//div[@aria-label="Next" and contains(@class, "x1i10hfl") and contains(@class, "xjbqb8w") and contains(@class, "x6umtig") and contains(@class, "x1b1mbwd") and contains(@class, "xaqea5y") and contains(@class, "xav7gou") and contains(@class, "x1ypdohk") and contains(@class, "xe8uvvx") and contains(@class, "xdj266r") and contains(@class, "x11i5rnm") and contains(@class, "xat24cr") and contains(@class, "x1mh8g0r") and contains(@class, "xexx8yu") and contains(@class, "x4uap5") and contains(@class, "x18d9i69") and contains(@class, "xkhd6sd") and contains(@class, "x16tdsg8") and contains(@class, "x1hl2dhg") and contains(@class, "xggy1nq") and contains(@class, "x1o1ewxj") and contains(@class, "x3x9cwd")]')
        driver.execute_script("arguments[0].scrollIntoView();", next)
        next.click()
        sleep(1000)
        driver.quit()
        sleep(1000)
        locinput = driver.find_element(By.XPATH, '#\:r13\:')
        locinput.send_keys("bexleyheath")
        sleep(10000)
        
    except KeyboardInterrupt:      
        print("KeyboardInterrupt received. Closing the script...")
    except Exception as e:
        print("An error occurred:", str(e))

        
# Function to handle script termination on SIGINT (Ctrl+C)
def stop_script(signum, frame):
    global keep_running
    keep_running = False
    sys.exit(0)

# Entry point of the script
if __name__ == "__main__":
    # Setting up signal handler for SIGINT
    signal.signal(signal.SIGINT, stop_script)
    # Calling the post function to start the Facebook posting process
    post('oliverfoben', 'Tomcat21!', '8', 'asdf')
