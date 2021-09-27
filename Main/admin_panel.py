import os
import time

import requests
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ParseMode, ReplyKeyboardRemove, ContentType

from Main import getLinks, CallbackQuery, ceil
from Main.backend.validators import isValidFloat
from Middleware.database import UsersDB, WithdrawsDB
from Misc.filters import IsAdmin
from Src import NAV, nav, Role, MSG, QIWI_TOKEN, AdminPanel, CMDS
from loader import dp, bot


# ==================== COMMANDS ================== #
@dp.message_handler(IsAdmin(), commands=[CMDS["ADD_ADMIN"]])
async def cmdAddAdmin(message: Message, command):
    if command and command.args:
        nick = command.args.split()[0]
        user = UsersDB.getUserByContraNick(nick)
        # If username is not valid
        if not user:
            await message.answer('Пользователь {nick} не найден!')
            return

        # If already admin
        if user["tgid"] in UsersDB.allAdminsId():
            await message.answer(f'Пользователь {user["username"]} уже является админом!')
            return

        # Successful adding admin
        UsersDB.update(user["tgid"], "role", Role.Admin.value)
        await message.answer(f'@{user["username"]} Назначен Администратором!')
        await bot.send_message(chat_id=user["tgid"],
                               text=f'Вы назначены Администратором!'
                                    f'Ваш бог: @{message.from_user.username}')


@dp.message_handler(IsAdmin(), commands=[CMDS["CHANGE_FEE"]])
async def cmdAddAdmin(message: Message, command):
    if command and command.args:
        nick = command.args.split()[0]
        user = UsersDB.getUserByContraNick(nick)
        # If username is not valid
        if not user:
            await message.answer('Пользователь {nick} не найден!')
            return

        # If wrong num of args
        if len(command.args.split()) < 2:
            await message.answer('Не корректный запрос')
            return

        fee = command.args.split()[1]
        if fee == -1:
            fee = os.environ["GLOBAL_FEE"]
        # If invalid fee
        if not isValidFloat(fee):
            await message.answer('Не корректный размер комиссии')
            return

        # Successful changed fee
        UsersDB.update(user["tgid"], "custom_fee", fee)
        await message.answer(f'У @{user["username"]} теперь комиссия составляет {fee}%!')
        await bot.send_message(chat_id=user["tgid"],
                               text=f'Вам изменили комиссию до {fee}%!'
                                    f'Ваш бог: @{message.from_user.username}')


# ==================== MESSAGES ================== #
@dp.message_handler(IsAdmin(), Text(NAV["SEND_MSG"]))
async def txtBroadcast(message: Message):
    await message.answer(text="⭐Выбери опцию кому отправить сообщение",
                         reply_markup=nav.broadcast_menu)


@dp.message_handler(IsAdmin(), Text(NAV["SEND_MSG_C"]))
async def txtBroadcastContra(message: Message):
    await message.answer(text="⭐Отправь сообщение для рассылки исполнителям",
                         reply_markup=ReplyKeyboardRemove())
    await AdminPanel.Broadcast.set()
    await dp.get_current().current_state().update_data(broadcast_opt="CONTRAS")


@dp.message_handler(IsAdmin(), Text(NAV["SEND_MSG_ALL"]))
async def txtBroadcastAll(message: Message):
    await message.answer(text="⭐Отправь сообщение для рассылки всем пользователям",
                         reply_markup=ReplyKeyboardRemove())
    await AdminPanel.Broadcast.set()
    await dp.get_current().current_state().update_data(broadcast_opt="ALL")


@dp.message_handler(IsAdmin(), Text(NAV["QA_CONFIRM"]), state=AdminPanel.Broadcast)
async def stateBroadcastContras(message: Message, state: FSMContext):
    opt = (await state.get_data())["broadcast_opt"]
    broadcast_msg = (await state.get_data())["broadcast_msg"]
    users = UsersDB.allContrasId() if opt == "CONTRAS" else \
        UsersDB.allUsersId() if opt == "ALL" else []
    # Send broadcasted
    for user in users:
        await bot.send_message(chat_id=user, text=MSG["BROADCAST"].format(broadcast_msg))
    # Answer to god
    await message.answer(text="Сообщение разослано!",
                         reply_markup=nav.startMenu(message.from_user.id))
    await state.finish()


