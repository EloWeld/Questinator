import asyncio

from Misc.utils import notify_role
from Src import Role, BOT_NAME, nav
from loader import dp, bot
from Main import main_handlers
from Main import contras

minute_msgs = False
is_parsing = 0
is_posting = 0


# ============= TIMER ============= #
async def minute_timer():
    global minute_msgs
    minute_msgs = False


async def scheduleTask(interval, task):
    while True:
        await task()
        await asyncio.sleep(interval)


# ============= STARTUP ============= #
async def onBotStartup(dispatcher):
    print(f"{BOT_NAME} started")

    # Notify Admins
    await notify_role(Role.Admin.value, f"💫 {BOT_NAME} strated!")


async def onBotShutdown(dp):
    # Notify Admins
    await notify_role(Role.Admin.value, f"🛑 {BOT_NAME} disabled!")

    # Close storages
    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == "__main__":
    from aiogram import executor

    executor.start_polling(dp, on_startup=onBotStartup,
                           on_shutdown=onBotShutdown)