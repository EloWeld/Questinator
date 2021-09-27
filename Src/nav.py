from aiogram.types import ReplyKeyboardMarkup as Menu, InlineKeyboardMarkup as IlMenu, \
    InlineKeyboardButton as IlBtn
from aiogram.types import KeyboardButton as Btn

# region =================== DEFAULT MENUs ================================
from Src import NAV, Role

guest_menu = Menu(resize_keyboard=True, one_time_keyboard=True, keyboard=[
    [
        Btn(NAV["CONTRAS"]),
        Btn(NAV["REGISTER"]),
        Btn(NAV["ABOUT"]),
    ]
])

user_menu = Menu(resize_keyboard=True, one_time_keyboard=True, keyboard=[
    [
        Btn(NAV["CONTRAS"]),
        Btn(NAV["MY_QUESTIONS"]),
        Btn(NAV["PROFILE"]),
        Btn(NAV["ABOUT"]),
    ]
])

admin_menu = Menu(resize_keyboard=True, one_time_keyboard=True, keyboard=[
    [
        Btn(NAV["CONTRAS"]),
        Btn(NAV["PROFILE"]),
        Btn(NAV["ABOUT"]),
    ],
    [
        Btn(NAV["MY_QUESTIONS"]),
        Btn(NAV["ADMIN_P"]),
    ],
    [
        Btn(NAV["SEND_MSG"]),
    ],
])

broadcast_menu = Menu(resize_keyboard=True, one_time_keyboard=True, keyboard=[
    [
        Btn(NAV["SEND_MSG_C"]),
        Btn(NAV["SEND_MSG_ALL"]),
    ],
])

skip_menu = Menu(resize_keyboard=True, one_time_keyboard=True, keyboard=[
    [
        Btn(NAV["SKIP"]),
    ]
])

keep_curr = Menu(resize_keyboard=True, one_time_keyboard=True, keyboard=[
    [
        Btn(NAV["KEEP"]),
    ]
])

cancel_q_menu = Menu(resize_keyboard=True, one_time_keyboard=True, keyboard=[
    [
        Btn(NAV["CANCEL"]),
    ]
])

ability_edit_menu = Menu(resize_keyboard=True, one_time_keyboard=True, keyboard=[
    [
        Btn(NAV["DELETE_ABILITY"]),
        Btn(NAV["KEEP"]),
    ]
])

admin_panel = Menu(resize_keyboard=True, keyboard=[
    [
        Btn(NAV["AP_REG_REQUESTS"]),
        Btn(NAV["AP_WITHDRAW_REQUESTS"]),
    ],
    [
        Btn(NAV["CHANGE_GLOBAL_FEE"]),
        Btn(NAV["BACK"]),
    ],
])

question_add_caption = Menu(resize_keyboard=True, one_time_keyboard=True, keyboard=[
    [
        Btn(NAV["QA_NO_CAPTION"]),
    ],
])

confirm_menu = Menu(resize_keyboard=True, one_time_keyboard=True, keyboard=[
    [
        Btn(NAV["QA_CHANGE"]),
        Btn(NAV["QA_CANCEL"]),
        Btn(NAV["QA_CONFIRM"]),
    ],
])


def startMenu(user_id: int):
    menu = Menu(resize_keyboard=True)
    from Middleware.database import UsersDB
    role = UsersDB.get(user_id, "role")
    if role == Role.Guest.value:
        menu.keyboard = guest_menu.keyboard
    if role == Role.User.value:
        menu.keyboard = user_menu.keyboard
    if role == Role.Admin.value:
        menu.keyboard = admin_menu.keyboard
    return menu


# endregion

# region =================== INLINE MENUs ================================
my_profile_menu = IlMenu(row_width=3, inline_keyboard=[
    [
        IlBtn(NAV["MY_ABILITIES"], callback_data='MY_ABILITIES'),
    ],
    [
        IlBtn(NAV["EDIT_PROFILE"], callback_data='EDIT_PROFILE'),
    ],
    [
        IlBtn(NAV["WITHDRAW"], callback_data='WITHDRAW'),
    ],
    [
        IlBtn(NAV["EDIT_CARD"], callback_data='EDIT_CARD'),
    ],
])


def getContraProfileMenu(user_id: int):
    contra_profile_menu = IlMenu(row_width=3, inline_keyboard=[
        [
            IlBtn(NAV["CONTRA_ABILITIES"], callback_data=f'CONTRA_ABILITIES:{user_id}'),
        ],
    ])
    return contra_profile_menu


