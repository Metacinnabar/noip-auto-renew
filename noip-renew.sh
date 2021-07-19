#!/bin/bash

# Check for Version request
VERSION="1.2"

if [ "$1" = "--version" ] ; then
    echo Version $VERSION
    return 0
fi

# No-IP Account
USERNAME=""
PASSWORD=""

LOGDIR=$1
PROGDIR=$(dirname -- $0)

# Notification Method
NOTIFICATION=""

# Discord
DISCORD_WEBHOOK=""

# Pushover
PUSHOVER_TOKEN=""
PUSHOVER_USER_KEY=""

# Slack
SLACK_TOKEN=""
CHANNEL=""

if [ ! -z "$NOTIFICATION" ]; then
    NPARMS=""
    case $NOTIFICATION in
        "Discord") NPARMS="|${DISCORD_WEBHOOK}";;
        "Pushover") NPARMS="|${PUSHOVER_TOKEN}|${PUSHOVER_USER_KEY}";;
        "Slack") NPARMS="|${SLACK_TOKEN}|${CHANNEL}";;
        "Telegram") NPARMS="";;
        *) echo "An error occured.";;
    esac
    NOTIFY="${NOTIFICATION}${NPARMS}"
else
    NOTIFY="None"
fi

if [ -z "$LOGDIR" ]; then
    $PROGDIR/noip-renew.py "$USERNAME" "$PASSWORD" "$NOTIFY" 2
else
    cd $LOGDIR
    $PROGDIR/noip-renew.py "$USERNAME" "$PASSWORD" "$NOTIFY" 0 >> $USERNAME.log
fi
