# from gpt4all import GPT4All
#
# model = GPT4All("mistral-7b-openorca.gguf2.Q4_0.gguf")
#
#
# async def generate_answer(sometext: str) -> list:
#     with model.chat_session():
#         while True:
#             prompt = sometext
#             if prompt.lower() == 'хватит':
#                 break
#
#             response = model.generate(prompt=prompt, temp=0)
#             return list(response)
from __future__ import annotations
import json
# import aioredis
from settings import GptSecrets
from yandex_cloud_ml_sdk import AsyncYCloudML


# redis = aioredis.from_url("redis://192.168.9.184:6379", decode_responses=True)


# async def get_context(user_id: int) -> list:
#     context = await redis.get(f"yagpt:{user_id}")
#     return json.loads(context) if context else []


# async def save_context(user_id: int, context: list):
#     await redis.setex(f"yagpt:{user_id}", 3600,json.dumps(context)) # TTL = 1 час


async def generate_answer(user_message):
    print(f"user message: {user_message}")
    sdk = AsyncYCloudML(
        folder_id=GptSecrets.folder_id,
        auth=GptSecrets.auth,
    )
    model = sdk.models.completions("yandexgpt-light", model_version="rc")
    model = model.configure(temperature=0.85)
    result = await model.run(
        [
            {"role": "system",
             "text": "Тебя зовут Агнесс, Ты оказваешь техническую поддержку абонентам\n"
                     "Ты работаешь в компании ""Связист""\n"
                     "Компания оказвает абоннетам услуги доступа в интернет, цифровое кабельное телевидение, стационарная телефонная связь, домофония, видеонаблюдение, IPTV\n"
                     "Доступ в интернет по технологии ADSL компания не оказывает, и техподдержку по данной тенологии не осуществляет\n"
             },
            {
                "role": "user",
                "text": user_message,
            },
        ],
    )
    print(result)
    return result.alternatives[0].text

# Функции для генерации ответа (обновлённая версия)
# import json
# from redis import asyncio as aioredis
# from settings import GptSecrets
# from yandex_cloud_ml_sdk import AsyncYCloudML
#
# # redis = Redis(host="192.168.9.184", port=6379, db=15, encoding="utf-8", decode_responses=True)
# redis = aioredis.from_url("redis://192.168.9.184:6379", decode_responses=True, db=15)
#
#
# async def get_context(user_id: int) -> list:
#     context = await redis.get(f"yagpt:{user_id}")
#     return json.loads(context) if context else []
#
#
# async def save_context(user_id: int, context: list):
#     await redis.setex(f"yagpt:{user_id}", 3600, json.dumps(context))
#
#
# def _trim_context(context: list, max_messages: int = 10) -> list:
#     """Оставляет последние N сообщений (user+assistant пар)"""
#     return context[-max_messages * 2:] if len(context) > max_messages * 2 else context
#
#
# async def generate_answer(user_message: str, user_id: int):
#     # Получаем текущий контекст
#     #context = await get_context(user_id)
#
#     # Добавляем новое сообщение пользователя
#     #context.append({"role": "user", "text": user_message})
#
#     # Обрезаем историю до последних 10 пар сообщений
#     #context = _trim_context(context)
#     context = [{"role": "user", "text": user_message}]
#
#     # Формируем полный запрос с системным промптом
#     messages = [
#                    {
#                        "role": "system",
#                        "text":
#                            "Тебя зовут Агнесс. Ты оказываешь техническую поддержку абонентам\n"
#                            "Ты работаешь в компании ""Связист""\n"
#                            " Компания оказывает абонентам услуги доступа в интернет, цифровое кабельное телевидение, стационарная телефонная связь, домофония, видеонаблюдение, IPTV\n"
#                            "Доступ в интернет по технологии ADSL компания не оказывает, и техподдержку по данной тенологии не осуществляет\n"
#                    },
#                ] + context
#     print(messages)
#     # Выполняем запрос к YandexGPT
#     sdk = AsyncYCloudML(
#         folder_id=GptSecrets.folder_id,
#         auth=GptSecrets.auth,
#     )
#     model = sdk.models.completions("yandexgpt", model_version="rc")
#     model = model.configure(temperature=0.3, max_tokens=4000)
#     print(model)
#     result = await model.run(messages)
#     print("result: {}".format(result))
#
#     # Извлекаем и сохраняем ответ
#     assistant_response = result.alternatives[0].text
#     # context.append({"role": "assistant", "text": assistant_response})
#
#     # Сохраняем обновлённый контекст
#     # await save_context(user_id, context)
#
#     return assistant_response
