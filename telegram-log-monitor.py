import json
import os
from collections import defaultdict
from telegram import Bot # v22.5 
import asyncio
import aiohttp
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

# bot parameters
TELEGRAM_BOT_TOKEN = os.getenv("MY_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# monitored logs path 
LOG_PATH = os.getenv("LOG_PATH")
LOG_DIR = os.path.dirname(LOG_PATH)

# script's output logger
logger = logging.getLogger(__name__)

last_pos = 0
ip_cache = {}

watched_uris = [
        '/',
        '/api/config',
        '/identity/connect/token',
        '/api/sync'
]

class LogHandler(FileSystemEventHandler):
    def __init__(self, loop, queue):
        self.loop = loop
        self.queue = queue

    def on_modified(self,event):
        if event.src_path == LOG_PATH:
            self.loop.call_soon_threadsafe(
                self.queue.put_nowait,
                None
            )

# bot send message
async def send_message(text, chat_id):
    try:
        async with bot:
            await bot.send_message(text=text, chat_id=chat_id)
    except Exception as e:
        logger.error(e)
        return

async def run_bot(messages, chat_id):
    text = ' '.join(messages)
    await send_message(text, chat_id)

def new_ip_entry():
    return {
            "first_access": None,
            "uris": [],
            "status": ''
    }

def new_cache_entry():
    return {
        'city': '',
        'region': ''
    }

async def get_ipinfo(ip,session):
    if ip in ip_cache:
        entry = ip_cache[ip]
        city = entry['city']
        region = entry['region']
        if city and region:
            return f"{city}, {region}"

    try:
        async with session.get(f"https://ipinfo.io/{ip}/json",timeout=aiohttp.ClientTimeout(total=5)) as res:
            res.raise_for_status()

            data = await res.json()

            city = data.get('city','Error retrieving city')
            region = data.get('region','Error retrieving region')

            ip_cache[ip]['city'] = city
            ip_cache[ip]['region'] = region

            return f"{city}, {region}"
    except asyncio.TimeoutError:
        err_message = f"Connection timed out for ip {ip}"
    except (json.JSONDecodeError,KeyError):
        err_message = f"Invalid parse format for ip {ip}"
    except aiohttp.ClientError as e:
        err_message = f"Client error: {e}"
    except Exception as e:
        err_message = f"Unknown exception: \"{e}\" for {ip}"
    
    logger.error(err_message)
    return err_message

def parse_logs(lines):
    dic = defaultdict(new_ip_entry)

    for line in lines:
        try:
            el = json.loads(line) 
            uri = el['request']['uri']

            if uri not in watched_uris:
                continue
            
            ip = el['request']['client_ip']
            ts = el['ts']
            status = el['status']
            dic[ip]['uris'].append(uri)
            dic[ip]['status'] = status

            if dic[ip]['first_access'] is None:
                dic[ip]['first_access'] = ts 

        except json.JSONDecodeError:
            logger.warning("Wrong json in monitored log file")
            continue
    
    return dic

async def create_message(dic, session):
    messages = []
    for ip,infos in dic.items():
        ip_details = await get_ipinfo(ip,session)
        message = f"Ip {ip} ({ip_details}) accessed at {infos['first_access']} and returned status {infos['status']}.\n" 
        if len(infos['uris']) > 0:
            message += f"Accessed uris: {infos['uris']}."
        else:
            message += "Unknown uris were accessed"
        messages.append(message)
    
    message_size = sum(len(m) for m in messages)
    
    if message_size > 4096:
        messages=messages[-1:]
        warn = 'Other IPs were detected but message was too long. Only last acces is being displayed'
        logger.warning(warn)
        messages.append(warn)

    return messages

async def handle_log(session: aiohttp.ClientSession):
    global last_pos
    
    with open(LOG_PATH,'r') as f:
        cur_size = os.path.getsize(LOG_PATH)
        if cur_size < last_pos:
            logger.info("Log rotation detected")
            last_pos = 0
        f.seek(last_pos)
        lines = f.readlines()
        last_pos= f.tell()

    dic = parse_logs(lines)
        
    messages = await create_message(dic,session)
    if messages:
        await run_bot(messages,CHAT_ID)

async def process_log(queue: asyncio.Queue):
    logger.info("Main started")
    async with aiohttp.ClientSession() as session:
        while True:
            await queue.get()
            logger.info("New access found")
            await handle_log(session)

def init_cache():
    global ip_cache
    ip_cache = defaultdict(new_cache_entry)

async def main():
    OUTPUTFILE="/var/log/telegram-log-monitor.log"
    if not os.access(OUTPUTFILE,os.W_OK):
        OUTPUTFILE=os.path.join(os.path.expanduser('~'),'.local/share/telegram-log-monitor.log')

    FORMAT = '[%(levelname)s] %(asctime)s: %(message)s'
    logging.basicConfig(format=FORMAT,filename=OUTPUTFILE,level=logging.INFO)

    init_cache()
    
    loop = asyncio.get_running_loop()
    queue = asyncio.Queue()

    event_handler = LogHandler(loop,queue)
    observer = Observer()
    observer.schedule(event_handler,path=LOG_DIR,recursive=False)
    observer.start()

    logger.info("Observer started")

    try:
        await process_log(queue)
    except Exception as e:
        logger.error(f"Unkown exception ({e}) in main process_log")
        exit(2)
    finally:
        observer.stop()
        observer.join()

asyncio.run(main())
