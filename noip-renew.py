#!/usr/bin/env python3
# Copyright 2017 loblab
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from datetime import date
from datetime import timedelta
import time
import sys
import os
import re
import base64
import subprocess

try:
    from discord_webhook import DiscordWebhook, DiscordEmbed
except ImportError:
    pass

try:
    import requests
except ImportError:
    pass

try:
    from slack import WebClient
    from slack.errors import SlackApiError
except ImportError:
    pass

try:
    import telegram_send
except ImportError:
    pass


class Logger:

    def __init__(self, level):
        self.level = 0 if level is None else level

    def log(self, msg, level=None):
        self.time_string_formatter = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))
        self.level = self.level if level is None else level
        if self.level > 0:
            print(f"[{self.time_string_formatter}] - {msg}")


class Notify:

    APP_TOKEN = ""
    USER_KEY = ""
    SLACK_TOKEN = ""
    CHANNEL = ""
    WEBHOOK_URL = ""

    def __init__(self, notification_type):
        self.notification_type = notification_type
        self.setup(self.notification_type)

    def setup(self, notification_type):
        return { "Discord": self.setupDiscord, "Pushover": self.setupPushover, "Slack": self.setupSlack }.get(self.notification_type.split('|')[0], lambda : 'Invalid')()

    def setupDiscord(self):
        self.WEBHOOK_URL = self.notification_type.split('|', 2)[1]

    def setupPushover(self):
        self.APP_TOKEN = base64.b64decode(self.notification_type.split('|')[1]).decode('utf-8')
        self.USER_KEY = base64.b64decode(self.notification_type.split('|')[2]).decode('utf-8')

    def setupSlack(self):
        self.SLACK_TOKEN = base64.b64decode(self.notification_type.split('|')[1]).decode('utf-8')
        self.CHANNEL = self.notification_type.split('|')[2]

    def pushover(self, msg, img):
        r = requests.post("https://api.pushover.net/1/messages.json", data = {
          "token": self.APP_TOKEN,
          "user": self.USER_KEY,
          "message": msg
        },
        files = {
          "attachment": ("image.png", open(img, "rb"), "image/png")
        })
        del r

    def discord(self, msg, img):
        webhook = DiscordWebhook(url=self.WEBHOOK_URL, content=msg)
        with open(img, "rb") as f:
            webhook.add_file(file=f.read(), filename=img)
        response = webhook.execute()
        print("Webhook response: " + str(response))

    def slack(self, msg, img):
        client = WebClient(token=self.SLACK_TOKEN)
        try:
            client.chat_postMessage(
                channel=self.CHANNEL,
                text=msg
            )
            client.files_upload(
                channels=self.CHANNEL,
                file=img,
                title=img,
            )
        except SlackApiError as e:
            assert e.response["error"]

    def telegram(self, msg, img):
        with open(img, "rb") as f:
            telegram_send.send(captions=[msg], images=[f])

    def send(self, message, image):
        if self.notification_type.split('|')[0] == "Discord":
            self.discord(message, image)
        elif self.notification_type.split('|')[0] == "Pushover":
            self.pushover(message, image)
        elif self.notification_type.split('|')[0] == "Slack":
            self.slack(message, image)
        elif self.notification_type.split('|')[0] == "Telegram":
            self.telegram(message, image)
        elif self.notification_type.split('|')[0] == "None":
            return
        else:
            raise Exception("Something went wrong with notifications. Try to reinstall the script.")


