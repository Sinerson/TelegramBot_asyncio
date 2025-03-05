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
                       decode_responses=DbSecrets.redis_decode
                       )


async def get_context(user_id: int) -> list:
    context = await redis.get(f"yagpt:{user_id}")
    return json.loads(context) if context else []


# async def save_context(user_id: int, context: list):
#     await redis.setex(f"yagpt:{user_id}", 3600, json.dumps(context))
#
#
# def _trim_context(context: list, max_messages: int = 20) -> list:
#     """Оставляет последние N сообщений (user+assistant пар)"""
#     return context[-max_messages * 2:] if len(context) > max_messages * 2 else context
#
#
# async def update_context(user_id: int, user_msg: str, bot_response: str):
#     context = await get_context(user_id)
#     context.extend([
#         {"role": "user", "text": user_msg},
#         {"role": "assistant", "text": bot_response}
#     ])
#     await save_context(user_id, context)
async def save_context(user_id: int, context: list):
    """
    Сохраняет контекст в Redis.

    Параметры:
        user_id (int): Идентификатор пользователя
        context (list): Контекст диалога
    """
    try:
        await redis.setex(
            f"yagpt:{user_id}",  # Ключ
            3600,  # TTL (1 час)
            json.dumps(context)  # Сериализованный контекст
        )
    except Exception as e:
        print(f"Ошибка сохранения контекста: {str(e)}")
        raise


def _trim_context(context: list, max_messages: int = 10) -> list:
    """
    Обрезает контекст, оставляя последние N пар сообщений.

    Параметры:
        context (list): Текущий контекст диалога
        max_messages (int): Максимальное количество пар сообщений

    Возвращает:
        list: Обрезанный контекст
    """
    # Оставляем последние N пар (user + assistant)
    return context[-max_messages * 2:] if len(context) > max_messages * 2 else context


async def update_context(user_id: int, user_msg: str, bot_response: str):
    """
    Обновляет и сохраняет контекст диалога в Redis.

    Параметры:
        user_id (int): Идентификатор пользователя в Telegram
        user_msg (str): Последнее сообщение от пользователя
        bot_response (str): Ответ бота (без обращения по имени)
    """
    try:
        # Получаем текущий контекст
        context = await get_context(user_id)

        # Добавляем новые сообщения
        context.append({"role": "user", "text": user_msg})
        context.append({"role": "assistant", "text": bot_response})

        # Обрезаем контекст, если он превышает лимит
        context = _trim_context(context, max_messages=10)

        # Сохраняем обновленный контекст
        await save_context(user_id, context)

        # Логирование для отладки
        print(f"Контекст обновлен для user_id={user_id}")
        print(f"Текущий размер контекста: {len(context)} сообщений")

    except Exception as e:
        # Логируем ошибки
        print(f"Ошибка при обновлении контекста: {str(e)}")
        raise


async def generate_answer(user_message: str, user_id: int, abonent: Abonent):
    print(abonent.get_services_info())
    sdk = YCloudML(
        folder_id=GptSecrets.folder_id,
        auth=GptSecrets.auth,
    )

    model = sdk.models.completions("yandexgpt-lite", model_version="rc")
    model = model.configure(temperature=0.5)

    system_prompt = ("Тебя зовут Агнесс.\n"
                     "Ты - оператор техподдержки интернет провайдера ООО ""Связист""\n"
                     f"Данные абонента:\n{abonent.get_services_info()}\n\n"
                     "Компания оказывает услуги на территории г.Кстово и Кстовского р-на\n"
                     "Общайся уважительно, на матерные слова не реагируй\n"
                     "Здоровайся только в первом сообщении\n"
                     "Отвечай точно на вопросы об услугах и платежах\n"
                     "Телефон технической поддержки: 8(83145)77777, email: helpdesk@sv-tel.ru\n"
                     "Телефон отдела продаж: 8(81345)77711\n"
                     "Официальный сайт компании: https://sv-tel.ru\n"
                     "Личный кабинет абонента: https://lk.sv-tel.ru\n"
                     )

    messages = [
        {"role": "system", "text": system_prompt},
        *await get_context(user_id=user_id)
    ]

    if abonent.is_first_message:
        greeting = abonent.get_greeting() + "Чем могу помочь?"
        messages.insert(1, {"role": "assistant", "text": greeting})
        messages.append({"role": "user", "text": user_message})
    else:
        messages.append({"role": "user", "text": user_message})

    result = model.run(messages=messages)

    response = result.alternatives[0].text

    if not abonent.is_first_message:
        response = f"{abonent.get_named()}, {response}"

    await update_context(user_id=user_id, user_msg=user_message, bot_response=response)

    return response
