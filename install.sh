#!/bin/bash

set -e 

ENVDIR="/etc/telegram-log-monitor"
DAEMON_DIR="/etc/systemd/system"
WORKDIR="/usr/local/bin/telegram-log-monitor"
USER=0

function showhelp(){
	cat << EOF
Usage: ./$(basename $0) LOGFILE [OPTION] ... 

  --env-path                  path where environment directory will be created. Default is /etc/telegram-log-monitor. 

  --script-dir                directory where to save main script. Default is /usr/local/bin. 

  --user-service              by default, the daemon is global, and is copied in /etc/systemd/system.
                              Add this flag if you wish to make it a user service.

  -h, --help                  show this help

  WARNING: if not present, each path specified with these flags will be created
  LOGFILE must be the first argument passed to this script.

EOF
	exit 0
}

if [[ $# -eq 0 ]];then
	showhelp
fi

if [[ ! -f "$1" ]]; then
	case $1 in
		-h|--help)
			showhelp
			;;
		*)
			echo -e "$1: no such file or directory\n"
			exit 1
			;;
	esac	
fi

LOGFILE="$1"
shift

while [[ "$#" -gt 0 ]]; do
	case "$1" in
		--env-path)
			ENVDIR="$2/telegram-log-monitor/"
			shift 2
			;;
		--script-dir)
			WORKDIR="$2"
			shift 2
			;;
		--user-service)
			DAEMON_DIR="$HOME/.config/systemd/user/"
			mkdir -p $DAEMON_DIR
			USER=1
			shift
			;;
		-h|--help)
			showhelp
			;;
		*)
			echo -e "Unknown option $1\n"
			showhelp
			exit 2
			;;
	esac
done


if [[ ! -d "$WORKDIR" ]]; then
	echo "$WORKDIR: not a directoryi"
	echo "Create it now? [Y/n]"
	read ans 
	if [[ $ans="Y" || $ans="y" ]]; then
		mkdir -p "$WORKDIR"
	else
		exit 3
	fi
fi

# Input bot details
echo "Enter your bot token:"
read -s TOKEN

echo "Enter your chat id:"
read -s CHAT_ID

echo $PWD
cp "$(dirname "$0")"/source/* "$WORKDIR"

# Create environment directory
mkdir -p "$ENVDIR"
ENVFILE="$ENVDIR/env"

if [[ ! -f "$ENVFILE" ]];then
	touch "$ENVFILE"
fi

# Create Environment File
echo "MY_TOKEN=$TOKEN" > "$ENVFILE"
echo "CHAT_ID=$CHAT_ID" >> "$ENVFILE"
echo "LOG_PATH=$LOGFILE" >> "$ENVFILE"

cp "$(dirname "$0")/telegram-log-monitor.service" "$DAEMON_DIR/telegram-log-monitor.service" 

# Change mock daemon with real data
sed -i\
       	-e "s|{{WORKDIR}}|$WORKDIR|g" \
	-e "s|{{ENVFILE}}|$ENVFILE|g" \
	-e "s|{{PYTHON_BIN}}|"$ENVDIR"/.venv/bin/python3|g" \
       	"$DAEMON_DIR/telegram-log-monitor.service"

# Create virtual Environment
python3 -m venv "$ENVDIR"/.venv
"$ENVDIR"/.venv/bin/pip3 install -r "$(dirname "$0")/requirements.txt"

# Start Daemon
if [[ $USER -eq 1 ]];then
	systemctl --user daemon-reload
	systemctl --user start telegram-log-monitor.service || { echo "Error starting service"; exit 4; }
else
	systemctl daemon-reload
	systemctl start telegram-log-monitor.service || { echo "Error starting service"; exit 4; }
fi
