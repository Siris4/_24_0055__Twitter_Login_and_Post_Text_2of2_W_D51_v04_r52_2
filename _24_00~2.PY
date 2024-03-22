import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

TWITTER_EMAIL = "YOUR_EMAIL"
TWITTER_PASSWORD = "YOUR_PASSWORD"
twitter_url = "https://twitter.com/"
search_keyword_within_twitter = "Comcast"

ACTUAL_DOWNLOAD_SPEED = 150
ACTUAL_UPLOAD_SPEED = 25

def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{timestamp} - {message}")

def init_driver():
    chrome_options = Options()
    chrome_options.page_load_strategy = 'eager'
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    log_message("Webdriver initialized.")
    return driver

def login_twitter(driver, email, password):
    start_time = time.time()
    driver.get(twitter_url)
    log_message("Twitter page loaded.")

    wait = WebDriverWait(driver, 10)
    try:
        sign_in_button_xpath = "//a[@href='/login']"
        sign_in_button = wait.until(EC.element_to_be_clickable((By.XPATH, sign_in_button_xpath)))
        sign_in_button.click()
        log_message("Sign-in button clicked.")

        selectors = [
            (By.XPATH, "//input[@name='session[username_or_email]']"),
            (By.CSS_SELECTOR, "input[autocomplete='username']"),
            (By.CSS_SELECTOR, "#react-root > div > div > div > main > div > div > div > div.css-175oi2r.r-1ny4l3l.r-6koalj.r-16y2uox > div.css-175oi2r.r-16y2uox.r-1jgb5lz.r-13qz1uu > div > div.css-175oi2r.r-1f1sjgu.r-mk0yit.r-13qz1uu > label > div > div.css-175oi2r.r-18u37iz.r-16y2uox.r-1wbh5a2.r-1wzrnnt.r-1udh08x.r-xd6kpl.r-1pn2ns4.r-ttdzmv > div > input"),
            (By.XPATH, "//*[@id='react-root']/div/div/div/main/div/div/div/div[2]/div[2]/div/div[5]/label/div/div[2]/div/input"),
            (By.XPATH, "/html/body/div/div/div/div/main/div/div/div/div[2]/div[2]/div/div[5]/label/div/div[2]/div/input"),
            (By.XPATH, "//input[@autocapitalize='sentences']")
        ]

        email_field = None
        for by, value in selectors:
            try:
                email_field = wait.until(EC.presence_of_element_located((by, value)))
                if email_field:
                    log_message("Email field found.")
                    break
            except TimeoutException:
                log_message(f"Email field not found using {by}='{value}'")

        if not email_field:
            raise Exception("Email field not found after trying all selectors.")

        email_field.send_keys(email)
        log_message("Email entered.")
        email_field.send_keys(Keys.RETURN)
        log_message("Email submitted.")

        password_selectors = [
            (By.NAME, 'password'),
            (By.CSS_SELECTOR, 'input[type="password"][autocomplete="current-password"]'),
            (By.CSS_SELECTOR, '.r-30o5oe'),
            (By.XPATH, "//input[@autocomplete='current-password']"),
            (By.XPATH, "//input[@type='password']")
        ]

        password_field = None
        for by, value in password_selectors:
            try:
                password_field = wait.until(EC.presence_of_element_located((by, value)))
                if password_field:
                    log_message("Password field found.")
                    break
            except TimeoutException:
                log_message(f"Password field not found with {by}='{value}'")

        if not password_field:
            raise Exception("Password field not found after trying all selectors.")

        password_field.send_keys(password)
        log_message("Password entered.")
        password_field.send_keys(Keys.RETURN)
        log_message("Login submitted.")

        end_time = time.time()
        total_time = end_time - start_time
        log_message(f"Login completed in {total_time:.2f} seconds.")

    except Exception as e:
        log_message(f"An error occurred during login: {str(e)}")

def navigate_to_twitter_explore(driver):
    wait = WebDriverWait(driver, 10)
    explore_button = None
    explore_selectors = [
        (By.CSS_SELECTOR, "#react-root > div > div > div.css-175oi2r.r-1f2l425.r-13qz1uu.r-417010.r-18u37iz > header > div > div > div > div:nth-child(1) > div.css-175oi2r.r-15zivkp.r-1bymd8e.r-13qz1uu.r-1awozwy > nav > a:nth-child(2) > div > div > svg"),
        (By.CSS_SELECTOR, "#react-root > div > div > div.css-175oi2r.r-1f2l425.r-13qz1uu.r-417010.r-18u37iz > header > div > div > div > div:nth-child(1) > div.css-175oi2r.r-15zivkp.r-1bymd8e.r-13qz1uu.r-1awozwy > nav > a:nth-child(2) > div > div"),
        (By.CSS_SELECTOR, "#react-root > div > div > div.css-175oi2r.r-1f2l425.r-13qz1uu.r-417010.r-18u37iz > header > div > div > div > div:nth-child(1) > div.css-175oi2r.r-15zivkp.r-1bymd8e.r-13qz1uu.r-1awozwy > nav > a:nth-child(2)"),
        (By.XPATH, "//a[@href='/explore']"),
        (By.XPATH, "//*[contains(@aria-label, 'Explore')]")
    ]

    for selector in explore_selectors:
        try:
            explore_button = wait.until(EC.element_to_be_clickable(selector))
            if explore_button:
                log_message("Explore button found.")
                explore_button.click()
                log_message("Navigated to Explore.")
                break
        except TimeoutException:
            log_message(f"Explore button not found using {selector[0]}='{selector[1]}'")

    if not explore_button:
        raise Exception("Explore button not found after trying all selectors.")

