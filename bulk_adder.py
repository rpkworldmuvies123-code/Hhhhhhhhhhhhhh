import os
import asyncio
import random
import threading
import traceback
import base64
import csv
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError, PeerFloodError, UserAlreadyParticipantError

# ================= CONFIGURATION =================
API_ID = 34964566
API_HASH = '0e1adb6860c9e1a4269c87b22ecfd46a'
SESSION_STRING = os.environ.get('TG_SESSION')
CSV_BASE64_DATA = os.environ.get('CSV_DATA_B64')
TARGET_GROUP = 'https://t.me/wingomaxhelpline'

# High-Level Settings (Safe Speed)
DAILY_LIMIT = 40          # Ek din me sirf 40 members add honge (Account safe rahega)
MIN_DELAY = 120           # 2 minute ka gap
MAX_DELAY = 240           # 4 minute ka gap
PROGRESS_FILE = 'progress.json' # Kahan tak add hua, ye save karega
# =================================================

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"added_today": 0, "last_index": 0}

def save_progress(added_today, last_index):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump({"added_today": added_today, "last_index": last_index}, f)

def run_adder():
    async def main():
        print("🚀 High-Level Script Start Ho Rahi Hai...", flush=True)
        
        if not CSV_BASE64_DATA:
            print("❌ ERROR: CSV_DATA_B64 nahi mila Render ke Environment me!", flush=True)
            return

        # Load Progress
        progress = load_progress()
        added_today = progress["added_today"]
        start_index = progress["last_index"]

        if added_today >= DAILY_LIMIT:
            print(f"🛑 Aaj ki limit ({DAILY_LIMIT}) poori ho chuki hai. Kal wapas aayein.", flush=True)
            return

        try:
            with open("members.csv", "wb") as f:
                f.write(base64.b64decode(CSV_BASE64_DATA.strip()))
            print("✅ Members data load ho gaya.", flush=True)
        except Exception as e:
            print(f"❌ ERROR: Data decode fail: {e}", flush=True)
            return

        usernames = []
        try:
            with open("members.csv", "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and not row[0].startswith("username"):
                        usernames.append(row[0].strip())
            print(f"✅ Total {len(usernames)} members mile hain.", flush=True)
        except Exception as e:
            print(f"❌ ERROR: CSV read fail: {e}", flush=True)
            return

        async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
            try:
                target_entity = await client.get_entity(TARGET_GROUP)
                print(f"✅ Target Group Connect: {TARGET_GROUP}", flush=True)
                
                # Generate Invite Link
                try:
                    invite_link = await client(ExportChatInviteRequest(target_entity))
                    INVITE_LINK = invite_link.link
                except:
                    INVITE_LINK = "https://t.me/wingomaxhelpline"

            except Exception as e:
                print(f"❌ ERROR: Group connect nahi hua: {e}", flush=True)
                return

            # Start from where we left off
            for index in range(start_index, len(usernames)):
                if added_today >= DAILY_LIMIT:
                    print(f"🛑 Daily limit ({DAILY_LIMIT}) poori. Kal se aage badhenge.", flush=True)
                    save_progress(added_today, index)
                    return

                username = usernames[index]
                print(f"[{index + 1}/{len(usernames)}] Processing: {username}", flush=True)
                
                try:
                    user_entity = await client.get_input_entity(username)
                    await client(InviteToChannelRequest(channel=target_entity, users=[user_entity]))
                    
                    added_today += 1
                    save_progress(added_today, index + 1)
                    print(f"✅ Added: {username} (Aaj ka Total: {added_today}/{DAILY_LIMIT})", flush=True)
                    
                    # Smart Delay
                    delay = random.randint(MIN_DELAY, MAX_DELAY)
                    print(f"⏳ Waiting for {delay // 60} minutes...\n", flush=True)
                    await asyncio.sleep(delay)

                except UserPrivacyRestrictedError:
                    print(f"❌ Privacy restricted: {username}", flush=True)
                    save_progress(added_today, index + 1)
                except FloodWaitError as e:
                    print(f"🚨 FLOOD WAIT! Telegram ne {e.seconds} seconds ka ban lagaya hai.", flush=True)
                    print("Script khud wait karegi aur phir se start hogi...", flush=True)
                    save_progress(added_today, index)
                    await asyncio.sleep(e.seconds + 60)
                    return # Restart process
                except PeerFloodError:
                    print("🚫 PeerFloodError: Account spam mark ho gaya. 24 ghante rest karein.", flush=True)
                    save_progress(added_today, index)
                    return 
                except UserAlreadyParticipantError:
                    print(f"⏩ Already in group: {username}", flush=True)
                    save_progress(added_today, index + 1)
                except Exception as e:
                    print(f"⚠️ Error adding {username}: {e}", flush=True)
                    save_progress(added_today, index + 1)

        print("✅ Aaj ka kaam khatam.", flush=True)

    try:
        asyncio.run(main())
    except Exception as e:
        print("Main thread error:", flush=True)
        traceback.print_exc()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("=> Trigger aaya! Process start ho raha hai...", flush=True)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>High-Level Script Running. Check Logs.</h1>")
        threading.Thread(target=run_adder, daemon=True).start()

def run_server():
    port = int(os.environ.get('PORT', 10000))
    print(f"Server start ho raha hai PORT: {port} par...", flush=True)
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

if __name__ == '__main__':
    run_server()
