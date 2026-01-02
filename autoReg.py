import logging
import os
import threading
import time
import random
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AutoRegistor:
    def __init__(self, args):
        self.monthDict = {
            1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
            7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
        }
        self.inv_monthDict = {self.monthDict[k]: k for k in self.monthDict.keys()}
        self.equipmentDict = {
            0: ["ProtoMAX abrasive waterjet cutting machine", "https://innowingwaterjet.ycb.me"],
            1: ["CNC milling machine", "https://innowingcncmilling.ycb.me"]
        }
        self.debug = args.debug
        self.non_headless = args.non_headless

    def startBot(self, lastName, firstName, phoneNum, email, content, url, date, month):
        service = Service()
        options = webdriver.ChromeOptions()

        if not self.non_headless:
            options.add_argument("--headless=new")  # Use the new headless mode
            options.add_argument("--window-size=960,540")  # Crucial for headless
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Suppress Chrome logs and warnings
        options.add_argument("--log-level=3")  # Suppress INFO, WARNING, ERROR
        options.add_argument("--disable-logging")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-component-extensions-with-background-pages")
        options.add_argument("--disable-features=TranslateUI")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("detach", True) # Keep browser open for inspection
        
        driver = webdriver.Chrome(service=service, options=options)
        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
        wait = WebDriverWait(driver, timeout=2, poll_frequency=1, ignored_exceptions=ignored_exceptions)
        cookie_consent = True  # Flag to track if cookie consent has been clicked

        def human_click(element):
            try:
                # Scroll element into view first (helps in headless)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.1)
                
                actions = ActionChains(driver)
                actions.move_to_element(element)
                actions.move_by_offset(random.randint(-5, 5), random.randint(-5, 5))
                actions.pause(random.uniform(0.2, 0.5))
                actions.click()
                actions.perform()
            except Exception as e:
                logging.warning(f"Human click failed, falling back to standard click: {e}")
                try:
                    element.click()
                except Exception:
                    # JS Click fallback for stubborn elements in headless
                    driver.execute_script("arguments[0].click();", element)

        while True:
            driver.get(url)
            driver.implicitly_wait(10)

            if cookie_consent:
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='cookie_consent']/div/p/button")))
                    cookie_btn = driver.find_element(By.XPATH, "//div[@data-testid='cookie_consent']/div/p/button")
                    human_click(cookie_btn)
                    time.sleep(0.2)
                    cookie_consent = False
                except (NoSuchElementException, StaleElementReferenceException, TimeoutException):
                    logging.warning("Cookie consent button not found or already clicked.")

            # Navigate to correct month
            while True:
                actual_month = driver.find_element(By.XPATH, "//div[@data-testid='monthView']/div/div/div/div/span").text.split(" ")[0]
                if self.inv_monthDict[actual_month] != month:
                    if self.inv_monthDict[actual_month] < month:
                        human_click(driver.find_element(By.XPATH, "//button[@aria-label='Next Month']"))
                    else:
                        human_click(driver.find_element(By.XPATH, "//button[@aria-label='Previous Month']"))
                    driver.implicitly_wait(1)
                    continue
                break

            # Select date
            date_id = f"20{date[0:2]}-{date[2:4]}-{date[4:6]}"
            for i in range(3):
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, f"//button[@id='{date_id}']")))
                    time.sleep(1)
                    target_element = driver.find_element(By.XPATH, f"//button[@id='{date_id}']")
                    logging.info(f"Thread {date_id}: Button located for {date_id}")
                    human_click(target_element)
                    break
                except Exception:
                    logging.warning(f"Thread {date_id}: Failed to locate button for {date_id}...")
                    if i == 2:
                        if not self.debug:
                            driver.quit()
                        return

            # Select time slot
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button.avl_slot-free')))
            except Exception:
                logging.warning(f"Thread {date_id}: Failed to find time slot for {date_id}...")
                if not self.debug:
                    driver.quit()
                return

            logging.info(f"Thread {date_id}: Clicked date {date_id}")
            target_elements = driver.find_elements(By.CLASS_NAME, "avl_slot-free")
            logging.info(f"Thread {date_id}: Possible time slots: {len(target_elements)}")

            if not target_elements:
                logging.warning(f"Thread {date_id}: No time slots available for {date_id}")
                return

            time_slot = target_elements[0]
            time_slot_text = f"{time_slot.text} - {int(time_slot.text[0:2])+1}:00"
            human_click(time_slot)

            time_delay = 0.25
            
            # Select project
            wait.until(EC.presence_of_element_located((By.XPATH, '//div/div/select[@data-testid="Q5"]')))
            logging.info(f"Thread {date_id}: Found project select")
            project = driver.find_element(By.XPATH, '//div/div/select[@data-testid="Q5"]')
            
            human_click(project)

            # Click the option directly (options don't support move_to_element well)
            project_select = project.find_elements(By.TAG_NAME, 'option')[8]
            time.sleep(time_delay)
            project_select.click()

            # Enter member information
            last_name_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//div/input[@data-testid='LNAME']")))
            last_name_field.send_keys(lastName)
            time.sleep(time_delay)

            first_name_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//div/input[@data-testid='FNAME']")))
            first_name_field.send_keys(firstName)
            time.sleep(time_delay)

            phone_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@data-testid='PHONE']")))
            phone_field.send_keys(phoneNum)
            time.sleep(time_delay)

            email_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//div/input[@data-testid='EMAIL']")))
            email_field.send_keys(email)
            time.sleep(time_delay)

            job_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//div/textarea[@data-testid='JOB']")))
            job_field.send_keys(content)
            time.sleep(time_delay)

            human_click(driver.find_element(By.XPATH, "//div/div/input[@data-testid='Q8']"))
            driver.implicitly_wait(1.5)
            
            # Submit form
            while True:
                try:
                    confirm_btn = driver.find_element(By.XPATH, "//button[@data-testid='confirm_button']")
                    human_click(confirm_btn)

                    # Check for captcha error popup
                    try:
                        refresh_button_xpath = "//button[span[contains(text(), 'Refresh the page')]]"
                        refresh_btn = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, refresh_button_xpath)))
                        logging.warning(f"Thread {date_id}: Captcha error detected. Clicking 'Refresh the page'.")
                        human_click(refresh_btn)
                        continue  # Retry submission
                    except Exception:
                        pass

                    break
                except Exception:
                    logging.warning(f"Thread {date_id}: Failed to click confirm button")
                    driver.implicitly_wait(0.5)


            try:
                wait = WebDriverWait(driver, timeout=8, poll_frequency=1, ignored_exceptions=ignored_exceptions)
                wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='bookingInformation']")))
                logging.info(f"Thread {date_id}: Submitted successfully for {date_id} ({time_slot_text})")
                if len(target_elements) == 1:
                    break
            except Exception:
                logging.warning(f"Thread {date_id}: Failed to submit for {date_id} ({time_slot_text})")

        if not self.debug:
            driver.quit()

    def register_multiple_dates_thread(self, lastName, firstName, phoneNum, email, content, url, dates, month):
        threads = []
        for date in dates:
            thread = threading.Thread(
                target=self.startBot,
                args=(lastName, firstName, phoneNum, email, content, url, date, month)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def register_multiple_dates(self, lastName, firstName, phoneNum, email, content, url, dates, month):
        for date in dates:
            self.startBot(lastName, firstName, phoneNum, email, content, url, date, month)

    def run_cli(self):
        file_path = os.path.join(os.path.dirname(__file__), 'userInfo.txt')
        # Load user info
        user_info = {}
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
                for line in lines:
                    info_type, data = map(str.strip, line.split(": ", 1))
                    user_info[info_type] = data
                    logging.info(f"{info_type: >15}: {data}")
        except FileNotFoundError:
            logging.error("userInfo.txt not found.")
            return

        # Equipment selection
        for key in self.equipmentDict:
            logging.info(f"[{key}]: {self.equipmentDict[key][0]}")
        equipment = -1
        while equipment not in self.equipmentDict:
            equipment = input("Equipment: ")
            try:
                equipment = int(equipment)
            except Exception:
                continue

        # Date input for testing
        dates = input("Dates (comma-separated, Format: YYMMDD, e.g., 250501,250503): ").split(",")
        dates = [date.strip() for date in dates]
        month = int(dates[0][2:4].lstrip("0"))
        url = self.equipmentDict[equipment][1]

        self.register_multiple_dates(
            lastName=user_info.get("Last Name", ""),
            firstName=user_info.get("First Name", ""),
            phoneNum=user_info.get("Phone Number", ""),
            email=user_info.get("Email", ""),
            content=user_info.get("Content", ""),
            url=url,
            dates=dates,
            month=month
        )

def main(args):
    registrar = AutoRegistor(args)
    registrar.run_cli()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto Booking Calendar Application")
    parser.add_argument('-d', '--debug', action='store_false', help='Run the application in debug mode')
    parser.add_argument( '-n', '--non_headless', action='store_true', help='Run the application in headless mode')

    main(parser.parse_args())