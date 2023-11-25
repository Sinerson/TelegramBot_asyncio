from aiogram import Router, F
from aiogram.types import Message
from icecream import ic
from filters.filters import IsKnownUsers, user_ids, admin_ids, manager_ids
import redis

poll_rt = Router()

connect = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True, charset='utf8')
somedict = {}


# Хэндлер для апдейтов на ответы в голосовании
@poll_rt.poll_answer()
async def poll_processing(message: Message):
    global set_result
    somedict["user_id"] = message.user.id
    somedict["name"] = message.user.first_name
    somedict["option_ids"] = message.option_ids[0]
    try:
        set_result = connect.hset(name=message.poll_id, mapping=somedict)
    except redis.RedisError as e:
        ic(f"error: {e}")
    get_result = connect.hgetall(message.poll_id)
    print(f"set_result: {set_result}, get_result: {get_result}")
