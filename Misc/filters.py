from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from Middleware.database import UsersDB
from Src import Role


class IsAdmin(BoundFilter):
    async def check(self, message: types.Message, *args) -> bool:
        is_private = await IsPrivate().check(message)
        admin = message.from_user.id in [x["tgid"] for x in UsersDB.all_admins()]
        return admin and is_private


class IsGuest(BoundFilter):
    async def check(self, message: types.Message, *args) -> bool:
        is_private = await IsPrivate().check(message)
        reg = UsersDB.get(message.from_user.id, "role") == Role.Guest.value
        return reg and is_private


class IsUser(BoundFilter):
    async def check(self, message: types.Message, *args) -> bool:
        is_private = await IsPrivate().check(message)
        reg = UsersDB.get(message.from_user.id, "role") != Role.Guest.value
        return reg and is_private


class IsPrivate(BoundFilter):
    async def check(self, message: types.Message):
        return message.chat.type == types.ChatType.PRIVATE