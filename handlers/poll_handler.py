from icecream import ic
from aiogram import Router
from aiogram.types import PollAnswer
from db.redis import RedisConnector
from services.excel_writer import export_to_excel

poll_rt = Router()


# Хэндлер для апдейтов на ответы в голосовании
@poll_rt.poll_answer()
async def poll_answer_add_processing(poll_answer: PollAnswer) -> None:
    # Проверим что за апдейт пришел
    # Голосование за вариант:
    if len(poll_answer.option_ids) > 0:
        conn = RedisConnector().create_connection(database=2)
        answer = {"user_id": poll_answer.user.id,
                  "name": poll_answer.user.first_name,
                  "poll_id": poll_answer.poll_id,
                  "option_ids": poll_answer.option_ids[0]
                  }
        # set_result = conn.hset(poll_answer.user.id, mapping=answer)
        set_result = conn.sadd(f"polls:{poll_answer.poll_id}:{poll_answer.option_ids[0]}", poll_answer.user.id)
    # Или отмена варианта
    else:
        conn = RedisConnector().create_connection(database=2)
        # для удаления результат голосования найдем количество ключей в которых может быть абонент
        cnt_keys = len(conn.keys(f"polls:{poll_answer.poll_id}:*"))
        ic(cnt_keys)
        cnt = 0
        # пробежим по всем ключам, и удалим значение из набора ,если оно где-то встречается
        while cnt <= cnt_keys:
            conn.srem(f"polls:{poll_answer.poll_id}:{cnt}", poll_answer.user.id)
            cnt += 1
    # poll_name = RedisConnector().create_connection(database=1).get(poll_answer.poll_id)
    # poll_data = RedisConnector().create_connection(database=2).hgetall(poll_answer.user.id)
    # await export_to_excel(data=poll_data, file_name=poll_name)
