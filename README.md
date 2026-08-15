# Telegram Log Monitor Bot

This is a lightweight, event-driven Python tool that monitors Caddy JSON logs in real time and alerts the user via Telegram Bot APIs.
Every time new lines are added to the log file, it parses the logs retrieving critical data, such as IP address, URIs accessed and return status code. It then enriches IP details with geographical information (city and region) using ipinfo.io APIs.

---

## Key Features
- **Event-Driven:** the script uses the `watchdog` library to detect file changes, avoiding polling and improving performance;
- **Efficient Log Reading:** every time a new access is detected only new lines are parsed, using `tell()` and `seek()` functions, for a more efficient reading;
- **Noise Reduction:** to reduce notification volume, the script filters only for specific URIs, considered more critical;
- **IP Geolocation and Caching:** for a new IP, geographical information is retrieved using `ipinfo.io` APIs, while those already checked are stored in a cache, implemented with a dictionary, to minimize API calls;
- **Batch Notifications:** at the end of the loop, Telegram Bot APIs are used to alert the user with a message aggregating all the latest accesses;
- **Logging:** this script generates logs for information and errors. If the user has sufficient privileges, the output log file will be automatically created in `/var/log/telegram-log-monitor.log`, otherwise it'll be stored in `~/.local/share/telegram-log-monitor.log`. 

---

## Requirements
- Caddy Web Server with JSON logging enabled;
- Docker and Docker Compose;
- Telegram Bot Token and Chat ID;

---

## Install & run
The application now runs inside a Docker container; the directory containing Caddy logs is mounted to the container in read-only mode. 

### 1. Configuration
Populate the required environment files: the root `.env` defines the host directory path for the read-only bind mount, while the `source/.env` contains application secrets (Bot Token, Chat ID, logfile name). The root `.env` file is already provided and can be edited with your values. 
For the application secrets in `source/`, two files are provided: `source/.env.example` is an example template showing the required variables, and `source/.env` is the ready-to-use, actual environment file after the `dotenvx` encryption. 

Optionally, you can encrypt the sensitive variables of the `source/.env` file using `dotenvx`
```bash
dotenvx encrypt -f ./source/.env
```
Please note that the generated `.env.keys` file must remain in the project root, so that Docker Compose is able to inject the decryption key in the container at runtime. 

### 2. Run the Service
Start the container in detached mode:
```bash
docker compose up -d
```

To view application logs:
```bash
docker compose logs -f
``` 

To stop the service:
```bash
docker compose down
```

### Security Notes
`dotenvx` only encrypts secrets "at rest", for source control security, allowing `.env` files to be committed securely to public repositories. However, in-container environments inherit the decryption key at runtime, meaning anyone with sufficient privileges on the host (or `docker exec` access) can inspect it. 

## Latest upgrades 
- Docker containerization and `dotenvx` encryption support;
