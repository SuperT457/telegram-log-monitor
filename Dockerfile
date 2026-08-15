FROM python:3.13-slim

# Install dotenvx
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://dotenvx.sh/install.sh | sh

WORKDIR /usr/local/app/

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY source/ .

# create necessary files and directories
RUN mkdir -p /var/log/accesses/ && touch /var/log/telegram-log-monitor.log

CMD ["dotenvx", "run", "--", "python3", "telegram-log-monitor.py"]
