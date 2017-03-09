#! python3
# Lexusdealerdirect.com web scraper
# Version 1.1
# Written by Zach Cutberth

# Import the needed libraries.
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from twilio.rest import TwilioRestClient
import time, shelve, re, config, sys

# Twilio rest client
twilioCli = TwilioRestClient(config.accountSID, config.authToken)

# Initialize the browser.
browser = webdriver.Chrome()
browser.maximize_window() # For maximizing window
browser.implicitly_wait(20) # gives an implicit wait for 20 seconds
browser.get(config.websiteUrl)

# Login to the website.
def loginToWebsite():
    username = browser.find_element_by_id("Username")
    password = browser.find_element_by_id("bodyView:adesaLogin:Password")
    username.send_keys(config.userLogin)
    password.send_keys(config.userPassword)
    browser.find_element_by_id("bodyView:adesaLogin:login").click()
    try:
        browser.find_element_by_id("ddonline2").click()
    except:
        browser.find_element_by_id("ddonline").click()


# Scrape website and send sms message when a new car is found.
def scrapeWebsite():
    # Open shelf file for DB storage
    carsDb = shelve.open('lexusdealerdirectcars')

    # Create key for database if it hasn't already been created.
    if 'cars' not in carsDb:
        carsDb['cars'] = []

    # Initialize carList.
    carList = []

    # Set seach criteria through dropdown menus.
    distance = Select(browser.find_element_by_id('bodyView:searchResultsTable:searchResultsDataTableForm:searchResults:location'))
    distance.select_by_value('< 1,000 mi')
    #time.sleep(10)
    perPage = Select(browser.find_element_by_id('bodyView:searchResultsTable:searchResultsDataTableForm:pagination2:resultsPerPageSelector'))
    perPage.select_by_value('50')
    #time.sleep(30)

    element = WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.ID, 'button'))

    #for attempt in range(10):
        #try:
            # Find the table cell that has the car name and VIN.
    cars = browser.find_elements_by_xpath('//td[strong]')
        #except StaleElementReferenceException:
        #   time.sleep(5)

    # Loop through cars and append them to carList.
    for car in cars:
        #try:
       carList.append(car.text)
        #except:
        #    cars = browser.find_elements_by_xpath('//td[strong]')


    # Click the next results page button.
    try:
        browser.find_element_by_id('bodyView:searchResultsTable:searchResultsDataTableForm:pagination3:nextButtonImage').click()
        time.sleep(15)
    except:
        pass

    #for attempt in range(10):
        #try:
            # Find the table cell that has the car name and VIN.
    cars = browser.find_elements_by_xpath('//td[strong]')
        #except StaleElementReferenceException:
            #time.sleep(5)

    # Loop through cars and append them to carList.
    for car in cars:
        #try:
        carList.append(car.text)
        #except:
        #    cars = browser.find_elements_by_xpath('//td[strong]')

    print(carList)

    # Look for RX model cars that don't already exist in carsDb, then append them to carsDb and send a sms message.
    for car in carList:
        if 'RX' in car:
            # Parse the VIN to find all wheel drive cars.
            if re.search(r'\w{3}B\w{13}', car) is not None:
                if car not in carsDb['cars']:
                    print(car)
                    carsDbtemp = carsDb['cars']
                    carsDbtemp.append(car)
                    carsDb['cars'] = carsDbtemp
                    for cellPhone in config.myCellPhone:
                        message = twilioCli.messages.create(body=('Lexus Dealer Direct has a ' + car + ' for sale.'), from_=config.myTwilioNumber, to=cellPhone)

    # Close carsDb file.
    carsDb.close()

    time.sleep(5)
    # Go back to the Buy Direct Online page so that when the scrape function restarts we get new results.
    #try:
    browser.find_element_by_id('ddonline2').click()
    #except:
    #    browser.find_element_by_id('ddonline').click()

    #time.sleep(10)

# Keep scraping the website as long as the user is logged in. If not log in the user and restart loop.
def scrapeWebsiteLoop():
    while browser.find_element_by_class_name('user').text == config.userName:
        scrapeWebsite()
    else:
        loginToWebsite()
        scrapeWebsiteLoop()

# Call the login to website function.
loginToWebsite()

# Call the scrape website loop.
scrapeWebsiteLoop()
