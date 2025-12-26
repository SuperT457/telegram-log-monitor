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

This script is not OS-specific, but in this repository at the moment only provides linux installation guide.

## Install & run
To install the script, you can easily clone the repository and run the `install.sh` script:

```
git clone https://github.com/SuperT457/telegram-log-monitor.git
cd telegram-log-monitor
./install.sh LOGFILE [OPTION] ...
```

To run the installation script you must provide, as CLI argument, the path to the log file you wish to monitor, then you may add some flags to custom your environment of execution. Run `./install.sh -h` for more details.
This script copies the python script to a directory where you it to be executed. Then, after providing needed information via command line o as arguments, it will create an environment of execution and a systemd service that will automatically start. By default, the daemon is a root daemon, working in `/etc/systemd/system`, but you can create a custom user service with the `--user-service` flag, and it'll then be store in `~/.config/systemd/user`.