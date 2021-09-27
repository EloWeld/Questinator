import datetime
import json
from math import ceil

import requests

from Misc.utils import notify_role, notify_role_photo
from Src import nav
from Src.config import Role, VALID_NICK_SYMBOLS, MSG, LINKS, ROLE_NAMES, VALID_ABILITY_SYMBOLS, YOOMONEY_API_URL, \
    BINKING_TOKEN, DT_FORMAT
from Middleware.database import UsersDB
from loader import bot


def getLinks(links: dict):
    links_text = ""
    for item in links.items():
        if item[0] != "CUSTOM":
            links_text += '<a href="{}">{}</a>'.format(item[1], LINKS[item[0]]) + ' | '
        else:
            for item2 in item[1]:
                links_text += '<a href="{}">{}</a>'.format(item2, LINKS["CUSTOM"]) + ' | '
    return links_text


def getSocialLinks(message: str):
    links = dict()
    for t in [x.split('\n') for x in message.split(' ')]:
        for text in t:
            if "instagram.com/" in text:
                links["INSTAGRAM"] = text
            elif "vk.com/" in text:
                links["VK"] = text
            elif "youtube.com/c/" in text:
                links["YOUTUBE"] = text
            elif "tiktok.com/@" in text:
                links["TIK-TOK"] = text
            elif "twitch.tv/" in text:
                links["TWITCH"] = text
            elif "t.me/" in text:
                links["FACEBOOK"] = text
            else:
                if "CUSTOM" not in links:
                    links["CUSTOM"] = list()
                links["CUSTOM"].append(text)
    return links


async def registerUser(user_id: int, data: dict):
    data["statuses"] = ":WAIT_REGISTER:"
    UsersDB.registerContra(user_id, data)

    await notify_role_photo(photo_id=data["photo"], role=Role.Admin.value,
                            message=MSG["NEW_CONTRA"].format(
                                data["contra_nick"],
                                data["description"],
                                getLinks(data["links"])
                            ), reply=nav.judge_contra(user_id))


def addAbility(data: dict, user_id: int):
    abils = UsersDB.get(user_id, "abilities")
    if len([ab for ab in abils["abilities"] if ab["id"] == data["ability_id"]]) == 0:
        abils["abilities"].append(dict(id=data["ability_id"],
                                       name=data["ability_desc"],
                                       price=data["ability_price"]))
    else:
        for ab in abils["abilities"]:
            if ab["id"] == data["ability_id"]:
                ab["name"] = data["ability_desc"]
                ab["price"] = data["ability_price"]

    UsersDB.update(user_id, "abilities", json.dumps(abils))


def deleteAbility(ability_id, user_id: int):
    abils = UsersDB.get(user_id, "abilities")
    for ab in abils["abilities"]:
        if ab["id"] == ability_id:
            abils["abilities"].remove(ab)
    UsersDB.update(user_id, "abilities", json.dumps(abils))


async def profile(caller_id: int, user_data):
    isMyProfile = caller_id == user_data["tgid"]
    reply = nav.my_profile_menu if isMyProfile else nav.getContraProfileMenu(user_data["tgid"])
    if isMyProfile:
        profile_text = MSG["PROFILE"].format(**dict(
            nick=user_data["contra_nick"],
            role=ROLE_NAMES[user_data["role"]],
            desc=user_data["description"],
            links=getLinks(user_data["soc_net_links"]),
            balance=str(user_data["deposit"]).replace('.', ',')
        ))
    else:
        profile_text = MSG["FOREIGN_PROFILE"].format(**dict(
            nick=user_data["contra_nick"],
            desc=user_data["description"],
            links=getLinks(user_data["soc_net_links"])
        ))

    if user_data["photo"] != "NO_PHOTO":
        await bot.send_photo(chat_id=caller_id, photo=user_data["photo"], caption=profile_text, reply_markup=reply)
    else:
        await bot.send_message(chat_id=caller_id, text=profile_text, reply_markup=reply)


async def sendQuestion(quest: dict, user_id):
    q = quest["question"]
    provider = MSG["QUESTION_F"] if "text" in q else MSG["QUESTION_NO_TEXT_F"]
    message_text = provider.format(**dict(
        q_id=quest["q_id"],
        user=UsersDB.get(quest["s_id"], "username"),
        question_text=q["text"] if "text" in q else "",
        price=quest["amount"],
        dt=datetime.datetime.fromtimestamp(float(q["date"])).strftime(DT_FORMAT)))
    if "video_note" in q or "sticker" in q:
        await bot.send_message(chat_id=user_id, text=message_text)
    else:
        q["caption"] = message_text
    await sendMedia(user_id, q, nav.judge_q(quest["q_id"]))


