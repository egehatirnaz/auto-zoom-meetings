from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import selenium.common.exceptions
from credentials import USER_EMAIL, USER_PASSWORD
import time


def launch_browser():
    browser = webdriver.Chrome(executable_path="chromedriver.exe")
    browser.get('https://zoom.us/')
    return browser


def main():
    browser = launch_browser()
    try:
        browser.find_element_by_xpath('//*[@id="navbar"]/ul[2]/li[5]/a')
        # User has not logged in yet.
        logged_in = False
    except selenium.common.exceptions.NoSuchElementException:
        logged_in = True  # User has logged in.

    if not logged_in:
        sign_in(browser)

    else:
        print("you are already logged in.")
    wait = WebDriverWait(browser, 10)
    wait.until(EC.url_changes('https://zoom.us/signin'))
    join_meeting(browser, "4949764796")

    input()


def sign_in(browser):
    browser.get('https://zoom.us/signin')
    browser.find_elements_by_xpath('//*[@id="email"]')[0].send_keys(USER_EMAIL)
    browser.find_elements_by_xpath('//*[@id="password"]')[0].send_keys(USER_PASSWORD)
    browser.find_elements_by_xpath('//*[@id="login-form"]/div[3]/div/div[1]/a')[0].click()


def join_meeting(browser, meeting_number):
    logged_join_button = browser.find_element_by_xpath('//*[@id="btnJoinMeeting"]')
    logged_join_button.click()
    browser.find_element_by_xpath('//*[@id="join-confno"]').send_keys(str(meeting_number[0:3]))
    browser.implicitly_wait(3)  # seconds
    browser.find_element_by_xpath('//*[@id="join-confno"]').send_keys(str(meeting_number[3:6]))
    browser.implicitly_wait(3)  # seconds
    browser.find_element_by_xpath('//*[@id="join-confno"]').send_keys(str(meeting_number[6:]))
    browser.find_element_by_xpath('//*[@id="btnSubmit"]').click()
    time.sleep(2)
    try:
        browser.find_element_by_xpath('//*[@id="action_container"]/div[3]/a').click()
    except selenium.common.exceptions.NoSuchElementException:
        try:
            browser.find_element_by_xpath('//*[@id="launch_meeting"]/div/div[4]/a').click()
        except selenium.common.exceptions.NoSuchElementException:
            print("Couldn't find the WC link.")
    time.sleep(2)

    zoom_root_url = browser.current_url.split("//")[-1].split("/")[0]
    print(zoom_root_url)
    destination_url = zoom_root_url + "/wc/join/" + meeting_number + "?pwd="
    print(destination_url)
    browser.get("https://" + destination_url)


if __name__ == '__main__':
    main()
