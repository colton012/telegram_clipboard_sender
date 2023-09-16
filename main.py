import asyncio
import pyperclip
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from PIL import ImageGrab
import io
import hashlib
import configparser 

config = configparser.ConfigParser()  
config.read('config.ini') 

TOKEN = config['main']['TOKEN']
USERID = int(config['main']['USERID'])

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
logging_middleware = LoggingMiddleware()
dp.middleware.setup(logging_middleware)

previous_clipboard_content = ""
previous_screenshot_hash = ""

async def get_content_hash(content):
    if isinstance(content, bytes):
        return hashlib.md5(content).hexdigest()
    else:
        return hashlib.md5(content.encode()).hexdigest()

async def send_clipboard_content():
    global previous_clipboard_content, previous_screenshot_hash

    while True:
        clipboard_content = pyperclip.paste()
        
        clipboard_hash = await get_content_hash(clipboard_content)

        try:
            screenshot = ImageGrab.grabclipboard()
            if screenshot:
                with io.BytesIO() as output:
                    screenshot.save(output, format="PNG")
                    screenshot_bytes = output.getvalue()
                    screenshot_hash = await get_content_hash(screenshot_bytes)
            else:
                screenshot_bytes = b""
                screenshot_hash = ""

            if clipboard_hash != previous_clipboard_content or screenshot_hash != previous_screenshot_hash:
                previous_clipboard_content = clipboard_hash
                previous_screenshot_hash = screenshot_hash

                if screenshot_hash:
                    await bot.send_photo(chat_id=USERID, photo=screenshot_bytes)
                elif clipboard_content.strip():
                    await bot.send_message(chat_id=USERID, text=clipboard_content)
        except Exception as e:
            print(f"Ошибка при отправке: {str(e)}")

        await asyncio.sleep(1)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(send_clipboard_content())
    executor.start_polling(dp, loop=loop, skip_updates=True)
