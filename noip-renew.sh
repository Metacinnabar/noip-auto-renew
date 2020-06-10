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

# Pushover
PUSHOVER_TOKEN=""
PUSHOVER_USER_KEY=""

# Slack
SLACK_TOKEN=""

if [ ! -z "$NOTIFICATION" ]; then
    NPARMS=""
    case $NOTIFICATION in
        "Pushover") NPARMS="|${PUSHOVER_TOKEN}|${PUSHOVER_USER_KEY}";;
        "Slack") NPARMS="|${SLACK_TOKEN}";;
        *) echo "An error occured.";;
    esac
    NOTIFICATION="${NOTIFICATION}${NPARMS}"
fi

if [ -z "$LOGDIR" ]; then
    $PROGDIR/noip-renew.py "$USERNAME" "$PASSWORD" 2 "$NOTIFICATION"
else
    cd $LOGDIR
    $PROGDIR/noip-renew.py "$USERNAME" "$PASSWORD" 0 "$NOTIFICATION" >> $USERNAME.log
fi
