from aiogram.filters import Command, ChatMemberUpdatedFilter, KICKED, MEMBER
from aiogram.types import Message, ChatMemberUpdated
from botlogic.settings import dp
from botlogic.handlers.events import bot_banned, bot_unbanned


# пример создания фильтра для хэндлера(обработчика)
async def my_start_filter(message: Message) -> bool:
    return message.text == "/start"


# Хэндлер для команды /start
# @dp.message(Command(commands=["start"]))
# async def cmd_start(message: Message):
#    await message.answer("Start command")

# Пример применения созданного выше фильтра обработчиком событий
@dp.message(my_start_filter)
async def cmd_start(message: Message):
    await message.answer(text="Start command")


# Событие апдейта при блокировке бота пользователем
@dp.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated):
    print(f"{bot_banned()} пользователем {event.from_user.id}")

# TODO: Необходимо разобраться как обрабатывать события блокировки бота администраторами, иначе валятся ошибки
#  отправки уведомлений о запуске и отсановке бота Событие апдейта при разблокировании бота пользователем
@dp.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_blocked_bot(event: ChatMemberUpdated):
    print(f"{bot_unbanned()} пользователем {event.from_user.id}")


# Хэндлер для команды /help
@dp.message(Command(commands=["help"]))
async def cmd_help(message: Message):
    await message.answer("Раздел помощи")


# Хэндлер для всех прочих сообщений, не обрабатываемых первыми двумя (/start, /help)
# этот хэндлер должен идти последним в списке, иначе будет ловить все апдейты
@dp.message()
async def other_messages(message: Message):
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.reply(text="Данный тип апдейтов не поддерживается методом send_copy")
