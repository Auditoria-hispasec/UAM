import sys
import time

import jwt
import requests
from selenium import webdriver

from config import COOKIE_NAME, URL_BASE, URL_REPORTS, JWT_KEY

COUNT = 0


def get_admin_token():
    # generate a jwt token with an expiration time of 1 minute
    payload = {
        'exp': time.time() + 60,
        'username': 'admin'
    }
    token = jwt.encode(payload, JWT_KEY, algorithm='HS256')
    return token

    

def get_reports():
    try:
        cookies = {COOKIE_NAME: COOKIE_VALUE}
        reports = requests.get(URL_REPORTS, cookies=cookies).json()
        return reports
    except:
        return []



def launch_browser(url):
    global COUNT

    print("opening url {}".format(url))
    COUNT += 1
    try:
        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')

        driver = webdriver.Chrome(options=options) 

        driver.get(URL_BASE)
        time.sleep(1)
        driver.delete_all_cookies()
        cookie = {"name": COOKIE_NAME, "value": COOKIE_VALUE, "httpOnly": True, 'sameSite': 'Lax'}
        driver.add_cookie(cookie)

        driver.get(url)

        time.sleep(10)
    except Exception as ex:
        print(ex)

    try:
        driver.close()
        driver.quit()
    except:
        pass


print("Backend started... checking reported urls...")
while True:
    if COUNT>10:
        os._exit(0)
        break
    COUNT+=1

    COOKIE_VALUE = get_admin_token()
    reports = get_reports()

    if reports:
        print("Received new reports", reports)

    sys.stdout.flush()

    for report in reports:
        url = URL_REPORTS + "/" + report
        launch_browser(url)

    time.sleep(5)
