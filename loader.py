from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from Src.config import BOT_TOKEN, BOT_NAME

import logging

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

#logging.basicConfig(filename="bot.log", level=logging.INFO)
log = logging.getLogger(BOT_NAME)
log.setLevel(logging.INFO)