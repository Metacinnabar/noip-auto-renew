# Script to auto renew/confirm noip.com free hosts

[noip.com](https://www.noip.com/) free hosts expire every month.
This script auto clicks web pages to renew the hosts,
using Python/Selenium with Chrome headless mode.

- Platform: Debian/Ubuntu/Raspbian Linux, no GUI needed (tested on Debian 9.x/10.x); python 3.6+
- Ver: 1.2
- Ref: [Technical explanation for the code (Chinese)](http://www.jianshu.com/p/3c8196175147)
- Updated: 06/11/2020
- Created: 11/04/2017
- Author: loblab
- Contributor: [IDemixI](https://www.github.com/IDemixI)

![noip.com hosts](https://raw.githubusercontent.com/loblab/noip-renew/master/screenshot.png)

## Usage

1. Clone this repository to the device you will be running it from. (`git clone https://github.com/loblab/noip-renew.git`)
2. Run setup.sh and set your noip.com account information.
3. Run `noip-renew-username`, check results.png (if succeeded) or exception.png (if failed)

For information on how to set up Notifications, please read the Notifications section.

For docker users, check Dockerfile, docker-compose.yml, crontab-docker-host.

Check confirmed records from multiple log files:

``` bash
grep -h Confirmed *.log | grep -v ": 0" | sort
```

To check script version, use command: ``noip-renew-username --version``

## Remarks

The script is not designed to renew/update the dynamic DNS records, though the latest version does have this ability if requested.
Check [noip.com documentation](https://www.noip.com/integrate) for that purpose.
Most wireless routers support noip.com. For more information, check [here](https://www.noip.com/support/knowledgebase/what-devices-support-no-ips-dynamic-dns-update-service/).
You can also check [DNS-O-Matic](https://dnsomatic.com/) to update multiple noip.com DNS records.


## Notification Setup

### Pushover:

1. Create an account over at https://pushover.net/signup.
2. After signing up and confirming your account, you should see a User Key. This is required during setup.
![2020-06-18_21-07-59](https://user-images.githubusercontent.com/23632287/85068139-d0451880-b1a9-11ea-89f1-ab0daf8a3921.png)
3. Create a [new application/API Token](https://pushover.net/apps/build). I've named mine "No-IP Host Monitor".
![2020-06-18_21-12-05](https://user-images.githubusercontent.com/23632287/85068447-51041480-b1aa-11ea-8d30-6650488502ef.png)
4. Once you've created your new App, you will see an API Token/Key. This is also required during setup.
![2020-06-18_21-13-27](https://user-images.githubusercontent.com/23632287/85068512-71cc6a00-b1aa-11ea-86d1-f360ad08ce2f.png)
5. Make sure you have the Pushover Application installed on your [device of choice](https://pushover.net/clients).
6. When running setup.sh, insert your pushover details when prompted.

### Slack:

1. Create an account over at https://slack.com/get-started#/create and set up your Team.
2. Once you're all set up, you will need to [create a new app](https://api.slack.com/apps)
![2020-06-18_21-03-42](https://user-images.githubusercontent.com/23632287/85068598-9b859100-b1aa-11ea-9a87-4df4388f0309.png)
3. The next step is to set up the correct permissions so that we can send a message with an image to Slack.
![2020-06-18_22-09-18](https://user-images.githubusercontent.com/23632287/85078604-ad702f80-b1bc-11ea-887b-24dc445fbc98.png)
4. The required scopes are chat:write & files:write. These can be added by clicking "Add an OAuth Scope"
![2020-06-18_23-24-42](https://user-images.githubusercontent.com/23632287/85078653-ca0c6780-b1bc-11ea-825f-ee9e28c2fb70.png) 
5. Once the scopes have been added, make sure you Reinstall App to reflect these changes.
![2020-06-18_23-27-01](https://user-images.githubusercontent.com/23632287/85078735-fe802380-b1bc-11ea-8a01-4d6f59e9df0a.png)
6. Make a note of your Bot User OAuth Access Token as this is used during setup.
![2020-06-18_22-13-17](https://user-images.githubusercontent.com/23632287/85078760-0c35a900-b1bd-11ea-9c67-e1f39bfe3073.png)
7. Now you must make sure that you add the bot to your channel of choice. This channel will be used during setup.
![2020-06-18_22-44-39](https://user-images.githubusercontent.com/23632287/85078811-2ff8ef00-b1bd-11ea-9543-cf616bfc56b2.png)
8. Install the script, entering your Access Token and Channel when prompted.


### Telegram:


## History
- 1.2 (06/11/2020): Added Notification support for Pushover, Slack & Telegram. 
- 1.1 (06/05/2020): Fixed error when attempting to update an expired host.
- 1.0 (05/18/2020): Minor fixes to an xpath & a try catch pass to avoid an exception. Also fixed versioning.
- 1.0 (04/16/2020): Catches "Would you like to upgrade?" page & stops script accordingly. Manual intervention still required.
- 0.9 (04/13/2020): Complete refactor of code, more stability & automatic crontab scheduling.
- 0.8 (03/23/2020): Added menu to repair/install/remove script along with ability to update noip.com details.
- 0.7 (03/21/2020): Code tidyup and improved efficiency (Removed number of hosts and automatically get this)
- 0.6 (03/15/2020): Improved support for Raspberry Pi (Raspbian Buster) & Changes to setup script.
- 0.5 (01/05/2020): Support raspberry pi, try different "chromedriver" packages in setup script.
- 0.4 (01/14/2019): Add num_hosts argument, change for button renaming; support user agent.
- 0.3 (05/19/2018): Support Docker, ignore timeout, support proxy, tested on python3.
- 0.2 (11/12/2017): Deploy the script as normal user only. root user with 'no-sandbox' option is not safe for Chrome.
- 0.1 (11/05/2017): Support Debian with Chrome headless.