def search_twitter(driver, query):
    wait = WebDriverWait(driver, 10)
    search_xpath = "//input[@aria-label='Search query']"
    search_box = wait.until(EC.presence_of_element_located((By.XPATH, search_xpath)))
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    log_message(f"Searched for {query}.")


def prepare_tweet(driver, message):
    wait = WebDriverWait(driver, 10)
    try:
        # Click the post button to open the tweet box
        post_button_xpath = "//a[@aria-label='Post']"
        post_button = wait.until(EC.element_to_be_clickable((By.XPATH, post_button_xpath)))
        post_button.click()
        log_message("Post button clicked.")

        # Layered catch mechanism for tweet box selection
        tweet_box_selectors = [
            "//*[@id='layers']/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[3]/div[2]/div[1]/div/div/div/div[1]/div[2]/div/div/div/div/div/div/div/div/div/div/div/label/div[1]/div/div/div/div/div/div[2]/div/div/div/div",
            "div[data-offset-key='1q64k-0-0']",
            "#layers > div:nth-child(2) > div > div > div > div > div > div.css-175oi2r.r-1ny4l3l.r-18u37iz.r-1pi2tsx.r-1777fci.r-1xcajam.r-ipm5af.r-g6jmlv.r-1habvwh > div.css-175oi2r.r-1wbh5a2.r-htvplk.r-1udh08x.r-1867qdf.r-rsyp9y.r-1pjcn9w.r-1potc6q > div > div > div > div:nth-child(3) > div.css-175oi2r.r-kemksi.r-1h8ys4a.r-1moyyf3.r-1pp923h > div:nth-child(1) > div > div > div > div.css-175oi2r.r-18u37iz.r-184en5c > div.css-175oi2r.r-1iusvr4.r-16y2uox.r-1777fci.r-1h8ys4a.r-1bylmt5.r-13tjlyg.r-7qyjyx.r-1ftll1t > div > div > div > div > div > div > div > div > div > div > div > label > div.css-175oi2r.r-1wbh5a2.r-16y2uox > div > div > div > div > div > div.DraftEditor-editorContainer > div > div > div > div",
            "/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[3]/div[2]/div[1]/div/div/div/div[1]/div[2]/div/div/div/div/div/div/div/div/div/div/div/label/div[1]/div/div/div/div/div/div[2]/div/div/div/div"
        ]

        tweet_box = None
        for selector in tweet_box_selectors:
            try:
                if selector.startswith(("//", "/html")):
                    tweet_box = wait.until(EC.visibility_of_element_located((By.XPATH, selector)))
                else:
                    tweet_box = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                if tweet_box:
                    log_message("Tweet box found.")
                    break
            except TimeoutException:
                log_message(f"Tweet box not found using selector: {selector}")

        if not tweet_box:
            raise Exception("Tweet box not found after trying all selectors.")

        # Scroll the tweet box into view
        driver.execute_script("arguments[0].scrollIntoView();", tweet_box)

        tweet_box.send_keys(message)
        log_message("Message typed in the tweet box.")

        # Do not submit the tweet, only type the message into the tweet box
        # tweet_box.send_keys(Keys.RETURN)  # This line should remain commented to prevent posting

    except Exception as e:
        log_message(f"An error occurred while preparing the tweet: {str(e)}")



def main():
    driver = init_driver()
    login_twitter(driver, TWITTER_EMAIL, TWITTER_PASSWORD)
    navigate_to_twitter_explore(driver)
    search_twitter(driver, search_keyword_within_twitter)
    prepare_tweet(driver, f"Thank you for these speeds: {ACTUAL_DOWNLOAD_SPEED} Mbps Download and {ACTUAL_UPLOAD_SPEED} Mbps Upload")
    log_message("Browser will remain open until manually closed.")
    input("Press Enter to close the browser...")
    driver.quit()

if __name__ == "__main__":
    main()
