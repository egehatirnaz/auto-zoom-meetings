from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import selenium.common.exceptions
import time, datetime, platform
import getpass

current_os = platform.system()


def launch_browser():
    browser_options = webdriver.ChromeOptions()
    browser_options.add_argument('disable-infobars')
    browser_options.add_argument("disable-notifications")

    prefs = {
        "protocol_handler": {"excluded_schemes,*": {"zoommtg": False}},
        "download_restrictions": 3
        }  # Downloads are blokced but Zoom still tries to open the desktop app. Todo: take a look later.
    browser_options.add_experimental_option("prefs", prefs)
    if current_os == "Windows":
        os_specific_driver = "_win.exe"
    elif current_os == "Darwin":
        os_specific_driver = "_macos"
    else:
        os_specific_driver = "_linux"
    browser = webdriver.Chrome(executable_path="ChromeDrivers/chromedriver" + os_specific_driver, options=browser_options)
    browser.get('https://zoom.us/')
    return browser


def main():
    print("Zoom Email:")
    user_email = input()
    user_password = getpass.getpass()
    print("Getting courses...")
    courses = get_courses("courses.txt")  # [[course1, 15:40], [course2, 08:40]]
    print("Done!")
    print("Please wait. You will be logged in automatically when the time comes. Do not close this window. [Press CTRL + C to terminate!]")
    while True:
        all_done = True
        for course in courses:
            all_done = True
            if not course[3]:  # Not marked as done yet.
                all_done = False
                if not course_timer(course[1], course[2]):  # it's not this course's time yet.
                    continue
                else:   # it's showtime!
                    zoom_automate(course[0], user_email, user_password, course[1] + 2, course[2] - 10)  # 2 x 50 min, 1 x 10 min
                    course[3] = True  # Mark course as done.
            else:   # This course has been attended.
                continue
        if all_done:
            break
        time.sleep(30)
    exit(0)


def zoom_automate(zoom_id, user_email, user_password, term_hour, term_minute):
    browser = launch_browser()
    try:
        browser.find_element_by_xpath('//*[@id="navbar"]/ul[2]/li[5]/a')
        # User has not logged in yet.
        logged_in = False
    except selenium.common.exceptions.NoSuchElementException:
        logged_in = True  # User has logged in.

    if not logged_in:
        sign_in(browser, user_email, user_password)
    else:
        print("you are already logged in.")
    wait = WebDriverWait(browser, 10)
    wait.until(EC.url_changes('https://zoom.us/signin'))
    join_meeting(browser, zoom_id)

    while not course_timer(term_hour, term_minute):
        time.sleep(60)
    # Exit buttons
    try:
        browser.find_element_by_xpath('//*[@id="wc-footer"]/div[3]/button').click()  # Are you sure button
        browser.find_element_by_xpath('/html/body/div[11]/div/div/div/div[2]/div/div/button').click()  # Yes button.
    except Exception as e:
        print(e)
        print("Couldn't exit gracefully.")
    time.sleep(200)
    browser.quit()


def sign_in(browser, user_email, user_password):
    browser.get('https://zoom.us/signin')
    browser.find_elements_by_xpath('//*[@id="email"]')[0].send_keys(user_email)
    browser.find_elements_by_xpath('//*[@id="password"]')[0].send_keys(user_password)
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
    except Exception:
        try:
            browser.find_element_by_xpath('//*[@id="launch_meeting"]/div/div[4]/a').click()
        except Exception:
            print("Couldn't find the WC link. Moving on.")

    zoom_root_url = browser.current_url.split("//")[-1].split("/")[0]
    destination_url = zoom_root_url + "/wc/join/" + meeting_number + "?pwd="
    browser.get("https://" + destination_url)
    browser.maximize_window()
    try:
        browser.find_element_by_xpath('//*[@id="joinBtn"]').click()
    except Exception as e:
        print("Could not click on button. Moving on.")
        print(e)
    time.sleep(3)
    try:
        browser.find_element_by_xpath('//*[@id="dialog-join"]/div[4]/div/div/div[1]/button').click()
    except Exception as e:
        print("Could not click on button. Moving on.")
        print(e)


def course_timer(hour, minute):
    if hour > 23 or hour < 0:
        hour %= 24
    if minute > 59 or minute < 0:
        minute %= 60

    now = datetime.datetime.now()
    course_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if now >= course_time:
        return True
    return False


def get_courses(path):
    wrapper = []
    try:
        fp = open('courses.txt', 'r')
        courses = fp.readlines()
        for course in courses:
            list = course.split("/")
            zoom_id = list[0].strip().replace("-", "")
            course_time = list[1].strip().split(":")
            wrapper.append([zoom_id, int(course_time[0]), int(course_time[1]), False])
    finally:
        fp.close()
    return wrapper


if __name__ == '__main__':
    main()
