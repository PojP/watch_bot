from aiogram import Dispatcher, types, Bot
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F

from ast import literal_eval
import re
import sys
import random
from base64 import b64decode
from datetime import datetime
import os
import requests
import bs4

import validators

import pytube
from pytube.exceptions import VideoUnavailable
bot = None






import re
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import requests as r
from selenium.webdriver.common.by import By

options = webdriver.FirefoxOptions()
options.add_argument('--headless')

driver = webdriver.Firefox(options=options)


def is_instagram_reels_url(url) -> bool:
    """
    Check the url is instagram reels url?
    :param url: instagram reels url
    :return: bool
    """
    pattern = r"https?://(?:www\.)?instagram\.com/reel/.*"
    match = re.match(pattern, url)
    if match:
        return True
    return False


def download_reels(url) -> bytes:
    """
    Download reels video

    :param url: instagram reels url
    :return: bytes
    """
    driver.get(url)

    wait = WebDriverWait(driver, 10)

    element = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'video')))

    reel_source = element.get_attribute('src')

    return r.get(reel_source).content







async def start(msg: types.Message):
    await msg.answer("Привет! Это бот для загрузки видео из TikTok и YouTube. Просто введите ссылку и получите видео. Удачи:)")

async def downloader(msg: types.Message):
    print("work")
    try:
        if validators.url(msg.text):
            if "tiktok.com/" in msg.text:

                ses = requests.Session()
                server_url = 'https://musicaldown.com/'
                headers = {
                    "Host": "musicaldown.com",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "DNT": "1",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "TE": "trailers"
                }
                ses.headers.update(headers)
                req = ses.get(server_url)
                data = {}
                parse = bs4.BeautifulSoup(req.text, 'html.parser')
                get_all_input = parse.findAll('input')
                for i in get_all_input:
                    if i.get("id") == "link_url":
                        data[i.get("name")] = msg.text
                    else:
                        data[i.get("name")] = i.get("value")
                post_url = server_url + "id/download"
                req_post = ses.post(post_url, data=data, allow_redirects=True)
                if req_post.status_code == 302 or 'This video is currently not available' in req_post.text or 'Video is private or removed!' in req_post.text:
                    print('- video private or remove')
                    return 'private/remove'
                elif 'Submitted Url is Invalid, Try Again' in req_post.text:
                    print('- url is invalid')
                    return 'url-invalid'
                get_all_blank = bs4.BeautifulSoup(req_post.text, 'html.parser').findAll(
                    'a', attrs={'target': '_blank'})

                download_link = get_all_blank[0].get('href')
                await msg.answer("Ждите, видео скачивается:)")
                get_content = requests.get(download_link)
                


                a=msg.text[23:].split('?')[0].replace('/','_')+".mp4"
                with open(a, 'wb') as fd:
                    fd.write(get_content.content)
                
                
                b=a[:-4]+str(datetime.now().time()).replace(':',"_").replace('.','_')+".mp4"
                os.rename(a,b)
            
                print(f"B IS HERE: {b}")

                try:
                    video_=FSInputFile(b)
                    await bot.send_video(msg.chat.id,video_)
                except Exception as e:
                    await bot.send_message(524845066,f"Ошибка!!\nЛинк: {msg.text} \n{e}")
                    print(e)
                    await msg.answer("Не вышло отправить видео. Ошибка отправлена разработчику")
                finally:
                    os.remove(b)

            elif msg.text[:19]=="https://youtube.com" or msg.text[:17]=="https://youtu.be/":

                await msg.answer("Ждите, видео скачивается:)")
                yt = pytube.YouTube(msg.text)
                stream = yt.streams.get_highest_resolution()

                print(yt.thumbnail_url)
                thumbnail_url=requests.get(yt.thumbnail_url.split('?')[0])
                
                th_a=msg.text[23:].split('?')[0].replace('/','_')+".jpeg"
                with open(th_a, 'wb') as fd:
                    fd.write(thumbnail_url.content)
                


                a=stream.download()
                b=a[:-4]+str(datetime.now().time()).replace(':',"_").replace('.','_')+".mp4"
                os.rename(a,b)
                print(b)
                try:
                    video_=FSInputFile(b)
                    thumbnail_=FSInputFile(th_a)
                    await bot.send_video(msg.chat.id,
                                         thumbnail=thumbnail_,
                                         video=video_,
                                         supports_streaming=True)
                except Exception as e:
                    await bot.send_message(524845066,f"Ошибка!!\nЛинк: {msg.text} \n{e}")
                    print(e)
                    await msg.answer("Не вышло отправить видео. Ошибка отправлена разработчику")
                finally:
                    os.remove(th_a)
                    os.remove(b)
            elif is_instagram_reels_url(msg.text):
                await msg.answer("Ждите, видео скачивается:)")
                reel=download_reels(msg.text)

                
                


                a=msg.text[30:].split('?')[0].replace('/','_')+".mp4"
                with open(a, 'wb') as fd:
                    fd.write(reel)
                
                
                b=a[:-4]+str(datetime.now().time()).replace(':',"_").replace('.','_')+".mp4"
                os.rename(a,b)
            
                print(f"B IS HERE: {b}")

                try:
                    video_=FSInputFile(b)
                    await bot.send_video(msg.chat.id,video_)
                except Exception as e:
                    await bot.send_message(524845066,f"Ошибка!!\nЛинк: {msg.text} \n{e}")
                    print(e)
                    await msg.answer("Не вышло отправить видео. Ошибка отправлена разработчику")
                finally:
                    os.remove(b)

                #await bot.send_video(msg.chat.id,video=,supports_streaming=True)

            else:
                await msg.answer("Неправильный url")
    
    except VideoUnavailable:
        await msg.answer("Видео недоступно для скачивания:(")

    except Exception as e:
        await bot.send_message(524845066,f"Ошибка!!\nЛинк: {msg.text} \n{e}")
        print(e)
        await msg.answer("Не вышло отправить видео. Ошибка отправлена разработчику")
def register_handlers(dp: Dispatcher, bot_: Bot):
    global bot
    bot =bot_
    dp.message.register(start, Command('start'))
    dp.message.register(downloader,F.text)
