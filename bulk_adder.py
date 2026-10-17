import os
import csv
import random
import asyncio
import base64
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError, PeerFloodError, UserAlreadyParticipantError

API_ID = 34964566
API_HASH = '0e1adb6860c9e1a4269c87b22ecfd46a'
SESSION_STRING = os.environ.get('TG_SESSION')
# Aapka naya group
TARGET_GROUP = 'https://t.me/wingomaxhelpline' 

# Render se aane wala CSV data
CSV_DATA_B64 = os.environ.get('CSV_DATA_B64') 
CSV_FILE = 'users.csv'

# Render free tier ke liye dummy web server
def run_dummy_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bulk Adder is Running...")
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

async def main():
    print("Script start ho rahi hai...")
    
    # Base64 data ko CSV file me convert karna
    if CSV_DATA_B64:
        with open(CSV_FILE, "wb") as f:
            f.write(base64.b64decode(CSV_DATA_B64))
        print("CSV file load ho gayi.")
    
    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
        try:
            group = await client.get_entity(TARGET_GROUP)
        except Exception as e:
            print(f"Group nahi mila (Kya aap admin hain?): {e}")
            return

        usernames = []
        try:
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and not row[0].startswith('username'): 
                        usernames.append(row[0].strip()) 
        except FileNotFoundError:
            print(f"Error: {CSV_FILE} nahi mili. Env variable check karein.")
            return

        print(f"Total {len(usernames)} users add karne hain.")

        for index, user in enumerate(usernames, 1):
            try:
                user_entity = await client.get_input_entity(user)
                
                # Group me add karna
                if hasattr(group, 'megagroup') or hasattr(group, 'broadcast'):
                    await client(InviteToChannelRequest(channel=group, users=[user_entity]))
                else:
                    await client(AddChatUserRequest(chat_id=group.id, user_id=user_entity, fwd_limit=10))
                
                print(f"[{index}/{len(usernames)}] Success: {user} added.")
                
                # Telegram block se bachne ke liye 40 se 90 second ka gap
                delay = random.randint(40, 90)
                print(f"Waiting for {delay} seconds...")
                await asyncio.sleep(delay)

            except FloodWaitError as e:
                print(f"Flood wait! Telegram ne {e.seconds} seconds ka wait karne ko kaha hai.")
                await asyncio.sleep(e.seconds)
            except UserPrivacyRestrictedError:
                print(f"[{index}] Skipped: {user} ki privacy ne add nahi hone diya.")
            except PeerFloodError:
                print("Bohot zyada requests! Account block ho sakta hai. Aaj ke liye ruk jayein.")
                break
            except UserAlreadyParticipantError:
                print(f"[{index}] Skipped: {user} pehle se group me hai.")
            except Exception as e:
                print(f"[{index}] Error adding {user}: {e}")

if __name__ == '__main__':
    # Web server start karein (Render ko zinda rakhne ke liye)
    threading.Thread(target=run_dummy_server, daemon=True).start()
    # Main scraper/add script start karein
    asyncio.run(main())
