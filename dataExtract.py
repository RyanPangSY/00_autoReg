from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait
import time
import yaml
# from selenium.webdriver_manager.chrome import ChromeDriverManager


# aria-disabled="false"

def extractData():
    equipmentDict = {
        # ProtoMAX abrasive waterjet cutting machine
        0: ["ProtoMAX abrasive waterjet cutting machine", "https://innowingwaterjet.ycb.me"],
        # CNC milling machine
        1: ["CNC milling machine", "https://innowingcncmilling.ycb.me"]
    }

    monthDict = {
        1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
        7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
    }
    inv_monthDict = {monthDict[k]: k for k in monthDict.keys()}

    service = Service()
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(service=service, options=options)
    ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
    wait = WebDriverWait(driver, timeout=1, poll_frequency=1, ignored_exceptions=ignored_exceptions)

    driver.get(equipmentDict[0][1])
    driver.implicitly_wait(1)

    # finding the select time calendar element and extracting the data
    div_xpath = "//div[@data-testid='selectTimeScreenCalendar']/div/div/div/div/div/div"
    wait.until(EC.presence_of_element_located((By.XPATH, div_xpath + "/button/span")))
    time.sleep(3)  # wait for the calendar to load

    calendar_data = driver.find_elements(By.XPATH, div_xpath + "/button")

    date_available_list = [False]
    current_month = driver.find_element(By.XPATH, "//div[@data-testid='monthView']/div/div/div/div/span").text.split(" ")[0]
    
    for date_div in calendar_data:
        date_available_list.append(date_div.get_attribute("aria-disabled") == "false")

    date_available_list_next_month= [False]
    try:
        driver.find_element(By.XPATH, "//button[@aria-label='Next Month']").click()
        driver.implicitly_wait(1)
        wait.until(EC.presence_of_element_located((By.XPATH, div_xpath + "/button")))
        time.sleep(3)  # wait for the next month calendar to load
        next_month = driver.find_element(By.XPATH, "//div[@data-testid='monthView']/div/div/div/div/span").text.split(" ")[0]
        calendar_data_next_month = driver.find_elements(By.XPATH, div_xpath + "/button")
        for date_div in calendar_data_next_month:
            date_available_list_next_month.append(date_div.get_attribute("aria-disabled") == "false")
    except NoSuchElementException:
        date_available_list_next_month = []
        print("No next month button found, assuming end of calendar.")
    driver.quit()

    # for i in range(1, len(calendar_data)+1):
    #     print("Date:", i, "\tAvailable:", data_available_list[i])
        
    with open('data/date.yaml', 'w') as file:
        yaml.dump({inv_monthDict[current_month]: date_available_list, inv_monthDict[next_month]: date_available_list_next_month}, file)
        print("Data saved to date.yaml")

def main():
    extractData()

if __name__ == "__main__":
    main()