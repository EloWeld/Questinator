import json
import os

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import *
from aiogram.types import *

from Main import nav, Role, profile, sendMedia, sendQuestion
from Middleware.database import UsersDB, QuestDB
from Misc.filters import IsGuest, IsPrivate, IsUser
from Src.config import NAV, MSG, TOP_LIMIT, GLOBAL_FEE
from Src.states import ProfileByNick, Question
from loader import dp, bot


# ==================== CALLBACKS ================== #
@dp.callback_query_handler(lambda x: NAV["PROFILE_BY_NICK"] in x.data)
async def cbProfileByNicj(cb: CallbackQuery):
    await cb.message.answer(text=MSG["PROFILE_BY_NICK"], reply_markup=ReplyKeyboardRemove())
    await ProfileByNick.Nick.set()

    await cb.answer()


@dp.callback_query_handler(lambda x: 'JUDGE_Q:ANSWER:' in x.data)
async def cbProfileByNicj(cb: CallbackQuery):
    q_id = cb.data[15:]
    await cb.message.answer(text=f"Введите ответ на вопрос <u>{q_id}</u>", reply_markup=nav.cancel_q_menu)
    await Question.Answer.set()
    await dp.get_current().current_state().update_data(q_id=q_id)
    await cb.answer()
    await cb.message.delete()


@dp.callback_query_handler(lambda x: 'CONTRA_PROFILE:' in x.data)
async def cbContraProfile(cb: CallbackQuery):
    contra_nick = cb.data.split(':')[1]
    print(contra_nick)
    contra_data = UsersDB.getUserByContraNick(contra_nick)
    await cb.answer()
    await profile(cb.from_user.id, contra_data)


# ==================== MESSAGES ================== #

@dp.message_handler(IsPrivate(), state=Question.Answer, content_types=[ContentType.ANY])
async def stateAnswerContras(message: Message, state: FSMContext):
    if message.text and message.text == NAV["CANCEL"]:
        await message.answer(text=MSG["A_CANCEL"], reply_markup=nav.startMenu(message.from_user.id))
        await state.finish()
        return

    q_id = (await state.get_data())["q_id"]
    await state.finish()

    # Answer to contractor
    custom_fee = UsersDB.get(message.from_user.id, "custom_fee")
    total_fee = GLOBAL_FEE if custom_fee == -1 else custom_fee
    await message.answer(MSG["QUESTION_ANSWERED"].format(total_fee),
                         reply_markup=nav.startMenu(message.from_user.id))
    contra_quests = QuestDB.activeContraQuests(message.from_user.id)
    remained = MSG["QUESTIONS_DONE"] if len(contra_quests) == 0 else \
        MSG["QUESTIONS_PROCESS"].format(len(contra_quests))
    await message.answer(text=remained, reply_markup=nav.startMenu(message.from_user.id))

    # Update question in db
    QuestDB.update_questions(q_id, dict(q_answer=message.as_json(),
                                        status="ANSWERED"))
    q_db = QuestDB.questByID(q_id)

    # Increase deposit
    c_deposit = UsersDB.get(q_db["r_id"], "deposit")
    UsersDB.update(q_db["r_id"], "deposit", c_deposit + q_db["amount"] * (1 - total_fee / 100))

    # Answer to sender
    contra_nick = UsersDB.get(q_db["r_id"], "contra_nick")
    answer = q_db["q_answer"]
    provider = "ANSWER_F" if "text" in answer else "ANSWER_NO_TEXT_F"
    message_text = MSG[provider].format(**dict(
        q_id=q_id,
        answer=answer["text"] if "text" in answer else "",
        price=q_db["amount"],
        user=contra_nick
    ))
    if "video_note" in answer or "sticker" in answer:
        await bot.send_message(chat_id=q_db["s_id"], text=message_text)
    else:
        answer["caption"] = message_text
    await sendMedia(q_db["s_id"], answer)


@dp.message_handler(IsPrivate(), Text(NAV["CONTRAS"]))
async def txtContras(message: Message):
    contras_s = UsersDB.allUsers()
    contras_s = sorted(contras_s, key=lambda x: float(x["deposit"]), reverse=True)
    contras = [x["contra_nick"] for x in contras_s if x["role"] == Role.User.value][:TOP_LIMIT]
    txt = '🎩 Топ исполнителей:\n'
    """txt += '\n'.join(['• <a href="https://t.me/{0}?start={1}"><b>{2}</b></a>'.format("minusaw_bot",
                                                                                     x["contra_nick"],
                                                                                     x["contra_nick"])
                      for x in UsersDB.allUsers() if x["role"] == Role.User.value]
                     )"""

    await message.answer(text=txt, reply_markup=nav.contracts_menu(contras))


@dp.message_handler(IsUser(), Text(NAV["MY_QUESTIONS"]))
async def txtMyActiveQuestions(message: Message):
    quests = QuestDB.activeContraQuests(message.from_user.id)
    if len(quests) == 0:
        await message.answer(text='📪 У вас нет новых вопросов',
                             reply_markup=nav.startMenu(message.from_user.id))
        return

    for quest in quests:
        await sendQuestion(quest, message.from_user.id)


@dp.message_handler(IsPrivate(), state=ProfileByNick.Nick)
async def txtContrasPBN(message: Message, state: FSMContext):
    username_test = message.text
    user_data = UsersDB.getUserByContraNick(username_test)
    if user_data is None:
        await message.answer(text=MSG["WRONG_PROFILE"].format(username_test),
                             reply_markup=nav.startMenu(message.from_user.id))
        await state.finish()
        return
    await profile(message.from_user.id, user_data)
    await message.answer(text='=======', reply_markup=nav.startMenu(message.from_user.id))
    await state.finish()
