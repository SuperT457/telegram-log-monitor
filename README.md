# Telegram Log Monitor Bot

This is a Python event-driven script that monitors caddy JSON logs in real time and aletrs user via Telegram Bot APIs.
Every time new lines are added to the log file, it parse the logs retrieving critical data, such as IP address, URIs accessed and return status code. It then enriches IP details with geographical information (city and region) using ipinfo.io APIs.

## Main functionalities
- The script uses `watchdog` module to detect file changes (event-driven) to avoid poolling and improve performance;
- Every time a new access is detected only new lines are parsed, using `tell()` and `seek()` functions, for a more efficient reading;
- To reduce notifcation quantity and noise, the script filter only for specific URIs, considered more critical;
- For a new IP, geographical information are retrieved using ipinfo.io APIs, while those already checked are stored in a cache, implemented with a dictionary;
- At the end of the loop, telegram APIs are used to alert the user with a message containg all the recent accesses;

## Requirements
- python 3.10+

The python modules to be installed are in the `requirements.txt` file and can be installed with:
```
pip3 install -r requirements.txt`
```

It is also possibile that you'll need to create a virtual environment in order to install the requirements. This can be done with:
```
python3 -m venv .venv
```

And then:
```
source /path/to/.venv/bin/activate
```
Before installing the needed modules.

This script is not OS-specific, but in this repository at the moment only provides linux systemd service for automation.

## Install & run
The quickest way to start this script is by copying the `telegram-monitor.service` to the systemd directory and run the service. 
You can do it in your home directory:
```
cp telegram-monitor.service ~/.config/systemd/system/
systemctl --user start telegram-monitor.service
```
Or, if you need root privileges: 
```
sudo cp telegram-monitor.service /etc/systemd/system/
sudo systemctl start telegram-monitor.service
```

In bot cases you'll need to edit the unit file with your personal paths where you script and log file are.