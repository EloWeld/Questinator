import json

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import *
from aiogram.types import *

from Main.backend.validators import isValidNickname
from Main.backend import registerUser, getSocialLinks
from Middleware.database import UsersDB
from Misc.filters import IsGuest, IsPrivate, IsUser
from Src import nav
from Src.nav import startMenu
from Src.states import Registration
from Src.config import NAV, MSG, CMDS

from loader import dp, log, bot


# ==================== MESSAGES ================== #
@dp.message_handler(IsGuest(), Text(NAV["REGISTER"]))
@dp.message_handler(IsGuest(), Command(CMDS["REGISTER"]))
async def cmdRegister(message: Message):
    await message.answer(text=MSG["R_REGISTER"])
    await message.answer(text=MSG["R_DESC"], reply_markup=ReplyKeyboardRemove())
    await Registration.Description.set()
    await dp.get_current().current_state().update_data(is_edit=False)


# ========================= (DESCRIPTION) =========================
@dp.message_handler(IsUser(), Text(NAV["KEEP"]), state=Registration.Description)
async def stateRegDescKeep(message: Message, state: FSMContext):
    await state.update_data(description=(await state.get_data())["u_data"]["description"])

    await message.answer(text=MSG["R_PHOTO"], reply_markup=nav.keep_curr)
    await Registration.Photo.set()


@dp.message_handler(IsPrivate(), state=Registration.Description)
async def stateRegDesc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)

    is_edit = (await state.get_data())["is_edit"]
    await message.answer(text=MSG["R_PHOTO"], reply_markup=nav.keep_curr if is_edit else nav.skip_menu)
    await Registration.Photo.set()


# ========================= (PHOTO) =========================
@dp.message_handler(IsPrivate(), Text(NAV["SKIP"]), state=Registration.Photo)
async def stateRegPhotoSkip(message: Message, state: FSMContext):
    await state.update_data(photo="NO_PHOTO")

    is_edit = (await state.get_data())["is_edit"]
    await message.answer(text=MSG["R_SN_LINKS"], reply_markup=nav.keep_curr if is_edit else nav.skip_menu)
    await Registration.Links.set()


@dp.message_handler(IsUser(), Text(NAV["KEEP"]), state=Registration.Photo)
async def stateRegPhotoKeep(message: Message, state: FSMContext):
    await state.update_data(photo=(await state.get_data())["u_data"]["photo"])

    await message.answer(text=MSG["R_SN_LINKS"], reply_markup=nav.keep_curr)
    await Registration.Links.set()


@dp.message_handler(IsPrivate(), state=Registration.Photo, content_types=['photo'])
async def stateRegPhoto(message: Message, state: FSMContext):
    photo_id = message.photo[0].file_id
    await state.update_data(photo=photo_id)

    is_edit = (await state.get_data())["is_edit"]
    await message.answer(text=MSG["R_SN_LINKS"], reply_markup=nav.keep_curr if is_edit else nav.skip_menu)
    await Registration.Links.set()


# ========================= (LINKS) =========================
@dp.message_handler(IsUser(), Text(NAV["KEEP"]), state=Registration.Links)
async def stateRegLinksKeep(message: Message, state: FSMContext):
    await state.update_data(links=(await state.get_data())["u_data"]["soc_net_links"])

    await message.answer(text=MSG["R_NICK"], reply_markup=nav.keep_curr)
    await Registration.ContraName.set()


@dp.message_handler(IsPrivate(), state=Registration.Links)
async def stateRegLinks(message: Message, state: FSMContext):
    await state.update_data(links=getSocialLinks(message.text))

    is_edit = (await state.get_data())["is_edit"]
    await message.answer(text=MSG["R_NICK"], reply_markup=nav.keep_curr if is_edit else ReplyKeyboardRemove())
    await Registration.ContraName.set()


# ========================= (CONTRA NAME) =========================
@dp.message_handler(IsUser(), Text(NAV["KEEP"]), state=Registration.ContraName)
async def stateNickLinks(message: Message, state: FSMContext):
    await state.update_data(contra_nick=(await state.get_data())["u_data"]["contra_nick"])
    await registerUser(message.from_user.id, await state.get_data())

    await message.answer(text=MSG["EDIT_FINISH"], reply_markup=startMenu(message.from_user.id))
    await state.finish()


@dp.message_handler(IsPrivate(), state=Registration.ContraName)
async def stateNickLinks(message: Message, state: FSMContext):
    validity = isValidNickname(message.text)

    if validity == 0:
        q = str(message.text).replace('<', '').replace('>', '')
        await state.update_data(contra_nick=q)
        await registerUser(message.from_user.id, await state.get_data())

        await message.answer(text=MSG["R_FINISH"], reply_markup=startMenu(message.from_user.id))
        await state.finish()
    elif validity == -1:
        await message.answer(text=MSG["R_NICK_1"], reply_markup=None)
        await Registration.ContraName.set()
    elif validity == -2:
        await message.answer(text=MSG["R_NICK_2"], reply_markup=None)
        await Registration.ContraName.set()
    elif validity == -3:
        await message.answer(text=MSG["R_NICK_3"], reply_markup=None)
        await Registration.ContraName.set()
