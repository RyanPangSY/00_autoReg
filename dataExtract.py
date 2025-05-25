from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait
import time
from threading import Thread


class ReturnableThread(Thread):
    # This class is a subclass of Thread that allows the thread to return a value.
    def __init__(self, target, args):
        Thread.__init__(self)
        self.target = target
        self.args = args
        self.result = None
    
    def run(self) -> None:
        self.result = self.target(self.args)


class DataExtractor:
    def __init__(self):
        self.equipmentDict = {
            # ProtoMAX abrasive waterjet cutting machine
            0: ["ProtoMAX abrasive waterjet cutting machine", "https://innowingwaterjet.ycb.me"],
            # CNC milling machine
            1: ["CNC milling machine", "https://innowingcncmilling.ycb.me"]
        }
        self.monthDict = {
            1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
            7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
        }
        self.inv_monthDict = {self.monthDict[k]: k for k in self.monthDict.keys()}

        self.service = Service()
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless")  # Run in headless mode
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.div_xpath = "//div[@data-testid='selectTimeScreenCalendar']/div/div/div/div/div/div"
        print("Extractor initialized")

    def extractData(self, equipmentIndex=0):
        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
        wait = WebDriverWait(self.driver, timeout=2, poll_frequency=1, ignored_exceptions=ignored_exceptions)

        self.driver.get(self.equipmentDict[equipmentIndex][1])
        self.driver.implicitly_wait(1)

        # finding the select time calendar element and extracting the data
        wait.until(EC.presence_of_element_located((By.XPATH, self.div_xpath + "/button/span")))
        time.sleep(2.5)  # wait for the calendar to load

        calendar_data = self.driver.find_elements(By.XPATH, self.div_xpath + "/button")

        date_available_list = [False]
        current_month = self.driver.find_element(By.XPATH, "//div[@data-testid='monthView']/div/div/div/div/span").text.split(" ")[0]
        
        for date_div in calendar_data:
            date_available_list.append(date_div.get_attribute("aria-disabled") == "false")

        date_available_list_next_month= [False]
        try:
            # driver.find_element(By.XPATH, "//button[@aria-label='Next Month']").click()
            self.driver.execute_script("arguments[0].click();", wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Next Month']"))))
            self.driver.implicitly_wait(1)
            wait.until(EC.presence_of_element_located((By.XPATH, self.div_xpath + "/button")))
            time.sleep(3)  # wait for the next month calendar to load
            next_month = self.driver.find_element(By.XPATH, "//div[@data-testid='monthView']/div/div/div/div/span").text.split(" ")[0]
            calendar_data_next_month = self.driver.find_elements(By.XPATH, self.div_xpath + "/button")
            for date_div in calendar_data_next_month:
                date_available_list_next_month.append(date_div.get_attribute("aria-disabled") == "false")
        except NoSuchElementException:
            date_available_list_next_month = []
            print("No next month button found, assuming end of calendar.")
        self.driver.quit()

        # for i in range(1, len(calendar_data)+1):
        #     print("Date:", i, "\tAvailable:", data_available_list[i])
        
        return {self.inv_monthDict[current_month]: date_available_list, self.inv_monthDict[next_month]: date_available_list_next_month}
    
    def extractMultipleData(self):
        threads = []
        results = {}
        for i in range(len(self.equipmentDict)):
            print(f"Starting thread for {self.equipmentDict[i][0]}...")
            extractor = DataExtractor()
            thread = ReturnableThread(target=extractor.extractData, args=i)
            print("Obtaining date availability for", self.equipmentDict[i][0], 'from the website...')
            thread.start()
            threads.append(thread)

        # Wait for the thread to finish
        for thread in threads:
            thread.join()
        
        # Print the result
        for i, thread in enumerate(threads):
            results[i] = thread.result

        return results


def main():
    extractor = DataExtractor()
    extracted_data = extractor.extractMultipleData()
    print("Extracted Data:", extracted_data)

if __name__ == "__main__":
    main()