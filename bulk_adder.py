import os
import asyncio
import random
import threading
import traceback
import base64
import csv
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError, PeerFloodError, UserAlreadyParticipantError

API_ID = 34964566
API_HASH = '0e1adb6860c9e1a4269c87b22ecfd46a'
SESSION_STRING = os.environ.get('TG_SESSION')
TARGET_GROUP = 'https://t.me/wingomaxhelpline'

# Yahan hum data Environment Variable se utha rahe hain
CSV_BASE64_DATA = os.environ.get('CSV_DATA_B64')

MIN_DELAY = 10
MAX_DELAY = 15

def run_adder():
    async def main():
        print("1. Script start ho rahi hai...", flush=True)
        
        if not CSV_BASE64_DATA:
            print("ERROR: CSV_DATA_B64 nahi mila Render ke Environment me!", flush=True)
            return

        try:
            with open("members.csv", "wb") as f:
                f.write(base64.b64decode(CSV_BASE64_DATA.strip()))
            print("2. Members ka data load ho gaya.", flush=True)
        except Exception as e:
            print(f"ERROR: Base64 decode fail ho gaya: {e}", flush=True)
            return

        usernames = []
        try:
            with open("members.csv", "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and not row[0].startswith("username"):
                        usernames.append(row[0].strip())
            print(f"3. Total {len(usernames)} members mile hain.", flush=True)
        except Exception as e:
            print(f"ERROR: CSV read fail: {e}", flush=True)
            return

        async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
            try:
                target_entity = await client.get_entity(TARGET_GROUP)
                print(f"4. Target Group connect: {TARGET_GROUP}", flush=True)
                
                try:
                    invite_link = await client(ExportChatInviteRequest(target_entity))
                    INVITE_LINK = invite_link.link
                    print(f"Invite Link mil gaya: {INVITE_LINK}", flush=True)
                except Exception as e:
                    print(f"Invite link nahi ban paya, default use kar rahe hain. Error: {e}", flush=True)
                    INVITE_LINK = "https://t.me/wingomaxhelpline"

            except Exception as e:
                print(f"ERROR: Target group connect nahi hua: {e}", flush=True)
                return

            for index, username in enumerate(usernames, 1):
                print(f"[{index}/{len(usernames)}] Processing: {username}", flush=True)
                
                try:
                    user_entity = await client.get_input_entity(username)
                    await client(InviteToChannelRequest(channel=target_entity, users=[user_entity]))
                    
                    print(f"✅ Added: {username}", flush=True)
                    delay = random.randint(MIN_DELAY, MAX_DELAY)
                    print(f"⏳ Wait {delay} sec...\n", flush=True)
                    await asyncio.sleep(delay)

                except UserPrivacyRestrictedError:
                    print(f"❌ Privacy restricted, link bhej rahe hain: {username}", flush=True)
                    try:
                        await client.send_message(user_entity, f"Hello! Aapko group me invite kiya gaya hai. Join karne ke liye is link par click karein: {INVITE_LINK}")
                        print(f"✉️ Invite link message bhej diya: {username}", flush=True)
                    except Exception as msg_err:
                        print(f"⚠️ Message nahi gaya: {username} - {msg_err}", flush=True)
                        
                except FloodWaitError as e:
                    print(f"⏳ Flood wait: {e.seconds} sec...", flush=True)
                    await asyncio.sleep(e.seconds + 5)
                except PeerFloodError:
                    print("🚫 PeerFloodError: Account ban ho sakta hai. Ruk rahe hain...", flush=True)
                    await asyncio.sleep(300)
                    continue 
                except UserAlreadyParticipantError:
                    print(f"⏩ Skipped: {username} (Already in group)", flush=True)
                except Exception as e:
                    print(f"⚠️ Error add {username}: {e}", flush=True)

        print("Script khatam.", flush=True)

    try:
        asyncio.run(main())
    except Exception as e:
        print("Main thread error:", flush=True)
        traceback.print_exc()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("=> URL Open hua, trigger process start ho raha hai...", flush=True)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>Script chal rahi hai. Logs check karein.</h1>")
        threading.Thread(target=run_adder, daemon=True).start()

def run_server():
    port = int(os.environ.get('PORT', 10000))
    print(f"Server start ho raha hai PORT: {port} par...", flush=True)
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

if __name__ == '__main__':
    run_server()
