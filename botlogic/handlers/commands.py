from aiogram import F
from aiogram.filters import Command, ChatMemberUpdatedFilter, KICKED, MEMBER
from aiogram.types import Message, ChatMemberUpdated
from botlogic.settings import dp, Secrets
from botlogic.handlers.events import bot_banned, bot_unbanned
from botlogic.filters import IsAdmin, admin_ids, NumbersInMessage


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


# Проверка на админа
'''@dp.message(IsAdmin(admin_ids))
async def answer_if_admins_update(message: Message):
    await message.answer(text="Вы в списке админов")'''


# Событие апдейта при блокировке бота пользователем
@dp.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated):
    print(f"{bot_banned()} пользователем {event.from_user.id}")


# TODO: Необходимо разобраться как обрабатывать события блокировки бота администраторами, иначе валятся ошибки
#  отправки уведомлений о запуске и остановке бота

#  Событие апдейта при разблокировании бота пользователем
@dp.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_blocked_bot(event: ChatMemberUpdated):
    print(f"{bot_unbanned()} пользователем {event.from_user.id}")


# Хэндлер для команды /help
@dp.message(Command(commands=["help"]))
async def cmd_help(message: Message):
    await message.answer("Раздел помощи")


# Этот хэндлер будет срабатывать, если сообщение пользователя
# начинается с фразы "найди числа" и в нем есть числа
@dp.message(F.text.lower().startswith('найди числа'),
            NumbersInMessage())
# Помимо объекта типа Message, принимаем в хэндлер список чисел из фильтра
async def process_if_numbers(message: Message, numbers: list[int]):
    await message.answer(
            text=f'Нашел: {", ".join(str(num) for num in numbers)}')


# Этот хэндлер будет срабатывать, если сообщение пользователя
# начинается с фразы "найди числа", но в нем нет чисел
@dp.message(F.text.lower().startswith('найди числа'))
async def process_if_not_numbers(message: Message):
    await message.answer(
            text='Не нашел что-то :(')


# Хэндлер для всех прочих сообщений, не обрабатываемых первыми двумя (/start, /help)
# этот хэндлер должен идти последним в списке, иначе будет ловить все апдейты
@dp.message()
async def other_messages(message: Message):
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.reply(text="Данный тип апдейтов не поддерживается методом send_copy")
