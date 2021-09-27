from datetime import datetime

from Middleware.database import UsersDB
from loader import bot


# Notify Admins/Moders/Other
async def notify_role(role, message: str, reply=None):
    for user in [x["tgid"] for x in UsersDB.allUsers() if x["role"] == role]:
        await bot.send_message(chat_id=user, text=message, reply_markup=reply)


async def notify_role_photo(photo_id, role, message: str, reply=None):
    for user in [x["tgid"] for x in UsersDB.allUsers() if x["role"] == role]:
        try:
            s = (await bot.get_file("photo_id")).file_id
            await bot.send_photo(photo=photo_id,
                                 chat_id=user,
                                 caption=message,
                                 reply_markup=reply)
        except:
            await bot.send_message(chat_id=user,
                                 text=message,
                                 reply_markup=reply)
