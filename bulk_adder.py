import os
import asyncio
import random
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError, PeerFloodError, UserAlreadyParticipantError

# ================= CONFIGURATION =================
API_ID = 34964566
API_HASH = '0e1adb6860c9e1a4269c87b22ecfd46a'
SESSION_STRING = os.environ.get('TG_SESSION') # Render se aayega

# Source group (Jahan se members nikalne hain)
SOURCE_GROUP = 'https://t.me/NIFTYSENSEX_12' 

# Target group (Jahan members add karne hain)
TARGET_GROUP = 'https://t.me/wingomaxhelpline' 

# Delay (Seconds) - Account ban se bachne ke liye
MIN_DELAY = 45
MAX_DELAY = 90
# =================================================

# Render free tier ke liye dummy server
def run_dummy_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Combined Scraper + Adder is Running...")
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

async def main():
    print("Script start ho rahi hai...")
    
    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
        try:
            print(f"Source Group Connect ho raha hai: {SOURCE_GROUP}")
            source_entity = await client.get_entity(SOURCE_GROUP)
            
            print(f"Target Group Connect ho raha hai: {TARGET_GROUP}")
            target_entity = await client.get_entity(TARGET_GROUP)
            
        except Exception as e:
            print(f"Group nahi mila: {e}")
            return

        print("Members nikalna aur add karna shuru...")
        
        offset = 0
        limit = 100
        total_added = 0
        total_checked = 0
        
        while True:
            try:
                # Source group se members fetch karein
                participants = await client(GetParticipantsRequest(
                    channel=source_entity, 
                    filter=ChannelParticipantsSearch(''),
                    offset=offset, 
                    limit=limit, 
                    hash=0
                ))
            except FloodWaitError as e:
                print(f"Flood wait (Fetch): {e.seconds} seconds...")
                await asyncio.sleep(e.seconds + 5)
                continue
                
            if not participants.users:
                print("Source group ke saare members check ho gaye.")
                break
                
            for user in participants.users:
                if not user.username:
                    continue # Skip agar username nahi hai
                    
                total_checked += 1
                print(f"[{total_checked}] Processing user: {user.username}")
                
                try:
                    # Target group me add karein
                    if hasattr(target_entity, 'megagroup') or hasattr(target_entity, 'broadcast'):
                        await client(InviteToChannelRequest(channel=target_entity, users=[user]))
                    else:
                        await client(AddChatUserRequest(chat_id=target_entity.id, user_id=user, fwd_limit=10))
                        
                    total_added += 1
                    print(f"✅ Success: {user.username} added. (Total Added: {total_added})")
                    
                    # Telegram block se bachne ke liye delay
                    delay = random.randint(MIN_DELAY, MAX_DELAY)
                    print(f"⏳ Waiting for {delay} seconds...\n")
                    await asyncio.sleep(delay)
                    
                except FloodWaitError as e:
                    print(f"⏳ Flood wait (Add): {e.seconds} seconds...")
                    await asyncio.sleep(e.seconds + 5)
                except UserPrivacyRestrictedError:
                    print(f"❌ Skipped: {user.username} ki privacy settings add nahi hone deti.")
                except PeerFloodError:
                    print("🚫 PeerFloodError: Bohot zyada requests! Account block ho sakta hai. Script rok rahi hai.")
                    return # Script exit
                except UserAlreadyParticipantError:
                    print(f"⏩ Skipped: {user.username} pehle se target group me hai.")
                except Exception as e:
                    print(f"⚠️ Error adding {user.username}: {e}")
            
            offset += len(participants.users)
            print(f"--- Agle {limit} members fetch kar rahe hain (Total Checked: {total_checked}) ---")

if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()
    asyncio.run(main())
