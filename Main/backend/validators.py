from Middleware.database import UsersDB
from Src import VALID_NICK_SYMBOLS, VALID_ABILITY_SYMBOLS


def isValidNickname(nickname: str):
    validSymbols = VALID_NICK_SYMBOLS
    if 15 >= len(nickname) >= 4:
        if all(x in validSymbols for x in nickname):
            if UsersDB.getUserByContraNick(nickname) is None:
                return 0
            else:
                return -3
        else:
            return -1
    else:
        return -2


def isValidAbilityName(name: str):
    if 30 >= len(name) >= 1 and all([x in VALID_ABILITY_SYMBOLS for x in name]):
        return True
    return False


def isValidFloat(s: str):
    return s.replace('.', '', 1).isdigit()


def isValidAbilityPrice(price: str):
    if isValidFloat(price) and int(price) and 0 < int(price) < 10000:
        return True
    return False


def isValidCardNumber(card_number: str):
    return 7 < len(card_number) < 30 and all(x in "0123456789 -" for x in card_number)


def formatCardName(card_number: str):
    cn = card_number.replace(' ', '').replace('-', '')
    if len(cn) == 16:
        return f'{cn[0:4]} {cn[4:8]} {cn[8:12]} {cn[12:16]}'
    elif len(cn) > 16:
        return f'{cn[0:8]} {cn[8:999]}'
    else:
        return cn


def isValidWDAmount(amount: str):
    return amount.replace('.', '', 1).isdigit() and float(amount) >= 10
