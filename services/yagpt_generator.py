from __future__ import annotations

import requests

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
    # print(f"Получен {user_id=}")
    context = await redis.get(f"yagpt:{user_id}")
    # print(f"Контекст из Redis: {context}")
    return json.loads(context) if context else []


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
    # print(f"Обрезаем лишние сообщения с начала")
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
        # print(f"Контекст обновлен для user_id={user_id}")
        # print(f"Текущий размер контекста: {len(context)} сообщений")

    except Exception as e:
        # Логируем ошибки
        print(f"Ошибка при обновлении контекста: {str(e)}")
        raise


async def tokenize_text(text):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {GptSecrets.auth}"
    }
    payload = {
        "modelUri": GptSecrets.modelUri,
        "text": text
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        token_text = [el.get('text') for el in response.json()['tokens']]
        number_of_tokens = len(token_text)
        return number_of_tokens, token_text
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


async def generate_answer(user_message: str, user_id: int, abonent: Abonent):
    global tokens, num_tok
    money = 0.0
    sdk = YCloudML(
        folder_id=GptSecrets.folder_id,
        auth=GptSecrets.auth,
    )

    model = sdk.models.completions(GptSecrets.model_name, model_version="rc")
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
    res_get_context = await get_context(user_id=user_id)
    # print(f"Текущий контектс: {res_get_context=}")
    messages = [
        {"role": "system", "text": system_prompt},
        # *await get_context(user_id=user_id)
        *res_get_context
    ]

    if abonent.is_first_message:
        greeting = abonent.get_greeting() + "Чем могу помочь?"
        messages.append({"role": "assistant", "text": greeting})
        messages.append({"role": "user", "text": user_message})
    else:
        messages.append({"role": "user", "text": user_message})

    try:
        num_tok, tokens = await tokenize_text(' '.join(el.get('text') for el in messages))
        if GptSecrets.model_name == "yandexgpt-lite":
            money = (0.20 / 1000) * num_tok
        elif GptSecrets.model_name == "yandexgpt":
            money = (0.60 / 1000) * num_tok
    except Exception as e:
        print(e)

    result = model.run(messages=messages)
    # print(result)

    response = result.alternatives[0].text
    # print(response)

    if not abonent.is_first_message:
        response = f"{abonent.get_named()}, {response}"

    await update_context(user_id=user_id, user_msg=user_message, bot_response=response)
    # print(response)
    return response, num_tok, tokens, money
