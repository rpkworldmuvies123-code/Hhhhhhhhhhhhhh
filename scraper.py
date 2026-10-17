import csv
import asyncio
import base64
import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

API_ID = 34964566
API_HASH = '0e1adb6860c9e1a4269c87b22ecfd46a'
# String session Render ke environment variable se aayega
SESSION_STRING = os.environ.get('TG_SESSION') 
TARGET_GROUP = 'https://t.me/NIFTYSENSEX_12'

async def main():
    print(f"Connecting to Telegram and fetching members from {TARGET_GROUP}...")
    
    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
        try:
            group = await client.get_entity(TARGET_GROUP)
            print("Fetching members, please wait... (Group bada hai toh time lagega)")
            
            participants = await client.get_participants(group, aggressive=True)
            
            filename = 'members.csv'
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['username', 'user_id', 'access_hash'])
                
                count = 0
                for user in participants:
                    if user.username:
                        writer.writerow([user.username, user.id, user.access_hash])
                        count += 1
                        
            print(f"Success! {count} members ki details save ho gayi.")
            
            # File ko base64 me convert karke print karein taaki Render logs se copy kar sakein
            with open(filename, "rb") as file:
                encoded_string = base64.b64encode(file.read()).decode('utf-8')
                print("\n\n--- START OF CSV DATA ---")
                print(encoded_string)
                print("--- END OF CSV DATA ---")
                print("\nUpar wale code ko copy karein.")
            
        except Exception as e:
            print(f"Error aa gaya: {e}")

if __name__ == '__main__':
    asyncio.run(main())