def getMyAbilitiesMenu(abilities: dict, user_id: int):
    reply = IlMenu(row_width=3, inline_keyboard=[
        [
            IlBtn(text=NAV["ADD_ABILITY"], callback_data=f'ADD_ABILITY:{user_id}'),
            IlBtn(text=NAV["IL_BACK"], callback_data=f'BACK:{user_id}'),
        ]
    ])
    abils_s = sorted(abilities["abilities"], key=lambda x: float(x["price"]))
    for ab in abils_s:
        reply.inline_keyboard.append([IlBtn(text=NAV["ABILITY_VIEW"].format(ab["name"], ab["price"]),
                                            callback_data=f'EDIT_ABILITY:{user_id}:{ab["id"]}')])
    return reply


def getContraAbilitiesMenu(abilities: dict, user_id: int):
    reply = IlMenu(row_width=3, inline_keyboard=[
        [IlBtn(text=NAV["IL_BACK"], callback_data=f'BACK:{user_id}')]
    ])
    abils_s = sorted(abilities["abilities"], key=lambda x: float(x["price"]))
    for ab in abils_s:
        reply.inline_keyboard.append([IlBtn(text=NAV["ABILITY_VIEW"].format(ab["name"], ab["price"]),
                                            callback_data=f'ASK_ABILITY:{user_id}:{ab["id"]}')])
    return reply


def judge_contra(user_id):
    reply = IlMenu(row_width=3, one_time_keyboard=True, inline_keyboard=[
        [
            IlBtn(NAV["ACCEPT_CONTRA"], callback_data=f'JUDGE_CONTRA:ACCEPT:{user_id}'),
            IlBtn(NAV["REJECT_CONTRA"], callback_data=f'JUDGE_CONTRA:REJECT:{user_id}'),
        ],
    ])
    return reply


def judge_q(q_id):
    reply = IlMenu(row_width=3, one_time_keyboard=True, inline_keyboard=[
        [
            IlBtn(NAV["Q_ANSWER"], callback_data=f'JUDGE_Q:ANSWER:{q_id}'),
        ],
    ])
    return reply


def judge_wd(user_id, trans):
    reply = IlMenu(row_width=3, inline_keyboard=[
        [
            IlBtn(NAV["WD_WIDTHDRAW"], callback_data=f'JUDGE_WD:WITHDRAW:{user_id}:{trans}'),
            IlBtn("🥝 Автоперевод", callback_data=f'JUDGE_WD:QIWIPAY:{user_id}:{trans}'),
            IlBtn(NAV["WD_REJECT"], callback_data=f'JUDGE_WD:REJECT:{user_id}:{trans}'),
        ],
    ])
    return reply


def contracts_menu(contras: list):
    reply = IlMenu(row_width=3,
                   inline_keyboard=[
                       [IlBtn(contra, callback_data=f'CONTRA_PROFILE:{contra}')]
                       for contra in contras
                   ])
    reply.inline_keyboard.append([IlBtn(NAV["PROFILE_BY_NICK"], callback_data=NAV["PROFILE_BY_NICK"])])
    return reply


# endregion

# region =================== PAYMENT MENUs ================================

ability_payment_menu = IlMenu(row_width=3, inline_keyboard=[
    [
        IlBtn(text='QIWI | Карта', callback_data='PAYMENT:QIWI'),
        IlBtn(text='Юмани | Карта', callback_data='PAYMENT:YOOMONEY'),
    ],
    [
        IlBtn(text=NAV["CANCEL"], callback_data='PAYMENT:CANCEL')
    ],
])


def payment_qiwi_menu(redirected_url: str):
    return IlMenu(row_width=3, inline_keyboard=[
        [
            IlBtn(text='🥝 Оплатить', url=redirected_url),
            IlBtn(text=NAV["PAYMENT_CHECK"], callback_data='PAYMENT:QIWI:CHECK')
        ],
        [
            IlBtn(text=NAV["CANCEL"], callback_data='PAYMENT:CANCEL')
        ],
        [
            IlBtn(text=NAV["IL_BACK"], callback_data='PAYMENT:BACK')
        ]
    ])


def payment_yoomoney_menu(redirected_url: str):
    return IlMenu(row_width=3, inline_keyboard=[
        [
            IlBtn(text='💳 Оплатить', url=redirected_url),
            IlBtn(text=NAV["PAYMENT_CHECK"], callback_data='PAYMENT:YOOMONEY:CHECK')
        ],
        [
            IlBtn(text=NAV["CANCEL"], callback_data='PAYMENT:CANCEL')
        ],
        [
            IlBtn(text=NAV["IL_BACK"], callback_data='PAYMENT:BACK')
        ]
    ])

# endregion
