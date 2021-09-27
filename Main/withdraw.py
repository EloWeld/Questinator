import json

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import *
from aiogram.types import *

from Main.backend.validators import isValidCardNumber, isValidWDAmount, formatCardName
from Main.backend.backend import getCardInfo
from Middleware.database import UsersDB, WithdrawsDB
from Misc.filters import IsGuest, IsUser
from Misc.utils import notify_role
from Src import nav
from Src.config import NAV, MSG, CMDS, Role
from Src.states import Registration, Payment
from loader import dp


# ==================== CALLBACKS ================== #
@dp.callback_query_handler(lambda x: "EDIT_CARD" in x.data)
async def cbEditCard(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer(text=MSG["NEW_CARD_MOTO"], reply_markup=ReplyKeyboardRemove())
    await Payment.NewCard.set()
    await dp.get_current().current_state().update_data(require_withdraw=False)


@dp.callback_query_handler(lambda x: "WITHDRAW" in x.data)
async def cbEditProfile(cb: CallbackQuery):
    await cb.message.answer(text=MSG["WITHDRAW_MOTO"])
    withdraw_data = UsersDB.get(cb.from_user.id, "withdraw_data")
    unprocessed_trans = any(x["status"] == "WAITING"
                            for x in WithdrawsDB.all_requests()
                            if x["sender_id"] == cb.from_user.id)
    await cb.answer()

    if unprocessed_trans:
        await cb.message.answer(text='У вас уже есть заявка на вывод!')
    elif not withdraw_data:
        await cb.message.answer(text=MSG["NEW_CARD_MOTO"], reply_markup=ReplyKeyboardRemove())
        await Payment.NewCard.set()
        await dp.get_current().current_state().update_data(require_withdraw=True)
    else:
        await cb.message.answer(text=MSG["BANK_INFO"].format(**withdraw_data), disable_web_page_preview=True)
        await cb.message.answer(text=MSG["WITHDRAW_ENTER_AMOUNT"], reply_markup=ReplyKeyboardRemove())
        await Payment.Widthdraw.set()


# ==================== MESSAGES ================== #
@dp.message_handler(IsUser(), state=Payment.Widthdraw)
async def stateNewCard(message: Message, state: FSMContext):
    amount = message.text
    u_deposit = UsersDB.get(message.from_user.id, "deposit")
    if not isValidWDAmount(amount):
        await message.answer(text='Некорректная сумма перевода! Ввывод отменён',
                             reply_markup=nav.startMenu(message.from_user.id))
        await state.finish()
    elif float(amount) > float(u_deposit):
        await message.answer(text='Недостаточно средств! Ввывод отменён',
                             reply_markup=nav.startMenu(message.from_user.id))
        await state.finish()
    else:
        WithdrawsDB.add_request(message.from_user.id, float(amount))
        await message.answer(text='Заявка на вывод отправлена на модерацию',
                             reply_markup=nav.startMenu(message.from_user.id))
        await state.finish()

        # Notify admins
        await notify_role(Role.Admin.value, "Есть новая анкета на вывод!")


@dp.message_handler(IsUser(), state=Payment.NewCard)
async def stateNewCard(message: Message, state: FSMContext):
    card_number = str(message.text).replace(' ', '').replace('-', '')
    if not isValidCardNumber(card_number):
        await message.answer(text=MSG["INVALID_CARD"],
                             reply_markup=nav.startMenu(message.from_user.id))
        await state.finish()
    else:
        info = getCardInfo(formatCardName(card_number))
        UsersDB.update(message.from_user.id, "withdraw_data", json.dumps(info))

        await message.answer(text=MSG["CARD_ADDED"])
        await message.answer(text=MSG["BANK_INFO"].format(**info),
                             disable_web_page_preview=True,
                             reply_markup=nav.startMenu(message.from_user.id))

        if (await state.get_data())["require_withdraw"]:
            await message.answer(text=MSG["WITHDRAW_ENTER_AMOUNT"])
            await Payment.Widthdraw.set()
        else:
            await state.finish()
