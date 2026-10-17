import os
import csv
import time
import random
import asyncio
import base64
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError, PeerFloodError, UserAlreadyParticipantError

API_ID = 34964566
API_HASH = '0e1adb6860c9e1a4269c87b22ecfd46a'
SESSION_STRING = os.environ.get('TG_SESSION')
TARGET_GROUP = 'https://t.me/wingomaxhelpline' # Yahan naya group link daal diya hai
CSV_FILE = 'users.csv' 

async def main():
    print("Script start ho rahi hai...")
    
    # Agar CSV data environment variable me hai toh load karein
    CSV_DATA_B64 = os.environ.get('CSV_DATA_B64')
    if CSV_DATA_B64:
        with open(CSV_FILE, "wb") as f:
            f.write(base64.b64decode(CSV_DATA_B64))
        print("CSV file successfully load ho gayi environment se.")
    
    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
        try:
            group = await client.get_entity(TARGET_GROUP)
        except Exception as e:
            print(f"Group nahi mila: {e}")
            return

        usernames = []
        try:
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and not row[0].startswith('username'): # Header skip karein
                        usernames.append(row[0].strip()) 
        except FileNotFoundError:
            print(f"Error: {CSV_FILE} nahi mili.")
            return

        print(f"Total {len(usernames)} users add karne hain.")

        for index, user in enumerate(usernames, 1):
            try:
                user_entity = await client.get_input_entity(user)
                
                # Group me add karein
                if hasattr(group, 'megagroup') or hasattr(group, 'broadcast'):
                    await client(InviteToChannelRequest(channel=group, users=[user_entity]))
                else:
                    await client(AddChatUserRequest(chat_id=group.id, user_id=user_entity, fwd_limit=10))
                
                print(f"[{index}/{len(usernames)}] Success: {user} added.")
                
                # Account ban se bachane ke liye 40 se 90 second ka gap
                delay = random.randint(40, 90)
                print(f"Waiting for {delay} seconds...")
                await asyncio.sleep(delay)

            except FloodWaitError as e:
                print(f"Flood wait! {e.seconds} seconds ka wait karein.")
                await asyncio.sleep(e.seconds)
            except UserPrivacyRestrictedError:
                print(f"[{index}] Skipped: {user} ki privacy settings add nahi hone deti.")
            except PeerFloodError:
                print("Bohot zyada requests! Account block ho sakta hai. Aaj ke liye ruk jayein.")
                break
            except UserAlreadyParticipantError:
                print(f"[{index}] Skipped: {user} pehle se group me hai.")
            except Exception as e:
                print(f"[{index}] Error adding {user}: {e}")

if __name__ == '__main__':
    asyncio.run(main())
