import os
from enum import Enum

from aiogram.types import ContentType
from dotenv import load_dotenv

load_dotenv()

# ======================== (CONSTANTS) ==========================
BOT_NAME = "Questinator"
BOT_TOKEN = os.getenv('TOKEN')
PROFILE_PIC = os.getenv('PROFILE_PIC')
GLOBAL_FEE = int(os.getenv('GLOBAL_FEE'))
VALID_ABILITY_SYMBOLS = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZzАаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя0123456789-=_+`~!@#$%^&*(),.<>;\':\" "
VALID_NICK_SYMBOLS = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789-_."
TOP_LIMIT = 10
DT_FORMAT = "%H:%M %d.%m.%Y"
ALLOW_CONTENT_TYPES = [ContentType.TEXT, ContentType.DOCUMENT, ContentType.VIDEO, ContentType.VOICE, ContentType.AUDIO,
                       ContentType.VIDEO_NOTE, ContentType.ANIMATION, ContentType.PHOTO]

# ======================== (PAYMENT) ==========================
QIWI_NUMBER = os.getenv('QIWI_NUMBER')
QIWI_TOKEN = os.getenv('QIWI_TOKEN')
BINKING_TOKEN = os.getenv('BINKING_TOKEN')

YOOMONEY_ACCESS_TOKEN = os.getenv('YOOMONEY_ACCESS_TOKEN')
YOOMONEY = os.getenv('YOOMONEY')

QIWI_API_URL = f'https://edge.qiwi.com/payment-history/v1/persons/{QIWI_NUMBER}/payments'
YOOMONEY_API_URL = 'https://yoomoney.ru/api/operation-history'


def getQiwiUrl(number: str, amount: float, comment: str):
    return "https://qiwi.com/payment/form/99" \
           f"?extra['account']={number}" \
           f"&amountInteger={int(amount)}" \
           f"&amountFraction={str(amount % 1)[2:5]}" \
           f"&extra['comment']={comment}" \
           f"&currency={643}" \
           "&blocked[0]=account" \
           "&blocked[1]=comment" \
           "&blocked[2]=sum "


# ======================== (DATABASE) ==========================
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_CREDS = dict(USER=DB_USER,
                PASSWORD=DB_PASS,
                HOST="chunee.db.elephantsql.com"
                )


# ======================== (ROLES) ==========================
class Role(Enum):
    Admin = 2
    User = 0
    Guest = -1


ROLE_NAMES = {
    Role.Admin.value: "Админ",
    Role.User.value: "Исполнитель",
    Role.Guest.value: "Гость",
}

# ======================== (DICTS) ==========================
LINKS = {
    "INSTAGRAM": "📸 Insta",
    "TIK-TOK": "🎵 Tik-tok",
    "YOUTUBE": "▶ YouTube",
    "VK": "🐶 VK",
    "TWITCH": "☁ Twitch",
    "FACEBOOK": "👾 Facebook",
    "CUSTOM": "✨ LINK",
}

CMDS = dict(
    CHANGE_FEE="change_fee",
    ADD_ADMIN="add_admin",
    START="start",
    PROFILE="profile",
    ADMIN_P="admin_panel",
    REGISTER="register",
)

NAV = dict(
    # === MAIN MENU === #
    ABOUT="🗿 Сервис",
    REGISTER="⭕ Зарегистрироваться",
    CONTRAS="🔍 Исполнители",
    PROFILE="🎩 Профиль",
    ADMIN_P="🎟 Админка",

    # === ADMIN === #
    CHANGE_GLOBAL_FEE="💱 Изменить размер комиссии",
    AP_REG_REQUESTS="🀄 Запросы на регистрацию",
    AP_WITHDRAW_REQUESTS="🀄 Запросы на вывод",
    ACCEPT_CONTRA="🟢 Подтвердить",
    REJECT_CONTRA="🔴 Отклонить",
    WD_IGNORE="⭕ Игнорить",
    WD_WIDTHDRAW="💳 Вывести",
    SEND_MSG="☁ Рассылка",
    SEND_MSG_C="☁ Сообщение исполнителям",
    SEND_MSG_ALL="☁ Сообщение всем",

    # === PROFILE === #
    MY_ABILITIES="📜 Опции",
    MY_QUESTIONS="📜 Мои вопросы",
    ABILITY_VIEW="🕳 •{} — {} ₽",
    EDIT_PROFILE="🙍‍♂️ Изменить профиль",
    WITHDRAW="💳 Вывести средства",

    # === PROFILE EDIT === #
    SKIP="⏭ Пропустить",
    KEEP="🎱 Оставить текущее",
    ADD_ABILITY="➕ Добавить опцию",
    DELETE_ABILITY="➕ Удалить опцию",

    # === OTHER === #
    PROFILE_BY_NICK="🔍 Найти по нику",
    CANCEL="🚫 Отменить",
    IL_BACK="⏪ Назад",
    BACK="⏪ Назад",

    # === QUESTION === #
    Q_ANSWER="✍ Ответить",
    Q_IGNORE="⭕Игнорить",

    # === QUESTION ASK MENU === #
    QA_ADD_CAPTION="✒ Добавить",
    QA_NO_CAPTION="✒ Не подписывать",
    QA_CHANGE="✒ Изменить",
    QA_CONFIRM="👌 Подтвердить",
    QA_CANCEL="✖ Отменить",

    # === PAYMENT === #
    PAYMENT_CHECK="🔎 Проверить оплату",
    CONTRA_ABILITIES="📜 Опции исполнителя",

)

MSG = dict(
    # === MOTO === #
    MOTO="Привет! Добро пожаловать в Квестинатор! "
         "Этот бот - целая социальная сеть по задаванию вопросов и ответу на них!",
    ABOUT="Информация о сервере:\n"
          "• Очень круто, очень-очень круто",
    RESTART_MOTO="Бот перезапущен",
    BROADCAST="☁ Рассылка сообщений\n"
              "———————————————\n"
              "{}\n"
              "———————————————\n",

    # === ADMIN === #
    AUTOPAY_INFO="🥝🦾💳Был осуществлён автоматический перевод на карту <b>{}</b>, на сумму <b>{}Р</b>.\n"
                 "Транзакция: {}",
    WAITING_WD_REQUEST="<u>{}</u> хочет вывести <u>{}</u> на карту ниже:\n"
                       "———————————————\n"
                       "{}\n"
                       "———————————————\n",
    YOUR_WD_CONFIRMED="✅ Заявка на вывод одобрена!",
    NO_REG_REQUESTS="⭕ Нет запросов на регистрацию",
    NO_WD_REQUESTS="⭕ Нет запросов на вывод",

    NEW_CONTRA="⭕ Новая заявка на профиль исполнителя!\n"
               "Профиль пользователя: <b><u>{}</u></b>\n"
               "Описание: <b>{}</b>\n"
               "Соц.сети: \n<b><i>{}</i></b>\n",

    # === WITHDRAW === #
    WITHDRAW_MOTO="Итак, вывод, самое интересное",
    WITHDRAW_ENTER_AMOUNT="Введите сумму для вывода(не менее 10Р)",
    NEW_CARD_MOTO="Введите номер карты для вывода",
    CARD_ADDED="✅ Карта успешно привязана!",
    BANK_INFO="ℹ Информация о банке: \n"
              "💳 Карта: {card}\n"
              "🏦 Банк: {bankName} \n"
              "🔗 Сайт банка: {bankSite} \n"
              "🏳 Страна: {bankCountry} \n",
    INVALID_CARD="Неправильный номер карты!",
    UNKNOWN_CARD_BANK="Неизвестный банк номера карты!",

    # === QUESTION ASK === #
    ASK_QUESTION_MOTO="Напишите свой вопрос. Вы можете прикрепить файл или фото",
    ASK_QUESTION_CAPTION="Добавиь подпись к вопросу? Если да, то напиши её ниже",
    ASK_QUESTION_PREVIEW_NO_CAP="Хорошо, подписи не будет.\n "
                                "Теперь выберите опцию в меню",
    ASK_QUESTION_PREVIEW="Вот ваш вопрос: \n"
                         "==========\n"
                         "{}\n"
                         "==========\n"
                         "Выберите опцию в меню",
    Q_CANCEL="🚫 Вопрос отменён 🚫",

    # === QUESTION === #
    NEW_QUESTION_F="У вас новый вопрос от пользователя {}!",
    QUESTION_NO_TEXT_F="Вопрос #{q_id} от пользователя <u>@{user}</u> на <b>{price}</b> ₽\n"
                       "Дата вопроса: <b>{dt}</b>\n",
    QUESTION_F="Вопрос #{q_id} от пользователя <u>@{user}</u> на <b>{price}</b> ₽\n"
               "Дата вопроса: <b>{dt}</b>\n"
               "———————————————\n"
               "{question_text}\n"
               "———————————————\n",
    A_CANCEL="⭕ Вопрос отложен",
    QUESTIONS_DONE="🌟 Вы ответили на все вопросы!",
    QUESTIONS_PROCESS="🌟 Вопросов осталось всего {}!",
    QUESTION_ANSWERED="Отличный ответ! Я бы лучше и не сказал!\n"
                      "Средства уже перечесляются на ваш внутриботовый счёт\n"
                      "Комиссия: {}%",

    # === ANSWER === #
    ANSWER_NO_TEXT_F="Ура! <b>{user}</b> ответил на ваш вопрос <u>#{q_id}</u> за <b>{price}</b> ₽\n",
    ANSWER_F="Ура! <b>{user}</b> ответил на ваш вопрос <u>#{q_id}</u> за <b>{price}</b> ₽\n"
             "———————————————\n"
             "{answer}\n"
             "———————————————\n",

    # === PAYMENT === #
    PAYMENT_SUCCESS="⭕ Статус платежа: <b><u>✔ Средства успешно переведены ✔</u></b>",
    PAYMENT_ERROR="⭕ Статус платежа: <b><u>❌ ВНУТРЕННЯЯ ОШИБКА ❌</u></b>\n"
                  "Обратитесь в тех.поддержку бота",
    PAYMENT_TNF="⭕ Статус платежа: <b><u>⌛ Ожидание платежа ⌛</u></b>\n",
    PAYMENT_MAIN="Выберите платежную систему:",
    PAYMENT_CANCELED="Оплата отменена",
    QIWI_PAYMENT="Оплата по QIWI",
    YOOMONEY_PAYMENT="Оплата по YOOMONEY",

    # === PROFILE === #
    DELETE_ABILITY="🚮 Опция удалена",
    PROFILE="✨✨✨ Твой профиль ✨✨✨\n\n"
            "📜 Описание: <b>{desc}</b>\n"
            "🔔 Соц.сети: \n"
            "<b><i>{links}</i></b>\n\n"
            "Права: <b>{nick}</b> — <b>{role}</b>\n"
            "Баланс: <b><u>{balance}</u></b> ₽\n",
    FOREIGN_PROFILE="Профиль пользователя: <b><u>{nick}</u></b>\n"
                    "📜 Описание: <b>{desc}</b>\n"
                    "🔔 Соц.сети: \n"
                    "<b><i>{links}</i></b>\n",
    NEW_ABILITY_DESC="📄 Опиши опцию кратко\n"
                     "(Максимум 30 символов)",
    NEW_ABILITY_PRICE="💲 Стоимость\n"
                      "(Максимум 10000₽)",

    # === PROFILE FIND === #
    PROFILE_BY_NICK="Введи ник исполнителя",
    WRONG_PROFILE="Нет такого пользователя <b>{}</b>!",

    # === REGISTRATION === #
    R_REGISTER="Отлично! Начинаем регистрацию.",
    R_EDIT_PROFILE="Хорошо, давай перезаполним твою анкету",
    R_DESC="Введи описание своего профиля",
    R_PHOTO="Пришли мне фото для профиля",
    YOUR_REG_CONFIRMED="Ваша заявка на исполнителя одобрена!\n"
                       "Чтобы активировать новые функции - напиши /start",
    YOUR_REG_REJECTED="Ваша заявка на исполнителя отклонена!\n",
    R_SN_LINKS="Пришли мне ссылки на твои соц. сети, я их отформатирую\n"
               "(Отправляй через пробел! Или через перенос строки)",
    R_NICK="Введи своё имя исполнтеля(никнейм), по которому другие пользователи будут находить тебя.\n"
           "• Латиница\n"
           "• От 4 до 15 символов\n"
           "• Цифры/Дэш/Дефис",
    R_NICK_1="Ник слишком короткий/длинный!\nВведи ещё раз, соблюдая правила выше",
    R_NICK_2="Недопустимые символы в нике!\nВведи ещё раз, соблюдая правила выше",
    R_NICK_3="Такой пользователь уже зарегистрирован!\nПридумай другой ник",
    R_FINISH="✅ Круто, регистрация завершена и отправлена на модерацию!",
    EDIT_FINISH="✅ Профиль был изменён и отправлена на модерацию!",
)

MSGE = Enum('MSG', MSG)
