from botlogic.settings import bot, Secrets
from botlogic.views import start_bot_msg, stop_bot_msg, bot_banned_msg, bot_unbanned_msg


# TODO: Необходимо реализовать удаление пробелов в списках idmin_id и manager_id

async def start_bot() -> None:
    admin_list: list = Secrets.admin_id.split(",")
    for _admin in admin_list:
        await bot.send_message(_admin, start_bot_msg())


async def stop_bot() -> None:
    admin_list: list = Secrets.admin_id.split(",")
    for _admin in admin_list:
        await bot.send_message(_admin, stop_bot_msg())


async def bot_banned() -> str:
    admin_list: list = Secrets.admin_id.split(",")
    for _admin in admin_list:
        await bot.send_message(_admin, bot_banned_msg())
    return bot_banned_msg()


async def bot_unbanned() -> str:
    admin_list: list = Secrets.admin_id.split(",")
    for _admin in admin_list:
        await bot.send_message(_admin, bot_unbanned_msg())
    return bot_unbanned_msg()
