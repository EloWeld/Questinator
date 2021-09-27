import json

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import *
from aiogram.types import *

from Middleware.database import UsersDB
from Misc.filters import IsPrivate
from Src import nav
from Src.states import Registration, Payment, Question
from Src.config import NAV, MSG, ALLOW_CONTENT_TYPES
from loader import dp


# ==================== CALLBACKS ================== #
@dp.callback_query_handler(lambda x: "EDIT_PROFILE" in x.data)
async def cbEditProfile(cb: CallbackQuery):
    await cb.message.answer(text=MSG["R_DESC"])
    await cb.message.answer(text=MSG["R_EDIT_PROFILE"], reply_markup=nav.keep_curr)
    await Registration.Description.set()

    user_data = UsersDB.getUser(cb.from_user.id)
    await dp.get_current().current_state().update_data(is_edit=True, u_data=user_data)

    await cb.answer()


# ==================== MESSAGES ================== #
@dp.message_handler(IsPrivate(), state=Question.Main, content_types=ALLOW_CONTENT_TYPES)
async def stateAbilityDescDelete(msg: Message, state: FSMContext):
    if msg.text and msg.text == NAV["CANCEL"]:
        await msg.answer(text=MSG["Q_CANCEL"], reply_markup=nav.startMenu(msg.from_user.id))
        await state.finish()
        return

    msg_j = json.loads(str(msg))
    if "caption" in msg_j:
        msg_j["text"] = msg_j["caption"]
    print(msg_j)
    await state.update_data(question=msg_j)

    if "text" not in msg_j:  # No text / caption detected
        await msg.answer(text=MSG["ASK_QUESTION_CAPTION"],
                         reply_markup=nav.question_add_caption)
        await Question.ConfirmText.set()
    else:

        await msg.answer(text=MSG["ASK_QUESTION_PREVIEW"].format(msg_j["text"]),
                         reply_markup=nav.confirm_menu)
        await Question.Confirm.set()


# ==================== QUESTION CAPTION ================== #
@dp.message_handler(IsPrivate(), Text(NAV["QA_NO_CAPTION"]), state=Question.ConfirmText)
async def stateConfirmTextNoCap(message: Message):
    await message.answer(text=MSG["ASK_QUESTION_PREVIEW_NO_CAP"],
                         reply_markup=nav.confirm_menu)
    await Question.Confirm.set()


@dp.message_handler(IsPrivate(), state=Question.ConfirmText)
async def stateConfirmTextCap(message: Message, state: FSMContext):
    if message.text:
        q_update = (await state.get_data())["question"]
        q = str(message.text).replace('<', '').replace('>', '')
        q_update["text"] = q
        await state.update_data(question=q_update)
        await message.answer(text=MSG["ASK_QUESTION_PREVIEW"].format(q_update["text"]),
                             reply_markup=nav.confirm_menu)
        await Question.Confirm.set()
    else:
        await stateConfirmTextNoCap(message)


@dp.message_handler(IsPrivate(), Text(NAV["QA_CHANGE"]), state=Question.Confirm)
async def stateAbilityDescDelete(message: Message, state: FSMContext):
    await message.answer(text=MSG["ASK_QUESTION_MOTO"], reply_markup=nav.cancel_q_menu)
    await Question.Main.set()


@dp.message_handler(IsPrivate(), Text(NAV["QA_CANCEL"]), state=Question.Confirm)
async def stateAbilityDescDelete(message: Message, state: FSMContext):
    await message.answer(text=MSG["Q_CANCEL"],
                         reply_markup=nav.startMenu(message.from_user.id))
    await state.finish()


@dp.message_handler(IsPrivate(), Text(NAV["QA_CONFIRM"]), state=Question.Confirm)
async def stateAbilityDescDelete(message: Message, state: FSMContext):
    await message.answer(text=MSG["PAYMENT_MAIN"], reply_markup=nav.ability_payment_menu)
    await Payment.Main.set()
