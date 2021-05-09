import re
import time
from datetime import date, datetime, timedelta

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from TwilioHandler import TwilioHandler

class SmithGolfHandler:
    def __init__(self, url: str, preferredTeeTimes, username: str, password: str, twilioHandler: TwilioHandler):
        self.url = url
        self.username = username
        self.password = password
        self.preferredTeeTimes = preferredTeeTimes.split(',')
        self.twilioHandler = twilioHandler

        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(30)
        self.driver.maximize_window()

    def BookSmithTeeTimes(self):
        
        print("Navigating to Smith URL")

        self.driver.get(self.url)

        assert "Fairfield Parks and Recreation Search" in self.driver.title

        today = datetime.now()
        dayInAWeek = today + timedelta(days=7)
        dayInAWeekString = dayInAWeek.strftime('%m/%d/%Y')
        isNextMonth = today.month != dayInAWeek.month

        #self.driver.get_screenshot_as_file('screenshots/smithgolf_mainpage_{}-{}.png'.format(today.strftime('%m.%d.%Y'), timeToRun.replace(':', '-')))

        print("Logging in")

        # Login
        self.driver.find_element_by_xpath("//a[@class='login-link popup-link']").click()
        #self.driver.get_screenshot_as_file('screenshots/smithgolf_LoginEmpty_{}-{}.png'.format(today.strftime('%m.%d.%Y'), timeToRun.replace(':', '-')))
        self.driver.find_element_by_id("weblogin_username").clear()
        self.driver.find_element_by_id("weblogin_username").send_keys(self.username)
        self.driver.find_element_by_id("weblogin_password").clear()
        self.driver.find_element_by_id("weblogin_password").send_keys(self.password)
        #self.driver.get_screenshot_as_file('screenshots/smithgolf_LoginFilled_{}-{}.png'.format(today.strftime('%m.%d.%Y'), timeToRun.replace(':', '-')))
        self.driver.find_element_by_xpath("//input[@id='weblogin_buttonlogin']").click()

        # Homepage - Navigate to Golf
        #self.driver.get_screenshot_as_file('screenshots/smithgolf_HomePageLoggedIn_{}-{}.png'.format(today.strftime('%m.%d.%Y'), timeToRun.replace(':', '-')))
        self.driver.get(self.url)
        #self.driver.get_screenshot_as_file('screenshots/smithgolf_LoggedInGolfTeeTimes_{}-{}.png'.format(today.strftime('%m.%d.%Y'), timeToRun.replace(':', '-')))

        print("Searching tee times")

        # TeeTime settings
        courseDropdownXPath = "//select[@name='secondarycode']/option[text()='H. Smith Richardson Golf Course']"
        numPlayersDropdownXpath = "//select[@name='numberofplayers']/option[text()='4']"
        numHolesDropdownXpath = "//select[@name='numberofholes']/option[text()='18 holes']"
        beginTimeDropdownXPath = "//input[@id='begintime']"
        beginTimeInputXPath = "//div[@id='begintime_root']/div/div/div/div/ul/li[text()='06:00 AM']"
        beginDateDropdownXPath = "//input[@name='begindate']"
        nextMonthXPath = "//div[@title='Next month']"
        beginDateInputXPath = "//div[@id='begindate_root']/div/div/div/div/table/tbody//td/div[@aria-label='{}']".format(dayInAWeekString)
        searchTeeTimesButton = "//input[@name='grwebsearch_buttonsearch']"
        searchTeeTimesTable = "//table[@id='grwebsearch_output_table']"

        self.driver.find_element_by_xpath(courseDropdownXPath).click()
        self.driver.find_element_by_xpath(numPlayersDropdownXpath).click()
        self.driver.find_element_by_xpath(numHolesDropdownXpath).click()
        self.driver.find_element_by_xpath(beginTimeDropdownXPath).click()
        self.driver.find_element_by_xpath(beginTimeInputXPath).click()
        self.driver.find_element_by_xpath(beginDateDropdownXPath).click()
        if(isNextMonth):
            self.driver.find_element_by_xpath(nextMonthXPath).click()
        self.driver.find_element_by_xpath(beginDateInputXPath).click()
        self.driver.find_element_by_xpath(searchTeeTimesButton).click()

        #self.driver.get_screenshot_as_file('screenshots/smithgolf_teetimes_{}-{}.png'.format(today.strftime('%m.%d.%Y'), timeToRun.replace(':', '-')))

        # Getting all available TeeTimes
        teeTimeRows = self.driver.find_element_by_xpath(searchTeeTimesTable).find_elements_by_css_selector('tr')
        teeTimeCells = self.driver.find_element_by_xpath(searchTeeTimesTable).find_elements_by_css_selector('td')

        teeTimesGrouped = [teeTimeCells[n: n + 8] for n in range(0, len(teeTimeCells), 8)]
        teeTimesDict = {teeTimesGrouped[i][1].text : {'AddToCartIndex': str(i), 'IsAddToCartAvailable': str(teeTimesGrouped[i][0].text == 'Add To Cart'), 'Date' : teeTimesGrouped[i][2].text, 'Holes': teeTimesGrouped[i][3].text, 'Course': teeTimesGrouped[i][4].text, 'OpenSlots': teeTimesGrouped[i][5].text } for i in range(len(teeTimesGrouped))}
        #teeTimeRowHeaders = ['AddToCart', 'Time', 'Date', 'Holes', 'Course', 'Open', 'Slots', 'Status']

        print("Searching for available tee times")

        # Booking available tee time in order of preferred times
        for teeTime in self.preferredTeeTimes:
            if (teeTime in teeTimesDict) and (teeTimesDict[teeTime]['IsAddToCartAvailable'] == 'True') and (teeTimesDict[teeTime]['Holes'] == '18 (Front)') and (teeTimesDict[teeTime]['Course'] == 'H. Smith Richardson Golf Course') and (teeTimesDict[teeTime]['OpenSlots'] == '4'):

                print("Trying to book %s tee time", teeTime)

                addToCartElements = self.driver.find_elements_by_xpath("//a[@title='Add To Cart' or @title='Unavailable']")
                # addToCartElements[int(teeTimesDict[teeTime]['AddToCartIndex'])].click()

                #self.driver.get_screenshot_as_file('screenshots/smithgolf_personalinfo_{}-{}.png'.format(today.strftime('%m.%d.%Y'), timeToRun.replace(':', '-')))
                # self.driver.find_element_by_id('golfmemberselection_buttononeclicktofinish').click()

                # Successfully booked Tee Time
                try:
                    time.sleep(5)
                    #self.driver.get_screenshot_as_file('screenshots/smithgolf_submitted_{}-{}.png'.format(today.strftime('%m.%d.%Y'), timeToRun.replace(':', '-')))
                    self.driver.find_element_by_id('webconfirmation_pageheader')
                    print("Booked %s", teeTime)
                    successMessage = "{} {} - booked {} teetime on {} at {} for {} people.".format(today.strftime('%m/%d/%Y'), datetime.now().strftime("%H:%M:%S"), teeTime, teeTimesDict[teeTime]['Date'], teeTimesDict[teeTime]['Course'], teeTimesDict[teeTime]['OpenSlots'])
                    print(successMessage)
                    self.twilioHandler.sendSms(successMessage)
                    print("Sent success SMS")
                    break
                # Failed to book Tee Time, retrying with next preferred time
                except:
                    #self.driver.get_screenshot_as_file('screenshots/smithgolf_failed_{}-{}.png'.format(today.strftime('%m.%d.%Y'), timeToRun.replace(':', '-')))
                    print("Failed to book %s", teeTime)
                    failMessage = "{} {} - FAILED to book {} teetime on {} at {} for {} people. Trying next preferred teetime...".format(today.strftime('%m/%d/%Y'), datetime.now().strftime("%H:%M:%S"), teeTime, teeTimesDict[teeTime]['Date'], teeTimesDict[teeTime]['Course'], teeTimesDict[teeTime]['OpenSlots'])
                    print(failMessage)
                    self.twilioHandler.sendSms(failMessage, True)
                    print("Sent failure SMS; retrying with new tee time")
                    self.driver.back()
                    time.sleep(1)
        
        print("\nQuitting...")
        self.driver.quit()