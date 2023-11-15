from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, KICKED
from aiogram.fsm.state import default_state
from aiogram.types import ChatMemberUpdated

from filters.filters import IsKnownUsers, user_ids, manager_ids, admin_ids
from services.other_functions import user_banned_bot_processing

ban_rt = Router()
ban_rt.my_chat_member.filter(F.chat.type == "private")
ban_rt.message.filter(F.chat.type == "private")


@ban_rt.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED),
                       IsKnownUsers(admin_ids, manager_ids, user_ids),
                       StateFilter(default_state)
                       )
async def user_blocked_bot(event: ChatMemberUpdated):
    user_banned_bot_processing(event.from_user.id)
    # if result[0]['RESULT'] == '1':
    #     ic(f"User {event.from_user.id} blocked bot")
    # else:
    #     ic("Error in ban handler!")
