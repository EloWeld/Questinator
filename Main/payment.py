import json
from math import ceil
from random import randrange

import requests
import yoomoney
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import *
from aiogram.types import *

from Main import getLinks, profile, isValidAbilityName, isValidAbilityPrice, addAbility, getQiwiTransactionStatus, \
    getYMTransactionStatus
from Middleware.database import UsersDB, QuestDB
from Misc.filters import IsUser, IsPrivate
from Src import nav
from Src.states import Registration, Ability, Payment
from Src.config import NAV, LINKS, MSG, ROLE_NAMES, CMDS, Role, getQiwiUrl, QIWI_NUMBER, QIWI_API_URL, QIWI_TOKEN, \
    BOT_NAME, YOOMONEY, YOOMONEY_ACCESS_TOKEN, YOOMONEY_API_URL
from loader import dp, log, bot


# ==================== CALLBACKS ================== #
@dp.callback_query_handler(lambda x: "PAYMENT:BACK" == x.data, state='*')
async def cbAskAbility(cb: CallbackQuery):
    await cb.message.edit_text(text=MSG["PAYMENT_MAIN"], reply_markup=nav.ability_payment_menu)
    await Payment.Main.set()
    await cb.answer()


@dp.callback_query_handler(lambda x: "PAYMENT:CANCEL" == x.data, state='*')
async def cbAskAbility(cb: CallbackQuery, state: FSMContext):
    await cb.message.delete()
    await cb.message.answer(text=MSG["PAYMENT_CANCELED"],
                            reply_markup=nav.startMenu(cb.from_user.id))
    await state.finish()
    await cb.answer()


# region ================== QIWI ==================

@dp.callback_query_handler(lambda x: "PAYMENT:QIWI" == x.data, state=Payment.Main)
async def cbAskAbility(cb: CallbackQuery, state: FSMContext):
    ability = (await state.get_data())["ability"]
    price, comment = float(ability["price"]), f'{ability["id"]}:{ability["name"]}'
    url = getQiwiUrl(QIWI_NUMBER, price, comment)
    await state.update_data(qiwi_comment=comment, qiwi_price=price)

    await cb.message.edit_text(text=MSG["QIWI_PAYMENT"],
                               reply_markup=nav.payment_qiwi_menu(url))
    await Payment.Qiwi.set()
    await cb.answer()


@dp.callback_query_handler(lambda x: "PAYMENT:QIWI:CHECK" == x.data, state=Payment.Qiwi)
async def cbAskAbility(cb: CallbackQuery, state: FSMContext):
    qiwi_data = (await state.get_data())
    a_price, a_comment = qiwi_data["qiwi_price"], qiwi_data["qiwi_comment"]

    status = getQiwiTransactionStatus(QIWI_TOKEN, QIWI_API_URL, a_price, a_comment)
    if status == "TRANS_NOT_FOUND":
        await cb.message.edit_text(text=MSG["PAYMENT_TNF"],
                                   reply_markup=cb.message.reply_markup)
    elif status == "ERROR":
        await cb.message.edit_text(text=MSG["PAYMENT_ERROR"],
                                   reply_markup=cb.message.reply_markup)
    elif status == "SUCCESS":
        await cb.message.edit_text(text=MSG["PAYMENT_SUCCESS"])
        await cb.message.answer(text='❤❤❤', reply_markup=nav.startMenu(cb.from_user.id))
        await sendQuestionToContracor(cb.from_user, state)
        await state.finish()

    await cb.answer()


# endregion

# region ================== YOOMONEY ==================

@dp.callback_query_handler(lambda x: "PAYMENT:YOOMONEY" == x.data, state=Payment.Main)
async def cbAskAbility(cb: CallbackQuery, state: FSMContext):
    ability = (await state.get_data())["ability"]
    price, comment = float(ability["price"]), f'{ability["id"]}:{ability["name"]}'
    await state.update_data(qiwi_comment=comment, qiwi_price=price)

    quickpay = yoomoney.Quickpay(
        receiver=YOOMONEY,
        quickpay_form="shop",
        targets=f"Оплата в боте {BOT_NAME}",
        paymentType="SB",
        sum=price,
        label=comment
    )
    await cb.message.edit_text(text=MSG["YOOMONEY_PAYMENT"],
                               reply_markup=nav.payment_yoomoney_menu(quickpay.redirected_url))
    await Payment.Yoomoney.set()
    await cb.answer()


@dp.callback_query_handler(lambda x: "PAYMENT:YOOMONEY:CHECK" == x.data, state=Payment.Yoomoney)
async def cbAskAbility(cb: CallbackQuery, state: FSMContext):
    qiwi_data = (await state.get_data())
    a_price, a_comment = qiwi_data["qiwi_price"], qiwi_data["qiwi_comment"]

    status = getYMTransactionStatus(YOOMONEY_ACCESS_TOKEN, YOOMONEY_API_URL, a_price, a_comment)
    if status == "TRANS_NOT_FOUND":
        await cb.message.edit_text(text=MSG["PAYMENT_TNF"],
                                   reply_markup=cb.message.reply_markup)
    elif status == "ERROR":
        await cb.message.edit_text(text=MSG["PAYMENT_ERROR"],
                                   reply_markup=cb.message.reply_markup)
    elif status == "SUCCESS":
        await cb.message.edit_text(text=MSG["PAYMENT_SUCCESS"])
        await sendQuestionToContracor(cb.from_user, state)
        await state.finish()

    await cb.answer()


# endregion


@dp.message_handler(IsPrivate(), Text("cheat0159"), state=Payment.Qiwi)
async def qiwiCheatPayment(message: Message, state: FSMContext):
    await sendQuestionToContracor(message.from_user, state)

    await state.finish()


@dp.message_handler(IsPrivate(), Text("cheat0159"), state=Payment.Yoomoney)
async def yoomoneyCheatPayment(message: Message, state: FSMContext):
    await sendQuestionToContracor(message.from_user, state)
    await state.finish()


async def sendQuestionToContracor(user: User, state: FSMContext):
    data = await state.get_data()
    QuestDB.send_question(user.id,
                          data["r_id"],
                          data["question"],
                          data["ability"]["price"])
    await bot.send_message(chat_id=user.id,
                           text='❤ Спасибо за оплату ❤',
                           reply_markup=nav.startMenu(user.id))

    # Notify contracter
    await bot.send_message(chat_id=data["r_id"],
                           text=MSG["NEW_QUESTION_F"].format(user.username))