@dp.message_handler(IsAdmin(), Text(NAV["QA_CHANGE"]), state=AdminPanel.Broadcast)
async def stateBroadcastContras(message: Message):
    await message.answer(text="Введите сообщение заново:",
                         reply_markup=ReplyKeyboardRemove())
    await AdminPanel.Broadcast.set()


@dp.message_handler(IsAdmin(), Text(NAV["QA_CANCEL"]), state=AdminPanel.Broadcast)
async def stateBroadcastContras(message: Message, state: FSMContext):
    await message.answer(text="🚫 Рассылка отменена",
                         reply_markup=nav.startMenu(message.from_user.id))
    await state.finish()


@dp.message_handler(IsAdmin(), state=AdminPanel.Broadcast, content_types=[ContentType.ANY])
async def stateBroadcastAll(message: Message, state: FSMContext):
    q = str(message.text).replace('<', '').replace('>', '')
    await state.update_data(broadcast_msg=q)
    await message.answer(text="⭐Вот превью рассылки\n"
                              "———————————————\n"
                              f"{q}\n"
                              "———————————————\n",
                         reply_markup=nav.confirm_menu)


@dp.message_handler(IsAdmin(), Text(NAV["BACK"]))
async def txtAdminPanel(message: Message):
    await message.answer(text="⭐🌟⭐🌟⭐🌟⭐🌟", reply_markup=nav.startMenu(message.from_user.id))


@dp.message_handler(IsAdmin(), Text(NAV["ADMIN_P"]))
async def txtAdminPanel(message: Message):
    await message.answer(text="⭐🌟⭐🌟 ADMIN PANEL⭐🌟⭐🌟\n"
                              "Изменить комиссию исполнителю - /change_fee 'nick' 'new fee'\n"
                              "Назначить админом исполнителя /add_admin 'nick'",
                         reply_markup=nav.admin_panel)


@dp.message_handler(IsAdmin(), Text(NAV["AP_WITHDRAW_REQUESTS"]))
async def txtAdminWDRequests(message: Message):
    requests = [x for x in WithdrawsDB.all_requests() if x["status"] == "WAITING"]

    if len(requests) == 0:
        await message.answer(text=MSG["NO_WD_REQUESTS"])
        return

    for reqest in requests:
        u_data = UsersDB.getUser(reqest["sender_id"])
        await message.answer(text=MSG["WAITING_WD_REQUEST"].format(
            '@' + u_data["username"],
            reqest["amount"],
            u_data["withdraw_data"]["card"]
        ), reply_markup=nav.judge_wd(reqest["sender_id"], reqest["trans_id"]))


@dp.message_handler(IsAdmin(), Text(NAV["AP_REG_REQUESTS"]))
async def txtAdminRegRequests(message: Message):
    requests = [x for x in UsersDB.allUsers() if ":WAIT_REGISTER:" in x["statuses"]]
    for reqest in requests:
        txt = MSG["NEW_CONTRA"].format(reqest["contra_nick"], reqest["description"], getLinks(reqest["soc_net_links"]))
        reply = nav.judge_contra(reqest["tgid"])
        if "photo" in reqest and reqest["photo"] != "NO_PHOTO":
            await message.answer_photo(photo=reqest["photo"], caption=txt, reply_markup=reply)
        else:
            await message.answer(text=txt, reply_markup=reply)

    if len(requests) == 0:
        await message.answer(text=MSG["NO_REG_REQUESTS"])


@dp.message_handler(IsAdmin(), Text(NAV["CHANGE_GLOBAL_FEE"]))
async def txtAdminFee(message: Message):
    await message.answer(text=f'Текущая комиссия: {os.environ["GLOBAL_FEE"]}%\n'
                              f'Введите новый размер комиссии: 1-99')
    await AdminPanel.Fee.set()


