# Overview
[![CodeFactor](https://www.codefactor.io/repository/github/metacinnabar/noip-auto-renew/badge)](https://www.codefactor.io/repository/github/metacinnabar/noip-auto-renew)
![GitHub repo size](https://img.shields.io/github/repo-size/Metacinnabar/noip-auto-renew)
![GitHub](https://img.shields.io/github/license/Metacinnabar/noip-auto-renew)
![GitHub last commit](https://img.shields.io/github/last-commit/Metacinnabar/noip-auto-renew)
![GitHub release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/Metacinnabar/noip-auto-renew?include_prereleases&sort=semver)

Noip-auto-renew is a simple program to renew free [noip](https://www.noip.com/) hosts before they expire. Schedules a cronjob to renew the host automatically.

Built with Python/Selenium with headless Chromium.

## Usage
Quick note: `username` is used in replacement of the system user you are running this program from.

#### Getting started 
1. Clone the repository  (`git clone https://github.com/Metacinnabar/noip-auto-renew`)
2. Enter the `noip-auto-renew` directory (`cd noip-auto-renew`)
2. Run `setup.sh` and set your noip.com account information. (`./setup.sh`)
3. Run `noip-renew-username`, check results.png (if succeeded) or exception.png (if failed)

For information on how to set up Notifications, please read the Notifications section.

For docker users, check `Dockerfile`, `docker-compose.yml`, and `crontab-docker-host`.

To check script version, use command: ``noip-renew-username --version``

## Notification Setup

<details><summary><strong>Discord</strong></summary>
<p>

1. Sign up on the [Discord website](https://discord.com/login).

2. After creating an account, create a server.

![Create Discord Server](https://user-images.githubusercontent.com/23632287/85154342-3c2d8c80-b24f-11ea-9404-05a24b500dc2.png)

3. Once this is done, right click on server > server settings > webhooks

![Navigate to Webhooks](https://user-images.githubusercontent.com/23632287/85154382-48b1e500-b24f-11ea-9e9b-e7a30c513a15.png)

4. Create a new webhook with a name of choice. Mine is "No-IP Host Monitor" and assign it to a channel.

![Create new Webhook](https://user-images.githubusercontent.com/23632287/85154439-5bc4b500-b24f-11ea-88bc-75c9ce4b88c4.png)

5. Copy the Webhook URL and enter this during setup. 

</p>
</details>

## Future Improvements

- [ ] Improve logging process to allow user to modify log level efficiently 
- [ ] Further tidy the script and improve installation & uninstallation process. Make this more streamline.
- [ ] Change the way the script sets "noip-renew-<strong>user</strong>" to call it. Make it noip-renew --noipaccountname
- [ ] Set up command parameters (`--configure --help --version --uninstall --repair --upgrade --logs`)
