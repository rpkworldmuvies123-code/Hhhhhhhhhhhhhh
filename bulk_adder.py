import os
import asyncio
import random
import threading
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetParticipantsRequest, InviteToChannelRequest
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError, PeerFloodError, UserAlreadyParticipantError

API_ID = 34964566
API_HASH = '0e1adb6860c9e1a4269c87b22ecfd46a'
SESSION_STRING = os.environ.get('TG_SESSION')
SOURCE_GROUP = 'https://t.me/NIFTYSENSEX_12'
TARGET_GROUP = 'https://t.me/wingomaxhelpline'
MIN_DELAY = 45
MAX_DELAY = 90

# Global flag taaki script baar-baar na chale
is_running = False

def run_scraper():
    global is_running
    if is_running:
        return
    is_running = True

    async def main():
        print("Script start ho rahi hai...")
        async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
            try:
                source_entity = await client.get_entity(SOURCE_GROUP)
                target_entity = await client.get_entity(TARGET_GROUP)
            except Exception as e:
                print(f"Group nahi mila: {e}")
                return

            offset = 0
            limit = 100
            total_added = 0
            total_checked = 0

            while True:
                try:
                    participants = await client(GetParticipantsRequest(
                        channel=source_entity, filter=ChannelParticipantsSearch(''),
                        offset=offset, limit=limit, hash=0
                    ))
                except FloodWaitError as e:
                    print(f"Flood wait: {e.seconds} sec...")
                    await asyncio.sleep(e.seconds + 5)
                    continue

                if not participants.users:
                    print("Saare members check ho gaye.")
                    break

                for user in participants.users:
                    if not user.username:
                        continue
                    total_checked += 1
                    print(f"[{total_checked}] Processing: {user.username}")

                    try:
                        await client(InviteToChannelRequest(channel=target_entity, users=[user]))
                        total_added += 1
                        print(f"✅ Added: {user.username} (Total: {total_added})")
                        delay = random.randint(MIN_DELAY, MAX_DELAY)
                        print(f"⏳ Wait {delay} sec...\n")
                        await asyncio.sleep(delay)
                    except FloodWaitError as e:
                        print(f"⏳ Flood wait: {e.seconds} sec...")
                        await asyncio.sleep(e.seconds + 5)
                    except UserPrivacyRestrictedError:
                        print(f"❌ Skipped: Privacy restricted.")
                    except PeerFloodError:
                        print("🚫 PeerFloodError: Account ban ho sakta hai. Stopping.")
                        return
                    except UserAlreadyParticipantError:
                        print(f"⏩ Skipped: Already in group.")
                    except Exception as e:
                        print(f"⚠️ Error: {e}")
                offset += len(participants.users)
        print("Script khatam ho gayi.")

    asyncio.run(main())
    is_running = False

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>Script Start Ho Gayi! Logs check karein.</h1>")
        # Jab UptimeRobot URL open karega, tab script start hogi
        threading.Thread(target=run_scraper, daemon=True).start()

def run_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

if __name__ == '__main__':
    run_server()