@dp.message_handler(IsAdmin(), state=AdminPanel.Fee)
async def txtAdminFee(message: Message, state: FSMContext):
    if message.text.replace('.', '', 1).isdigit() and 0 < float(message.text) < 100:
        await message.answer(text=f'Установлен новый размер комиссии: {float(message.text)}%')
        os.putenv("GLOBAL_FEE", message.text)
        os.environ["GLOBAL_FEE"] = message.text
        await state.finish()
    else:
        await message.answer(text=f'Некорректный ввод!')
        await message.answer(text='Введите новый размер комиссии: 1-99')
        await AdminPanel.Fee.set()


# ==================== CALLBACKS ================== #
@dp.callback_query_handler(lambda x: "JUDGE_CONTRA" in x.data)
async def judgeContra(cb: CallbackQuery):
    _, action, user_id = cb.data.split(':')
    user_username = UsersDB.get(user_id, "username")
    txt = ""
    if action == "ACCEPT":
        UsersDB.update(user_id, "statuses", ":CONTRA:")
        if UsersDB.get(user_id, "role") != Role.Admin.value:
            UsersDB.update(user_id, "role", Role.User.value)
        txt = f"✅ Заявка пользователя <b>{user_username}</b> одобрена"
        await bot.send_message(chat_id=user_id, text=MSG["YOUR_REG_CONFIRMED"],
                               reply_markup=nav.startMenu(user_id))
    elif action == "REJECT":
        txt = f"🚫 Заявка пользователя <b>{user_username}</b> отклонена"
        await bot.send_message(chat_id=user_id, text=MSG["YOUR_REG_REJECTED"],
                               reply_markup=nav.startMenu(user_id))

    try:
        await cb.message.edit_caption(caption=txt)
    except:
        await cb.message.edit_text(text=txt)
    await cb.answer()


@dp.callback_query_handler(lambda x: "JUDGE_WD:" in x.data)
async def judgeContra(cb: CallbackQuery):
    _, action, user_id, trans = cb.data.split(':')
    await cb.answer()

    if action in ["WITHDRAW", "QIWIPAY"]:
        wd = WithdrawsDB.get(int(trans))
        if action == "QIWIPAY":
            s = qiwiAutoPay(UsersDB.get(user_id, "withdraw_data")["card"], float(wd["amount"]))
            try:
                await cb.message.answer(text=MSG["AUTOPAY_INFO"].format(s["fields"]["account"],
                                                                        s["sum"]["amount"],
                                                                        s["transaction"]["id"]))
            except:
                await cb.message.answer(text='Ошибка при автопереводе: ' + str(s["message"]))
                return

        u_deposit = UsersDB.get(user_id, "deposit")

        # Change contractor deposit
        UsersDB.update(user_id, "deposit", u_deposit - float(wd["amount"]))

        # Change transaction status
        WithdrawsDB.update_withdraw(trans, "status", "DONE")

        # Notify contractor
        await bot.send_message(chat_id=user_id, text=MSG["YOUR_WD_CONFIRMED"])

        await cb.message.delete()
    elif action == "REJECT":
        WithdrawsDB.update_withdraw(trans, "status", "REJECTED")
        await cb.message.edit_reply_markup(reply_markup=None)
        await cb.message.edit_text(text=f"🚫 Заявка <u>#{trans}</u> отклонена")
        await bot.send_message(chat_id=user_id,
                               text=f"🚫 Ваша заявка на вывод <u>#{trans}</u> отклонена!")


def qiwiAutoPay(card: str, amount: float):
    s = requests.Session()
    s.headers.update({"Accept": "application/json",
                      "authorization": f"Bearer {QIWI_TOKEN}",
                      "Content-Type": "application/json"})
    postjson = {"id": str(int(time.time() * 1000)), "sum": {"amount": 0, "currency": "643"},
                "paymentMethod": {"type": "Account", "accountId": "643"}, "fields": {"account": ""}}
    postjson['sum']['amount'] = ceil(amount)
    postjson['fields']['account'] = card
    provider_id = '21013'

    res = s.post('https://edge.qiwi.com/sinap/api/v2/terms/' + provider_id + '/payments', json=postjson)
    return res.json()
