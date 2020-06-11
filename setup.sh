#!/bin/bash
set -e

PYTHON=python3
USER=$(whoami)
if [ "$USER" == "root" ]; then
    USER=$1
    if [ -z "$USER" ]; then
        echo "Chrome is safer to run as normal user instead of 'root', so"
        echo "run the script as a normal user (with sudo permission), "
        echo "or specify the user: $0 <user>"
        exit 1
    fi
    HOME=/home/$USER
else
    SUDO=sudo
fi


function config() {
    LOGDIR=/var/log/noip-renew/$USER
    INSTDIR=/usr/local/bin
    INSTEXE=$INSTDIR/noip-renew-$USER
    CRONJOB="30 0    * * *   $USER    $INSTEXE $LOGDIR"
}


function install() {
    echo "Installing necessary packages..."
    read -p 'Perform apt-get update? (y/n): ' update
    if [ "${update^^}" = "Y" ]
    then
      $SUDO apt-get update
    fi

    $SUDO apt -y install chromium-chromedriver || \
      $SUDO apt -y install chromium-driver || \
      $SUDO apt -y install chromedriver


    PYV=`python3 -c "import sys;t='{v[0]}{v[1]}'.format(v=list(sys.version_info[:2]));sys.stdout.write(t)";`
    if [[ "$PYV" -lt "36" ]] || ! hash python3;
    then
      echo "This script requires Python version 3.6 or higher. Attempting to install..."
      $SUDO apt-get -y install python3
    fi

    # Debian9 package 'python-selenium' does not work with chromedriver,
    # Install from pip, which is newer
    $SUDO apt -y install chromium-browser # Update Chromium Browser or script won't work.
    $SUDO apt -y install $PYTHON-pip
    $SUDO $PYTHON -m pip install selenium
    read -p 'Set up Notifications? (y/n): ' notify
    if [ "${notify^^}" = "Y" ]
    then
      notificationInstall
    fi
}


function deploy() {
    echo "Deploying the script..."

    # Remove current installation first.
    if ls $INSTDIR/*noip-renew* 1> /dev/null 2>&1; then
        $SUDO rm $INSTDIR/*noip-renew*
    fi

    $SUDO mkdir -p $LOGDIR
    $SUDO chown $USER $LOGDIR
    $SUDO cp noip-renew.py $INSTDIR
    $SUDO cp noip-renew-skd.sh $INSTDIR
    $SUDO cp noip-renew.sh $INSTEXE
    $SUDO chown $USER $INSTEXE
    $SUDO chown $USER $INSTDIR/noip-renew-skd.sh
    $SUDO chmod 700 $INSTEXE
    noip
    if [ "${notify^^}" = "Y" ]
    then
      notificationSetup "$notification" # This calls notification setup with the selected notification type.
    fi
    $SUDO sed -i '/noip-renew/d' /etc/crontab
    echo "$CRONJOB" | $SUDO tee -a /etc/crontab
    $SUDO sed -i 's/USER=/USER='$USER'/1' $INSTDIR/noip-renew-skd.sh
    echo "Installation Complete."
    echo "To change noip.com account details, please run setup.sh again."
    echo "Logs can be found in '$LOGDIR'"
}


function noip() {
    echo "Enter your No-IP Account details..."
    read -p 'Username: ' uservar
    read -sp 'Password: ' passvar

    passvar=`echo -n $passvar | base64`
    echo

    $SUDO sed -i 's/USERNAME=".*"/USERNAME="'$uservar'"/1' $INSTEXE
    $SUDO sed -i 's/PASSWORD=".*"/PASSWORD="'$passvar'"/1' $INSTEXE
}


function installer() {
    config
    install
    deploy
}


function uninstall() {
    $SUDO sed -i '/noip-renew/d' /etc/crontab
    $SUDO rm $INSTDIR/*noip-renew*
    read -p 'Do you want to remove all log files? (y/n): ' clearLogs
    if [ "${clearLogs^^}" = "Y" ]
    then
      $SUDO rm -rf $LOGDIR
    fi
}


function notificationInstall() {
    PS3='Select an option: '
    options=("Pushover Notifications" "Slack Notifications" "Telegram Notifications" "None")
    select opt in "${options[@]}"
    do
        case $opt in
            "Pushover Notifications")
                notification="Pushover"
                echo "Pushover requirements installed..."
                break
                ;;
            "Slack Notifications")
                notification="Slack"
                $SUDO $PYTHON -m pip install slackclient
                echo "Slack requirements installed..."
                break
                ;;
            "Telegram Notifications")
                notification="Telegram"
                $SUDO $PYTHON -m pip install telegram-send
                echo "Telegram requirements installed..."
                break
                ;;
            "None")
                notify="N"
                break
                ;;
            *) echo "invalid option $REPLY";;
        esac
    done
}


function notificationSetup() {
    $SUDO sed -i 's/NOTIFICATION=".*"/NOTIFICATION="'$1'"/1' $INSTEXE

    case $1 in
        "Pushover") pushover;;
        "Slack") slack;;
        "Telegram") telegram;;
    esac
}


function pushover() {
    echo "Enter your Pushover Token..."
    read -p 'Token: ' tokenvar

    tokenvar=`echo -n $tokenvar | base64`

    $SUDO sed -i 's/PUSHOVER_TOKEN=".*"/PUSHOVER_TOKEN="'$tokenvar'"/1' $INSTEXE

    echo "Enter your Pushover User Key..."
    read -p 'User: ' uservar

    tokenvar=`echo -n $uservar | base64`

    $SUDO sed -i 's/PUSHOVER_USER_KEY=".*"/PUSHOVER_USER_KEY="'$uservar'"/1' $INSTEXE
}


function slack() {
    echo "Enter your Slack Bot User OAuth Access Token..."
    read -p 'Token: ' tokenvar

    tokenvar=`echo -n $tokenvar | base64`

    $SUDO sed -i 's/SLACKTOKEN=".*"/SLACKTOKEN="'$tokenvar'"/1' $INSTEXE
}


function telegram() {
    echo "Please configure Telegram:"
    $SUDO telegram-send --configure
}


PS3='Select an option: '
options=("Install/Repair Script" "Update noip.com account details" "Uninstall Script" "Exit setup.sh")
echo "No-IP Auto Renewal Script Setup."
select opt in "${options[@]}"
do
    case $opt in
        "Install/Repair Script")
            installer
            break
            ;;
        "Update noip.com account details")
            config
            noip
            echo "noip.com account settings updated."
            break
            ;;
        "Uninstall Script")
            config
            if ls $INSTDIR/*noip-renew* 1> /dev/null 2>&1; then
                uninstall
                echo "Script successfully uninstalled."
            else
                echo "Script is not installed."
            fi
            break
            ;;
        "Exit setup.sh")
            break
            ;;
        *) echo "invalid option $REPLY";;
    esac
done
