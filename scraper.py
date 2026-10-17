import csv
import asyncio
import base64
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

API_ID = 34964566
API_HASH = '0e1adb6860c9e1a4269c87b22ecfd46a'
SESSION_STRING = os.environ.get('TG_SESSION')
TARGET_GROUP = 'https://t.me/NIFTYSENSEX_12'

def run_dummy_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

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
                    participants = await client.get_participants(group, limit=limit, offset=offset, aggressive=True)
                    if not participants:
                        break
                        
                    for user in participants:
                        if user.username:
                            writer.writerow([user.username, user.id, user.access_hash])
                            total_count += 1
                    
                    offset += limit
                    print(f"Abhi tak {total_count} members mil chuke hain...")
                    await asyncio.sleep(2)
            
            print(f"Success! Total {total_count} members ki details save ho gayi.")
            
            with open(filename, "rb") as file:
                encoded_string = base64.b64encode(file.read()).decode('utf-8')
                print("\n\n--- START OF CSV DATA ---")
                
                # Data ko 2000 character ke chhote chunks me print karega
                chunk_size = 2000
                for i in range(0, len(encoded_string), chunk_size):
                    print(encoded_string[i:i+chunk_size])
                    
                print("--- END OF CSV DATA ---")
            
        except Exception as e:
            print(f"Error aa gaya: {e}")

if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()
    asyncio.run(main())
