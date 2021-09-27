from aiogram.dispatcher.filters.state import StatesGroup, State


class Registration(StatesGroup):
    Description = State()
    Photo = State()
    Links = State()
    ContraName = State()


class ProfileByNick(StatesGroup):
    Nick = State()


class Ability(StatesGroup):
    Description = State()
    Price = State()


class Payment(StatesGroup):
    Main = State()
    Qiwi = State()
    Yoomoney = State()
    Widthdraw = State()
    NewCard = State()


class Question(StatesGroup):
    Main = State()
    Confirm = State()
    ConfirmText = State()
    Answer = State()


class AdminPanel(StatesGroup):
    Fee = State()
    Broadcast = State()
