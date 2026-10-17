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
        print("1. Script start ho rahi hai...", flush=True)
        if not SESSION_STRING:
            print("ERROR: TG_SESSION environment variable nahi mila!", flush=True)
            return
            
        try:
            async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
                print("2. Telegram se connect ho gaya.", flush=True)
                
                try:
                    source_entity = await client.get_entity(SOURCE_GROUP)
                    print(f"3. Source Group connect: {SOURCE_GROUP}", flush=True)
                    
                    target_entity = await client.get_entity(TARGET_GROUP)
                    print(f"4. Target Group connect: {TARGET_GROUP}", flush=True)
                except Exception as e:
                    print(f"ERROR: Group connect nahi ho paya. Kya aap dono group ke member/admin hain? Details: {e}", flush=True)
                    return

                offset = 0
                limit = 100
                total_added = 0
                total_checked = 0

                while True:
                    print(f"5. Members fetch kar rahe hain (Offset: {offset})...", flush=True)
                    try:
                        participants = await client(GetParticipantsRequest(
                            channel=source_entity, filter=ChannelParticipantsSearch(''),
                            offset=offset, limit=limit, hash=0
                        ))
                    except FloodWaitError as e:
                        print(f"Flood wait (fetch): {e.seconds} sec...", flush=True)
                        await asyncio.sleep(e.seconds + 5)
                        continue
                    except Exception as e:
                        print(f"ERROR fetch karte waqt: {e}", flush=True)
                        break

                    if not participants.users:
                        print("6. Saare members check ho gaye.", flush=True)
                        break

                    for user in participants.users:
                        if not user.username:
                            continue
                        total_checked += 1
                        print(f"[{total_checked}] Processing: {user.username}", flush=True)

                        try:
                            await client(InviteToChannelRequest(channel=target_entity, users=[user]))
                            total_added += 1
                            print(f"✅ Added: {user.username} (Total: {total_added})", flush=True)
                            delay = random.randint(MIN_DELAY, MAX_DELAY)
                            print(f"⏳ Wait {delay} sec...\n", flush=True)
                            await asyncio.sleep(delay)
                        except FloodWaitError as e:
                            print(f"⏳ Flood wait (add): {e.seconds} sec...", flush=True)
                            await asyncio.sleep(e.seconds + 5)
                        except UserPrivacyRestrictedError:
                            print(f"❌ Skipped: {user.username} (Privacy restricted)", flush=True)
                        except PeerFloodError:
                            print("🚫 PeerFloodError: Account ban ho sakta hai. Ruk rahe hain.", flush=True)
                            return
                        except UserAlreadyParticipantError:
                            print(f"⏩ Skipped: {user.username} (Already in group)", flush=True)
                        except Exception as e:
                            print(f"⚠️ Error add karte waqt: {e}", flush=True)
                    
                    offset += len(participants.users)
            print("Script khatam.", flush=True)
        except Exception as e:
            print(f"ERROR: TelegramClient connect nahi ho paya. Session expire ho sakta hai. Details: {e}", flush=True)

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
        self.wfile.write(b"<h1>Trigger aaya! Ab Render ke Logs tab me jayein aur dekhein.</h1>")
        # Background me scraper start karega
        threading.Thread(target=run_scraper, daemon=True).start()

def run_server():
    port = int(os.environ.get('PORT', 10000))
    print(f"Server start ho raha hai PORT: {port} par...", flush=True)
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

if __name__ == '__main__':
    run_server()
