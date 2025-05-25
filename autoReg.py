import logging
import os
import threading
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AutoRegistor:
    def __init__(self):
        self.monthDict = {
            1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
            7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
        }
        self.inv_monthDict = {self.monthDict[k]: k for k in self.monthDict.keys()}
        self.equipmentDict = {
            0: ["ProtoMAX abrasive waterjet cutting machine", "https://innowingwaterjet.ycb.me"],
            1: ["CNC milling machine", "https://innowingcncmilling.ycb.me"]
        }

    def startBot(self, lastName, firstName, phoneNum, email, content, url, date, month):
        service = Service()
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        driver = webdriver.Chrome(service=service, options=options)
        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
        wait = WebDriverWait(driver, timeout=2, poll_frequency=1, ignored_exceptions=ignored_exceptions)
        cookie_consent = False  # Flag to track if cookie consent has been clicked

        while True:
            driver.get(url)
            driver.implicitly_wait(10)

            if cookie_consent:
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='cookie_consent']/div/p/button")))
                    driver.find_element(By.XPATH, "//div[@data-testid='cookie_consent']/div/p/button").click()
                    time.sleep(0.2)
                    cookie_consent = False
                except (NoSuchElementException, StaleElementReferenceException, TimeoutException):
                    logging.warning("Cookie consent button not found or already clicked.")

            # Navigate to correct month
            while True:
                actual_month = driver.find_element(By.XPATH, "//div[@data-testid='monthView']/div/div/div/div/span").text.split(" ")[0]
                if self.inv_monthDict[actual_month] != month:
                    if self.inv_monthDict[actual_month] < month:
                        driver.find_element(By.XPATH, "//button[@aria-label='Next Month']").click()
                    else:
                        driver.find_element(By.XPATH, "//button[@aria-label='Previous Month']").click()
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
                    target_element.click()
                    break
                except Exception:
                    logging.warning(f"Thread {date_id}: Failed to locate button for {date_id}...")
                    if i == 2:
                        driver.quit()
                        return

            # Select time slot
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button.avl_slot-free')))
            except Exception:
                logging.warning(f"Thread {date_id}: Failed to find time slot for {date_id}...")
                driver.quit()
                return

            logging.info(f"Thread {date}: Clicked date {date_id}")
            target_elements = driver.find_elements(By.CLASS_NAME, "avl_slot-free")
            logging.info(f"Thread {date}: Possible time slots: {len(target_elements)}")

            if not target_elements:
                logging.warning(f"Thread {date}: No time slots available for {date_id}")
                return

            time_slot = target_elements[0]
            time_slot.click()

            # Select project
            wait.until(EC.presence_of_element_located((By.XPATH, '//div/div/select[@data-testid="Q5"]')))
            logging.info(f"Thread {date}: Found project select")
            project = driver.find_element(By.XPATH, '//div/div/select[@data-testid="Q5"]')
            project.click()
            project_select = project.find_elements(By.TAG_NAME, 'option')[8]
            project_select.click()
            project.click()

            # Enter member information
            driver.find_element(By.XPATH, "//div/input[@data-testid='LNAME']").send_keys(lastName)
            driver.implicitly_wait(1.5)
            driver.find_element(By.XPATH, "//div/input[@data-testid='FNAME']").send_keys(firstName)
            driver.implicitly_wait(1.5)
            driver.find_element(By.XPATH, "//input[@data-testid='PHONE']").send_keys(phoneNum)
            driver.implicitly_wait(1.5)
            driver.find_element(By.XPATH, "//div/input[@data-testid='EMAIL']").send_keys(email)
            driver.implicitly_wait(1.5)
            driver.find_element(By.XPATH, "//div/textarea[@data-testid='JOB']").send_keys(content)
            driver.implicitly_wait(1.5)
            driver.find_element(By.XPATH, "//div/div/input[@data-testid='Q8']").click()
            driver.implicitly_wait(1.5)
            ActionChains(driver).move_to_element(driver.find_element(By.XPATH, "//button[@data-testid='confirm_button']")).perform()

            # Submit form
            while True:
                try:
                    driver.find_element(By.XPATH, "//button[@data-testid='confirm_button']/span").click()
                    break
                except Exception:
                    logging.warning(f"Thread {date}: Failed to click confirm button")
                    driver.implicitly_wait(0.5)

            try:
                wait = WebDriverWait(driver, timeout=8, poll_frequency=1, ignored_exceptions=ignored_exceptions)
                wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='bookingInformation']")))
                logging.info(f"Thread {date}: Submitted successfully for {date_id}")
                if len(target_elements) == 1:
                    break
            except Exception:
                logging.warning(f"Thread {date}: Failed to submit for {date_id}...")

        driver.quit()

    def register_multiple_dates(self, lastName, firstName, phoneNum, email, content, url, dates, month):
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

def main():
    registrar = AutoRegistor()
    registrar.run_cli()

if __name__ == "__main__":
    main()