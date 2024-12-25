import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import uuid
import time
import random
from pymongo import MongoClient

class TwitterScraper:
    def __init__(self, twitter_username, twitter_password):
        # Initialize Twitter credentials
        self.twitter_username = twitter_username
        self.twitter_password = twitter_password
        self.ip_address = None

    def setup_driver(self):
        """Setup Chrome WebDriver"""
        chrome_options = Options()

        # Additional options to mimic a regular browser
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Set user agent to avoid detection
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # Initialize the driver
        driver = webdriver.Chrome(options=chrome_options)

        # Additional settings to avoid detection
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver

    def get_public_ip(self):
        """Fetch the public IP address of the machine"""
        try:
            response = requests.get("https://api.ipify.org?format=json", timeout=10)
            response.raise_for_status()
            ip_data = response.json()
            self.ip_address = ip_data['ip']
            print(f"Public IP: {self.ip_address}")
            return self.ip_address
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch public IP: {str(e)}")
            return "IP fetch failed"

    def random_sleep(self, min_seconds=2, max_seconds=5):
        """Add random delays to mimic human behavior"""
        time.sleep(random.uniform(min_seconds, max_seconds))

    def type_like_human(self, element, text):
        """Type text with random delays between keystrokes"""
        for character in text:
            element.send_keys(character)
            time.sleep(random.uniform(0.1, 0.3))

    def handle_security_challenge(self, driver):
        """Handle various security challenges that might appear"""
        try:
            verification_prompt = driver.find_elements(By.XPATH, "//span[contains(text(), 'Verify')]")
            if verification_prompt:
                raise Exception("Twitter requires additional verification. Please log in manually once to verify your account.")

            unusual_activity = driver.find_elements(By.XPATH, "//span[contains(text(), 'unusual')]")
            if unusual_activity:
                self.random_sleep(5, 8)
                proceed_button = driver.find_element(By.XPATH, "//span[contains(text(), 'Continue')]")
                proceed_button.click()

            captcha = driver.find_elements(By.XPATH, "//iframe[contains(@title, 'recaptcha')]")
            if captcha:
                raise Exception("CAPTCHA detected. Please solve it manually.")
                
        except Exception as e:
            raise Exception(f"Security challenge encountered: {str(e)}")

    def login_to_twitter(self, driver):
        """Log in to Twitter with the provided credentials"""
        try:
            driver.delete_all_cookies()
            driver.get("https://twitter.com/i/flow/login")
            self.random_sleep(3, 5)
            
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='username']"))
            )
            self.type_like_human(username_field, self.twitter_username)
            self.random_sleep(1, 2)
            
            next_button = driver.find_element(By.XPATH, "//span[text()='Next']")
            next_button.click()
            self.random_sleep(2, 3)
            
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))
            )
            self.type_like_human(password_field, self.twitter_password)
            self.random_sleep(1, 2)
            
            login_button = driver.find_element(By.XPATH, "//span[text()='Log in']")
            login_button.click()
            self.random_sleep(3, 5)
            
            self.handle_security_challenge(driver)
            
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//span[text()='Home']"))
            )
        except Exception as e:
            raise Exception(f"Login failed: {str(e)}")

    def get_trending_topics(self):
        """Scrape trending topics from Twitter"""
        self.get_public_ip()
        driver = self.setup_driver()
        
        try:
            self.login_to_twitter(driver)
            self.random_sleep(3, 5)
            
            trending_section = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label, 'Timeline: Trending now')]"))
            )
            
            trending_topics = []
            topics = trending_section.find_elements(By.XPATH, ".//span[starts-with(text(), '#')]")
            
            for topic in topics[:5]:
                text = topic.text.strip()
                if text and text not in trending_topics:
                    trending_topics.append(text)
            
            while len(trending_topics) < 5:
                trending_topics.append("No trend available")
            
            record = {
                "_id": str(uuid.uuid4()),
                "nameoftrend1": trending_topics[0],
                "nameoftrend2": trending_topics[1],
                "nameoftrend3": trending_topics[2],
                "nameoftrend4": trending_topics[3],
                "nameoftrend5": trending_topics[4],
                "timestamp": datetime.now(),
                "ip_address": self.ip_address
            }
            return record
        finally:
            driver.quit()

    def save_to_mongodb(self, record):
        """Save the record to MongoDB"""
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['twitter_trends']
            collection = db['trending_topics']
            
            # Convert datetime to string for proper JSON serialization
            record['timestamp'] = record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            
            # Insert the record and return the inserted document
            inserted_id = collection.insert_one(record).inserted_id
            saved_record = collection.find_one({"_id": inserted_id})
            return saved_record
        except Exception as e:
            print(f"MongoDB Error: {str(e)}")
            raise
        finally:
            client.close()

    def run_scraper(self):
        """Run the Twitter scraper"""
        try:
            record = self.get_trending_topics()
            saved_record = self.save_to_mongodb(record)
            print("Scraped and saved record:", saved_record)
            return saved_record
        except Exception as e:
            print(f"Scraper Error: {str(e)}")
            raise

# Example usage
if __name__ == "__main__":
    scraper = TwitterScraper(
        twitter_username='your_twitter_username',
        twitter_password='your_twitter_password'
    )
    
    scraper.run_scraper()
