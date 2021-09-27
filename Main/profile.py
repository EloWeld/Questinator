from random import randrange

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import *
from aiogram.types import *

from Main.backend import deleteAbility, profile, addAbility
from Main.backend.validators import isValidAbilityName, isValidAbilityPrice
from Middleware.database import UsersDB
from Misc.filters import IsUser, IsPrivate
from Src import nav
from Src.states import Registration, Ability, Question
from Src.config import NAV, MSG, CMDS
from loader import dp, bot


# ==================== CALLBACKS ================== #
@dp.callback_query_handler(lambda x: "ASK_ABILITY" in x.data)
async def cbAskAbility(cb: CallbackQuery):
    _, contra_id, ab_id = cb.data.split(':')

    abilities = UsersDB.get(int(contra_id), "abilities")["abilities"]
    abilitiesId = [x for x in abilities if int(ab_id) == int(x["id"])]
    if len(abilitiesId) == 0:
        await cb.message.answer(text='Ошибка! Нет такой опции!')
        await cb.answer()
        return

    ability = abilitiesId[0]

    await cb.message.answer(text=MSG["ASK_QUESTION_MOTO"], reply_markup=nav.cancel_q_menu)
    await Question.Main.set()
    await dp.get_current().current_state().update_data(ability=ability,
                                                       r_id=contra_id)

    await cb.answer()


@dp.callback_query_handler(lambda x: "CONTRA_ABILITIES" in x.data)
async def cbContraAbilities(cb: CallbackQuery):
    user_id = int(cb.data.split(':')[1])
    abilities = UsersDB.get(user_id, "abilities")
    await cb.message.edit_reply_markup(nav.getContraAbilitiesMenu(abilities, user_id))
    await cb.answer()


@dp.callback_query_handler(lambda x: "ADD_ABILITY" in x.data)
async def cbAddAbility(cb: CallbackQuery):
    await cb.message.answer(text=MSG["NEW_ABILITY_DESC"], reply_markup=ReplyKeyboardRemove())
    await Ability.Description.set()
    await dp.get_current().current_state().update_data(ability_id=str(hash(randrange(1, 99999999))))
    await cb.answer()


@dp.callback_query_handler(lambda x: "EDIT_ABILITY" in x.data)
async def cbEditAbility(cb: CallbackQuery):
    ability_id = cb.data.split(":")[2]
    abilities = UsersDB.get(cb.from_user.id, "abilities")
    if ability_id in [x["id"] for x in abilities["abilities"]]:
        await cb.message.answer(text=MSG["NEW_ABILITY_DESC"], reply_markup=nav.ability_edit_menu)
        await Ability.Description.set()
        await dp.get_current().current_state().update_data(ability_id=str(ability_id))
    else:
        await cb.message.answer(text="INVALID ABILITY NAME!")
    await cb.answer()


@dp.callback_query_handler(lambda x: "MY_ABILITIES" in x.data)
async def cbMyAbilities(cb: CallbackQuery):
    abilities = UsersDB.get(cb.from_user.id, "abilities")
    await cb.message.edit_reply_markup(nav.getMyAbilitiesMenu(abilities, cb.from_user.id))

    await cb.answer()


@dp.callback_query_handler(lambda x: "BACK:" in x.data)
async def cbBackInline(cb: CallbackQuery):
    id_ = int(cb.data.split(':')[1])
    if cb.from_user.id == id_:
        await cb.message.edit_reply_markup(nav.my_profile_menu)
    else:
        await cb.message.edit_reply_markup(nav.getContraProfileMenu(id_))

    await cb.answer()


@dp.callback_query_handler(lambda x: "EDIT_PROFILE" in x.data)
async def cbEditProfile(cb: CallbackQuery):
    await cb.message.answer(text=MSG["R_EDIT_PROFILE"], reply_markup=ReplyKeyboardRemove())
    await cb.message.answer(text=MSG["R_DESC"], reply_markup=nav.keep_curr)
    await Registration.Description.set()

    user_data = UsersDB.getUser(cb.from_user.id)
    await dp.get_current().current_state().update_data(is_edit=True, u_data=user_data)

    await cb.answer()


# ==================== MESSAGES ================== #
@dp.message_handler(IsPrivate(), Text(NAV["DELETE_ABILITY"]), state=Ability.Description)
async def stateAbilityDescDelete(message: Message, state: FSMContext):
    q = str(message.text).replace('<', '').replace('>', '')
    await state.update_data(ability_desc=q)

    deleteAbility((await state.get_data())["ability_id"], message.from_user.id)
    await message.answer(text=MSG["DELETE_ABILITY"], reply_markup=nav.startMenu(message.from_user.id))
    await profile(message.from_user.id, UsersDB.getUser(message.from_user.id))
    await state.finish()


@dp.message_handler(IsPrivate(), state=Ability.Description)
async def stateAbilityDesc(message: Message, state: FSMContext):
    q = str(message.text).replace('<', '').replace('>', '')
    if not isValidAbilityName(q):
        await message.answer(text='Не корректно! Ещё раз!')
        await Ability.Description.set()
        return
    await state.update_data(ability_desc=q)

    await message.answer(text=MSG["NEW_ABILITY_PRICE"])
    await Ability.Price.set()


@dp.message_handler(IsPrivate(), state=Ability.Price)
async def stateAbilityDesc(message: Message, state: FSMContext):
    if not isValidAbilityPrice(message.text):
        await message.answer(text='Не корректно! Ещё раз!')
        await Ability.Price.set()
        return

    await state.update_data(ability_price=int(message.text))
    data = await state.get_data()
    addAbility(data, message.from_user.id)

    await message.answer(text=f'Опция добавлена/изменена!',
                         reply_markup=nav.startMenu(message.from_user.id))
    await profile(message.from_user.id, UsersDB.getUser(message.from_user.id))
    await state.finish()


@dp.message_handler(IsPrivate(), commands=[CMDS["PROFILE"]])
async def commandProfile(message: Message, command):
    if ' ' in message.text:
        nick = command.args.split(' ')[0]
        await openProfileByNick(message.from_user.id, nick)
    else:
        await txtMyProfile(message)


async def openProfileByNick(caller_id: int, nick: str):
    user_data = UsersDB.getUserByContraNick(nick)
    if user_data is None:
        await bot.send_message(chat_id=caller_id,
                               text=MSG["WRONG_PROFILE"].format(nick),
                               reply_markup=nav.startMenu(caller_id))
        return False
    await profile(caller_id, user_data)
    return True


@dp.message_handler(IsUser(), Text(NAV["PROFILE"]))
async def txtMyProfile(message: Message):
    user_data = UsersDB.getUser(message.from_user.id)

    await profile(message.from_user.id, user_data)
