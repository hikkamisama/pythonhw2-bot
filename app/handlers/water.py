import aiohttp
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
import datetime
import db.repository as repository
from config import openweather_token, openweather_url

water_router = Router()

@water_router.message(Command("log_water"))
async def log_water(message: Message, command: CommandObject, db_conn):
    if not command.args or not command.args.isdigit():
        await message.answer("Напишите команду в правильном формате, например: /log_water 300")
        return

    user_id = message.from_user.id
    user_data = await repository.get_profile(db_conn, user_id)
    if user_data is None:
        await message.answer("Профиль не найден. Создайте профиль с помощью команды /set_profile или /set_profile_default")
        return

    await repository.log_history(db_conn, user_id, datetime.datetime.now(datetime.timezone.utc), 'water', int(command.args))

    reply = await get_reply_water(message, True, db_conn)
    await message.answer(reply)

async def check_weather(message: Message, db_conn):
    user_id = message.from_user.id
    user_data = await repository.get_profile(db_conn, user_id)
    city = user_data['city']
    temp = None
    temp_error_msg = ""
    params = {
        "q": city,
        "appid": openweather_token
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(openweather_url, params=params) as response:
                temp_json = await response.json()
                if response.status == 200 and "main" in temp_json:
                    temp = temp_json['main']['temp'] - 273.15
                else:
                    temp_error_msg = f"\n\nНе удалось получить температуру для города {city}."
    except Exception as ex:
        temp_error_msg = f"\n\nОшибка при получении температуры: {str(ex)}"
    return temp, temp_error_msg

async def get_reply_water(message: Message, verbose: bool, db_conn):
    user_id = message.from_user.id

    temp, temp_error_msg = await check_weather(message, db_conn)

    user_progress = await repository.check_progress(db_conn, user_id)
    activity = user_progress['activity_minutes']
    water_intake = user_progress['water_intake']
    base_water_norm = user_progress['water_norm']

    extra_activity = (activity // 30) * 500 if activity else 0
    extra_heat = (temp is not None and temp > 25) * 500
    water_norm = base_water_norm + extra_activity + extra_heat

    user_data = await repository.get_profile(db_conn, user_id)
    city = user_data['city']

    result_message = (
        f"- Выпито: {water_intake} из {water_norm} мл."
    )

    if water_intake > water_norm:
        result_message += f"\n- Вы выпили больше вашей нормы на {water_intake - water_norm} мл."
    elif water_intake == water_norm:
        result_message += "\n- Вы выпили норму воды в день."
    else:
        result_message += f"\n- Осталось: {water_norm - water_intake} мл."

    if verbose:
        if temp is not None and temp > 25:
            result_message += f"\n\nВ {city} сейчас жарко (температура {temp:.1f}°C), норма воды увеличена."
        if activity > 30:
            result_message += f"\n\nСегодня у вас было {activity} минут активности, норма воды увеличена."
        if temp_error_msg:
            result_message += "\n\nПри попытке узнать температуру возникла ошибка:\n" + temp_error_msg

    return result_message