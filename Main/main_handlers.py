from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import *
from aiogram.types import *

from Main.profile import openProfileByNick
from Middleware.database import UsersDB
from Misc.filters import IsPrivate
from Src import *
from loader import dp, log


# ==================== MESSAGES ================== #
@dp.message_handler(IsPrivate(), commands=[CMDS["START"]])
async def cmdStart(message: Message, command):
    if command.args is not None:
        profile_name = command.args.split()[0]
        await openProfileByNick(message.from_user.id, profile_name)
    try:
        UsersDB.addUser(message.from_user)
    except Exception as e:
        log.info(f"Can't add user {message.from_user.username} {str(e.args)}")
        print(f"Can't add user {message.from_user.username} {str(e.args)}")

    await message.answer(text=MSG["MOTO"], reply_markup=nav.startMenu(message.from_user.id))


@dp.message_handler(IsPrivate(), Command(CMDS["START"]), state='*')
async def cmdStart(message: Message, command, state: FSMContext):
    await message.answer(text=MSG["RESTART_MOTO"], reply_markup=nav.startMenu(message.from_user.id))
    await state.finish()


@dp.message_handler(IsPrivate(), Text(NAV["ABOUT"]))
async def btnAbout(message: Message):
    await message.answer(text=MSG["ABOUT"])


@dp.message_handler(commands=["loveme"])
async def loveme(message: Message):
    await message.answer(text=
                         '''
  ,d88b.d88b,
88888888888
`Y8888888Y'
   `Y888Y'    -Alyona Fontenelle is my queen-
     `Y'

'''
                         )