def getQiwiTransactionStatus(token: str, qiwi_api_url: str, amount: float, comment: str):
    p = {'rows': '15'}
    head = {'Authorization': f'Bearer {token}'}
    response = requests.get(url=qiwi_api_url, params=p, headers=head)
    status = "TRANS_NOT_FOUND"

    # Check on errors
    if response.status_code != 200:
        print(f'Error {response.status_code}! Content: {response.content}')
        return "ERROR"

    # Step by step in history to find transaction
    history = response.json()["data"]
    for trans in history:
        t_amount, t_comment, t_status = float(trans["sum"]["amount"]), str(trans['comment']), trans['status']
        if abs(ceil(t_amount) - int(amount)) < 3 and comment == t_comment:
            # Transaction found
            if t_status == "SUCCESS":
                return "SUCCESS"
            else:
                status = t_status

    return status


def getYMTransactionStatus(ym_token: str, ym_api_url: str, amount: float, comment: str):
    head = {"Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {ym_token}"}
    response = requests.post(ym_api_url, data=f'type=deposition', headers=head)
    status = "TRANS_NOT_FOUND"

    # Check on errors
    if response.status_code != 200:
        print(f'Error {response.status_code}! Content: {response.content}')
        return "ERROR"

    # Step by step in history to find transaction
    ymoperations = response.json()['operations']
    for oper in ymoperations:
        if "label" in oper and oper['label'] == comment and abs(ceil(float(oper['amount'])) - amount) < 3:
            # Transaction found
            if oper['status'] == "success":
                return "SUCCESS"
            else:
                status = str(oper['status']).upper()
        else:
            print(oper)

    return status


def getCardInfo(cardnum: str):
    result = dict(
        card=cardnum,
        bankName="Unknown bank",
        bankSite="Unknown site",
        bankCountry="Unknown country",
        bankColor="Unknown color",
    )
    binking_url = 'https://api.binking.io/form'
    p = {
        "apiKey": BINKING_TOKEN,
        "cardNumber": cardnum.replace(' ', '')[:6]
    }
    response = requests.get(url=binking_url, params=p)
    if response.status_code != 200 or response.json() is None or "bankName" not in response.json():
        print(cardnum, "Не удалось определить карту!")
    else:
        r_data = response.json()
        result["bankName"] = r_data["bankName"]
        result["bankSite"] = r_data["bankSite"]
        result["bankCountry"] = r_data["bankCountry"]
        result["bankColor"] = r_data["bankColor"]
    return result


async def sendMedia(chat_id: int, data: dict, reply=None):
    a, q = chat_id, data
    print(data)
    if "photo" in q:
        await bot.send_photo(chat_id=a, photo=q["photo"][0]["file_id"],
                             caption=q["caption"] if "caption" in q else '',
                             reply_markup=reply)
    elif "video_note" in q:
        await bot.send_video_note(chat_id=a, video_note=q["video_note"]["file_id"],
                                  duration=q["video_note"]["duration"], thumb=q["video_note"]["thumb"]["file_id"],
                                  reply_markup=reply)
    elif "animation" in q:
        await bot.send_animation(chat_id=a, animation=q["animation"]["file_id"],
                                 width=q["animation"]["width"], height=q["animation"]["height"],
                                 thumb=q["animation"]["thumb"]["file_id"], duration=q["animation"]["duration"],
                                 caption=q["caption"] if "caption" in q else '',
                                 reply_markup=reply)
    elif "audio" in q:
        await bot.send_audio(chat_id=a, audio=q["audio"]["file_id"],
                             thumb=q["audio"]["thumb"]["file_id"] if "thumb" in q["audio"] else None,
                             title=q["audio"]["title"] if "title" in q["audio"] else "Аудио-файл",
                             duration=q["audio"]["duration"],
                             caption=q["caption"] if "caption" in q else '',
                             reply_markup=reply)
    elif "document" in q:
        await bot.send_document(chat_id=a, document=q["document"]["file_id"],
                                thumb=q["document"]["thumb"]["file_id"],
                                caption=q["caption"] if "caption" in q else '',
                                reply_markup=reply)
    elif "voice" in q:
        await bot.send_voice(chat_id=a, voice=q["voice"]["file_id"], duration=q["voice"]["duration"],
                             caption=q["caption"] if "caption" in q else '',
                             reply_markup=reply)
    elif "video" in q:
        await bot.send_video(chat_id=a, video=q["video"]["file_id"],
                             width=q["video"]["width"], height=q["video"]["height"],
                             thumb=q["video"]["thumb"]["file_id"], duration=q["video"]["duration"],
                             caption=q["caption"] if "caption" in q else '',
                             reply_markup=reply)
    elif "sticker" in q:
        await bot.send_sticker(chat_id=a, sticker=q["sticker"]["file_id"],
                               reply_markup=reply)
    elif "text" in q:
        await bot.send_message(chat_id=a, text=q["caption"],
                               reply_markup=reply)
