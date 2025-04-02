# Pre-requisite: install selenium
# open terminal and input "pip install selenium" to install selenium

# Used to import the webdriver from selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait
import os
import time
from selenium.webdriver.common.action_chains import ActionChains
 
# Get the path of chromedriver which you have install

def startBot(lastName, firstName, phoneNum, email, content, url, date, month):

    monthDict = {
        1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"    
    }
    inv_monthDict = {monthDict[k]: k for k in monthDict.keys()}

    service = Service()
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)


    # giving the path of chromedriver to selenium webdriver
    # driver = webdriver.Chrome(excutable_path = path)
    
    while (True):
        wait = WebDriverWait(driver, timeout=5, poll_frequency=1, ignored_exceptions=ignored_exceptions)
        
        # opening the website in chrome.
        driver.get(url)
        driver.implicitly_wait(10)

        actual_month = driver.find_element(By.XPATH, "//div[@data-testid='monthView']/div/div/div/div/span").text.split(" ")[0]

        print("Actual month: " + actual_month)
        # test if the month is correct
        if (inv_monthDict[actual_month] != month):
            if (inv_monthDict[actual_month] < month):
                driver.find_element(By.XPATH, "//button[@aria-label='Next Month']/span/svg").click()
            else:
                driver.find_element(By.XPATH, "//button[@aria-label='Previous Month']/span/svg").click()

            continue
        
        while True:
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, "//button[@id='" + date + "']")))
                target_element = driver.find_element(By.XPATH, "//button[@id='" + date + "']")
                print("Button located")
                time.sleep(1)
                target_element.click()
                break
            except:
                print("Fail to locate the button...")

        # driver.execute_script("var ele = arguments[0];ele.addEventListener('click', function() {ele.setAttribute('automationTrack','false');});",target_element)

        # while not target_element.get_attribute("automationTrack"):
        #     target_element.click()
        #     driver.execute_script("var ele = arguments[0];ele.addEventListener('click', function() {ele.setAttribute('automationTrack','false');});",target_element)
        # print("First clicked: okay")

        # track if the element is clicked
        # driver.execute_script("var ele = arguments[0];ele.addEventListener('click', function() {ele.setAttribute('automationTrack','true');});", target_element)

        # print("Clicked: " + str(target_element.get_attribute("automationTrack")))
        # while not target_element.get_attribute("automationTrack"):
        #     print("Failed to click: " + date)
        #     target_element = driver.find_elements(By.ID, date)
        #     target_element[0].click()
        #     time.sleep(1)
        
        # element = driver.find_element(By.ID, date)
        # if element: break

        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button.avl_slot-free')))
        except:
            if not EC.presence_of_element_located((By.CSS_SELECTOR, 'button.avl_slot-free')):
                target_element = driver.find_element(By.ID, date)
                target_element.click()
            print("Fail to proceed...")
            return

        print("Clicked: " + date)
        print('\t', end='')
        # print(target_element)

        # target_element is a list containing the possible time slots
        target_elements = driver.find_elements(By.CLASS_NAME, "avl_slot-free")
        # module__slot_column___2m3E8 
        print("Possible time slot: " + str(len(target_elements)))

        time_slot = target_elements[0]
        print('\t', end='')
        print(time_slot)
        time_slot.click()
        # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div._questionSelect_14epn_7')))
        wait.until(EC.presence_of_element_located((By.XPATH, '//div/div/select[@data-testid="Q5"]')))
        print("Found select")

        # Select the project
        project = driver.find_element(By.XPATH, '//div/div/select[@data-testid="Q5"]')
        project.click()
        # hard code to select the 8th option
        project_select = project.find_elements(By.TAG_NAME, 'option')[8]
        project_select.click()
        project.click()

        # Member information
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
        while True:
            try:
                driver.find_element(By.XPATH, "//button[@data-testid='confirm_button']/span").click()
            except:
                print("Fail to click the confirm button")
                time.sleep(1)
                continue
            break
        driver.implicitly_wait(1.5)


        try:
            wait = WebDriverWait(driver, timeout=8, poll_frequency=1, ignored_exceptions=ignored_exceptions)
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='bookingInformation']")))
            print("Submitted successfully")
        except:
            print("Failed to submit...")

        driver.implicitly_wait(10)


def main():
    # Driver Code
    # Enter below your login credentials
    file_path = os.path.join(os.path.dirname(__file__), 'userInfo.txt')

    equipmentDict = {
        # ProtoMAX abrasive waterjet cutting machine
        0: ["ProtoMAX abrasive waterjet cutting machine", "https://innowingwaterjet.ycb.me"],
        # CNC milling machine
        1: ["CNC milling machine", "https://innowingcncmilling.ycb.me"]
    }

    f = open(file_path, "r")
    userInfo = f.readlines()
    for i in range(len(userInfo)):
        infoType = userInfo[i].split(": ")[0].strip()
        data = userInfo[i].split(": ")[1].strip()
        print('{0: >15}'.format(infoType) + ": " + data)

        # input data to the corresponding variable
        match infoType:
            case "Last Name":
                lastName = data
            case "First Name":
                firstName = data
            case "Phone Number":
                phoneNum = data
            case "Email":
                email = data
            case "Content":
                content = data
            case _:
                print("Invalid data")
    f.close()

    for key in equipmentDict:
        print("[" + str(key) + "]: " + equipmentDict[key][0])
    equipment = -1
    while equipment not in equipmentDict:
        equipment = input("Equipment: ")
        try:
            equipment = int(equipment)
        except:
            continue
    
    date = input("Date (Format: YYMMDD): ")
    month = int(date[2:4].lstrip("0"))
    date = "20" + date[0:2] + "-" + date[2:4] + "-" + date[4:6]
    print(date)
    url = equipmentDict[equipment][1]
    # lastName = input("Last Name: ")
    # firstName = input("First Name: ")
    # phoneNum = input("Phone Number (+852): ")
    # email = input("HKU Email: ")
    # content = "Robocon"
    print("Please wait...")

    startBot(lastName, firstName, phoneNum, email, content, url, date, month)

main()