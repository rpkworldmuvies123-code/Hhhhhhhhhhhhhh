import os
import asyncio
import random
import threading
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetParticipantsRequest, InviteToChannelRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError, PeerFloodError, UserAlreadyParticipantError

API_ID = 34964566
API_HASH = '0e1adb6860c9e1a4269c87b22ecfd46a'
SESSION_STRING = os.environ.get('TG_SESSION')
SOURCE_GROUP = 'https://t.me/NIFTYSENSEX_12'
TARGET_GROUP = 'https://t.me/wingomaxhelpline'
MIN_DELAY = 45
MAX_DELAY = 90

def run_scraper():
    async def main():
        print("Script start ho rahi hai...")
        async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
            try:
                source_entity = await client.get_entity(SOURCE_GROUP)
                target_entity = await client.get_entity(TARGET_GROUP)
                print("Dono groups connect ho gaye.")
            except Exception as e:
                print(f"Group connect error: {e}")
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
                    print(f"Flood wait (fetch): {e.seconds} sec...")
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
                        print(f"⏳ Flood wait (add): {e.seconds} sec...")
                        await asyncio.sleep(e.seconds + 5)
                    except UserPrivacyRestrictedError:
                        print(f"❌ Skipped: {user.username} (Privacy restricted)")
                    except PeerFloodError:
                        print("🚫 PeerFloodError: Account ban ho sakta hai. Ruk rahe hain.")
                        return
                    except UserAlreadyParticipantError:
                        print(f"⏩ Skipped: {user.username} (Already in group)")
                    except Exception as e:
                        print(f"⚠️ Error: {e}")
                offset += len(participants.users)
        print("Script khatam.")

    try:
        asyncio.run(main())
    except Exception as e:
        print("Main thread error:")
        traceback.print_exc()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>Trigger aaya! Ab Logs check karein.</h1>")
        threading.Thread(target=run_scraper, daemon=True).start()

def run_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

if __name__ == '__main__':
    run_server()