class Robot:

    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:64.0) Gecko/20100101 Firefox/64.0"
    LOGIN_URL = "https://www.noip.com/login"
    HOST_URL = "https://my.noip.com/#!/dynamic-dns"

    def __init__(self, username, password, notification_type, debug):
        self.debug = debug
        self.username = username
        self.password = password
        self.browser = self.init_browser()
        self.logger = Logger(debug)
        self.notification = Notify(notification_type)

    @staticmethod
    def init_browser():
        options = webdriver.ChromeOptions()
        #added for Raspbian Buster 4.0+ versions. Check https://www.raspberrypi.org/forums/viewtopic.php?t=258019 for reference.
        options.add_argument("disable-features=VizDisplayCompositor")
        options.add_argument("headless")
        options.add_argument("no-sandbox")  # need when run in docker
        options.add_argument("window-size=1200x800")
        options.add_argument(f"user-agent={Robot.USER_AGENT}")
        if 'https_proxy' in os.environ:
            options.add_argument("proxy-server=" + os.environ['https_proxy'])
        browser = webdriver.Chrome(options=options)
        browser.set_page_load_timeout(90) # Extended timeout for Raspberry Pi.
        return browser

    def login(self):
        self.logger.log(f"Opening {Robot.LOGIN_URL}...")
        self.browser.get(Robot.LOGIN_URL)
        if self.debug > 1:
            self.browser.save_screenshot("debug1.png")

        self.logger.log("Logging in...")
        ele_usr = self.browser.find_element_by_name("username")
        ele_pwd = self.browser.find_element_by_name("password")
        ele_usr.send_keys(self.username)
        ele_pwd.send_keys(base64.b64decode(self.password).decode('utf-8'))
        self.browser.find_element_by_id("clogs-captcha-button").click()
        if self.debug > 1:
            time.sleep(1)
            self.browser.save_screenshot("debug2.png")

    def update_hosts(self):
        count = 0

        self.open_hosts_page()
        time.sleep(1)
        iteration = 1
        next_renewal = []

        hosts = self.get_hosts()
        for host in hosts:
            host_link = self.get_host_link(host, iteration) # This is for if we wanted to modify our Host IP.
            host_button = self.get_host_button(host, iteration) # This is the button to confirm our free host
            host_name = host_link.text
            expiration_days = self.get_host_expiration_days(host, iteration)
            next_renewal.append(expiration_days)
            self.logger.log(f"{host_name} expires in {str(expiration_days)} days")
            if expiration_days < 7:
                self.update_host(host_button, host_name)
                count += 1
            iteration += 1
        self.browser.save_screenshot("results.png") # Image of host page listing all active hosts.
        self.logger.log(f"Confirmed hosts: {count}", 2)
        nr = min(next_renewal) - 6
        today = date.today() + timedelta(days=nr)
        day = str(today.day)
        month = str(today.month)
        self.notification.send(f"No-IP Renew ran successfully. The next host update is in {str(nr)} days", "results.png")
        subprocess.call(['/usr/local/bin/noip-renew-skd.sh', day, month, "True"])
        return True

    def open_hosts_page(self):
        self.logger.log(f"Opening {Robot.HOST_URL}...")
        try:
            self.browser.get(Robot.HOST_URL)
        except TimeoutException as e:
            self.browser.save_screenshot("timeout.png")
            self.logger.log(f"Timeout: {str(e)}")
            self.notification.send(f"Timeout: {str(e)}", "timeout.png")

    def update_host(self, host_button, host_name):
        self.logger.log(f"Updating {host_name}")
        host_button.click()
        time.sleep(3)
        
        try:
            if self.browser.find_elements_by_xpath("//h2[@class='big']")[0].text == "Upgrade Now":
                raise Exception("Manual intervention required. Upgrade text detected.")
        except (NoSuchElementException):
            self.logger.log("Manual intervention not required. Proceeding.")
            pass

        self.browser.save_screenshot(f"{host_name}_success.png")
        self.notification.send(f"{host_name} updated successfully", f"{host_name}_success.png")

    @staticmethod
    def get_host_expiration_days(host, iteration):
        try:
            host_remaining_days = host.find_element_by_xpath(".//a[@class='no-link-style']").text
        except (NoSuchElementException):
            host_remaining_days = "Expires in 0 days"
            pass
        regex_match = re.search("\\d+", host_remaining_days)
        if regex_match is None:
            raise Exception("Expiration days label does not match the expected pattern in iteration: {iteration}")
        expiration_days = int(regex_match.group(0))
        return expiration_days

    @staticmethod
    def get_host_link(host, iteration):
        return host.find_element_by_xpath(".//a[@class='link-info cursor-pointer']")

    @staticmethod
    def get_host_button(host, iteration):
        return host.find_element_by_xpath(".//following-sibling::td[4]/button[contains(@class, 'btn')]")

    def get_hosts(self):
        host_tds = self.browser.find_elements_by_xpath("//td[@data-title='Host']")
        if len(host_tds) == 0:
            raise Exception("No hosts or host table rows not found")
        return host_tds

    def run(self):
        rc = 0
        self.logger.log(f"Debug level: {self.debug}")
        try:
            self.login()
            if not self.update_hosts():
                rc = 3
        except Exception as e:
            self.logger.log(str(e))
            self.browser.save_screenshot("exception.png")
            self.notification.send(f"An error has occured: {str(e)}", "exception.png")
            subprocess.call(['/usr/local/bin/noip-renew-skd.sh', "0", "0", "False"])
            rc = 2
        finally:
            self.browser.quit()
        return rc


def main(argv=None):
    noip_username, noip_password, notification_type, debug = get_args_values(argv)
    return (Robot(noip_username, noip_password, notification_type, debug)).run()


def get_args_values(argv):
    if argv is None:
        argv = sys.argv
    if len(argv) < 4:
        print(f"Usage: {argv[0]} <noip_username> <noip_password> <notification_type> [<debug-level>]")
        sys.exit(1)

    noip_username = argv[1]
    noip_password = argv[2]
    notification_type = argv[3]
    debug = 1
    if len(argv) > 4:
        debug = int(argv[4])
    return noip_username, noip_password, notification_type, debug


if __name__ == "__main__":
    sys.exit(main())
