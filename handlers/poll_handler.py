from aiogram import Router
from aiogram.types import PollAnswer
from db.redis import RedisConnector
from services.excel_writer import export_to_excel

poll_rt = Router()


# Хэндлер для апдейтов на ответы в голосовании
@poll_rt.poll_answer()
async def poll_processing(poll_answer: PollAnswer) -> None:
    # if poll_answer.user.id in [admin_ids + manager_ids + user_ids]:
    conn = RedisConnector().create_connection(database=2)
    answer = {"user_id": poll_answer.user.id, "name": poll_answer.user.first_name,
              "option_ids": poll_answer.option_ids[0]}
    set_result = conn.hset(name=poll_answer.poll_id, mapping=answer)
    poll_name = RedisConnector().create_connection(database=1).get(poll_answer.poll_id)
    poll_data = RedisConnector().create_connection(database=2).hgetall(poll_answer.poll_id)
    await export_to_excel(data=poll_data, file_name=poll_name)
