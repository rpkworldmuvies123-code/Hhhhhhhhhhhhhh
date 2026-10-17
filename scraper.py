import csv
import asyncio
import base64
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.errors import FloodWaitError

API_ID = 34964566
API_HASH = '0e1adb6860c9e1a4269c87b22ecfd46a'
SESSION_STRING = os.environ.get('TG_SESSION')
TARGET_GROUP = 'https://t.me/NIFTYSENSEX_12'

# Ye function tab chalega jab aap URL open karenge
def run_scraper():
    async def main():
        print(f"Connecting to Telegram and fetching ALL members from {TARGET_GROUP}...")
        async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
            try:
                group = await client.get_entity(TARGET_GROUP)
                filename = 'members.csv'
                total_count = 0
                
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['username', 'user_id', 'access_hash'])
                    offset = 0
                    limit = 200
                    
                    while True:
                        try:
                            participants = await client(GetParticipantsRequest(
                                channel=group, filter=ChannelParticipantsSearch(''),
                                offset=offset, limit=limit, hash=0
                            ))
                        except FloodWaitError as e:
                            print(f"Flood wait: {e.seconds} seconds...")
                            await asyncio.sleep(e.seconds + 5)
                            continue
                        
                        if not participants.users: break
                        for user in participants.users:
                            if user.username:
                                writer.writerow([user.username, user.id, user.access_hash])
                                total_count += 1
                        
                        offset += len(participants.users)
                        print(f"Abhi tak {total_count} members mil chuke hain...")
                        await asyncio.sleep(2)
                
                print(f"Success! Total {total_count} members ki details save ho gayi.")
                
                with open(filename, "rb") as file:
                    encoded_string = base64.b64encode(file.read()).decode('utf-8')
                    print("\n\n--- START OF CSV DATA ---")
                    for i in range(0, len(encoded_string), 2000):
                        print(encoded_string[i:i+2000])
                    print("--- END OF CSV DATA ---")
            except Exception as e:
                print(f"Error aa gaya: {e}")
    asyncio.run(main())

# Web server jo request aane par scraper start karega
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Scraping started! Check logs.")
        # Sirf ek baar chalne ke liye check
        if not getattr(self.server, 'is_running', False):
            self.server.is_running = True
            threading.Thread(target=run_scraper, daemon=True).start()

def run_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

if __name__ == '__main__':
    run_server()
