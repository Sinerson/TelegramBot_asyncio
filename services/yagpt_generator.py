from __future__ import annotations
from settings import GptSecrets, DbSecrets
from yandex_cloud_ml_sdk import YCloudML
from redis import asyncio as aioredis
import json
from services.classes import Abonent

redis = aioredis.Redis(host=DbSecrets.redis_host,
                       port=DbSecrets.redis_port,
                       db=15,
                       encoding='utf-8',
                       # charset=DbSecrets.redis_charset,
                       decode_responses=DbSecrets.redis_decode)


async def get_context(user_id: int) -> list:
    context = await redis.get(f"yagpt:{user_id}")
    return json.loads(context) if context else []


async def save_context(user_id: int, context: list):
    await redis.setex(f"yagpt:{user_id}", 3600, json.dumps(context))


def _trim_context(context: list, max_messages: int = 20) -> list:
    """Оставляет последние N сообщений (user+assistant пар)"""
    return context[-max_messages * 2:] if len(context) > max_messages * 2 else context


async def update_context(user_id: int, user_msg: str, bot_response: str):
    context = await get_context(user_id)
    context.extend([
        {"role": "user", "text": user_msg},
        {"role": "assistant", "text": bot_response}
    ])
    await save_context(user_id, context)


async def generate_answer(user_message: str, user_id: int, abonent: Abonent):
    sdk = YCloudML(
        folder_id=GptSecrets.folder_id,
        auth=GptSecrets.auth,
    )

    model = sdk.models.completions("yandexgpt-lite", model_version="rc")
    model = model.configure(temperature=0.5)

    # context = await get_context(user_id=user_id)
    # context.append({"role": "user", "text": user_message})
    # context = _trim_context(context=context)

    system_prompt = ("Тебя зовут Агнесс.\n"
                     "Ты - оператор техподдержки интернет провайдера ООО ""Связист""\nК тебе обращаются абоненты за помощью\n"
                     f"Данные абонента:\n{abonent.get_services_info()}\n\n"
                     "компания в которой ты работаешь подключает услуги на территории г.Кстово и Кстовского р-на\n"
                     "Набор услуг следующий: интернет (Ethernet и PON), цифровое кабельное ТВ, стационарный телефон, умный домофон, видеонаблюдение, ОТТ- телевидение\n"
                     "Общайся уважительно, на матерные слова не реагируй\n"
                     "Всегда обращайся к абоненту по имени и отчеству\n"
                     "Здоровайся только в первом сообщении\n"
                     "Отвечай точно на вопросы об услугах и платежах\n"
                     )

    message = [
        {"role": "system", "text": system_prompt},
        *await get_context(user_id=user_id),
        {"role": "user", "text": user_message}
    ]

    if abonent.is_first_message:
        message.insert(1, {"role": "assistant", "text": abonent.get_greeting() + " Чем могу помочь?"})

    result = model.run(messages=message)

    response = result.alternatives[0].text
    addressed_response = f"{abonent.get_address()}, {response}"

    await update_context(user_id=user_id, user_msg=user_message, bot_response=addressed_response)
    # await save_context(user_id=user_id, context=context)

    return addressed_response
