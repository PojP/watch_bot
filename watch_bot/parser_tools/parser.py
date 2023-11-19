#from src.db_controller import db
import pyrogram
from config_reader import config
import asyncio
import re
from pyrogram import Client

api_id = int(config.api_id.get_secret_value())
api_hash = config.api_hash.get_secret_value()
content_chat_id=int(config.chat_id.get_secret_value())
target_chat_id=-1001902274622


def remove_emoji(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

async def main():
    async with Client("my_account", api_id, api_hash) as app:
        #print(await app.get_chat(target_chat_id))
        msgs_cnt=await app.get_chat_history_count(target_chat_id)
        print(msgs_cnt)
        counter=0
        titles=[]
        alph="йцукенгшщзхъфывапролджэячсмитьбюqwertyuiopasdfghjklzxcvbnm"
        alph+=alph.upper()+"0123456789"
        async for message in app.get_chat_history(target_chat_id):
            if message.caption is not None and "сезон" not in message.caption.lower() and message.video is not None and "#трейлер" not in message.caption:
                #print(message.caption)
                s=message.caption.split('\n')[0].split('(')[0]
                
                if s[0] not in alph:
                    s=s[1:]
                s=s.split("#")[0]
                s= ' '.join(s.split())
                s=remove_emoji(s)
                bad_array=["https://t.me/gairithi/83"]
                if s not in titles and not s.split(" «")[0].isdigit():
                    if not any(ext in s for ext in bad_array):
                        s=s.split('/')[0]
                        titles.append(s)
                        print(s)
                        counter+=1
            
        print(counter)
        print()
        print()
        print()
        print(titles)

def start():
    asyncio.run(main())



