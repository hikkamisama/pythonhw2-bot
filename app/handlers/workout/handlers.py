from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import datetime
from typing import Any
import db.repository as repository
from config import admin_id

workout_router = Router()

@workout_router.message(Command("log_workout"))
async def log_workout(message: Message, state: FSMContext, db_conn, ninjas_api):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer(
            "Пожалуйста, используйте формат: /log_workout <активность> <длительность>\n"
            "Например: /log_workout swimming 30"
        )
        return

    user_id = message.from_user.id
    user_data = await repository.get_profile(db_conn, user_id)
    if user_data is None:
        await message.answer("Профиль не найден. Создайте профиль с помощью команды /set_profile или /set_profile_default")
        return
    weight = user_data['weight']

    activity = parts[1].lower()
    value = parts[2]

    try:
        duration = int(value)
    except ValueError:
        await message.answer("Пожалуйста, укажите длительность в минутах целым числом.")
        return
    
    total_cal, ninja_error = await ninjas_api.search(activity, duration, weight)
    if ninja_error and message.from_user.id == admin_id:
        await message.answer("Во время исполнения поиска активности возникли ошибки:" + ninja_error)
    elif total_cal is None:
        await message.answer("На ваш запрос не нашлось информации в базе данных. Попробуйте еще раз или используйте команду /log_workout_custom")
    else:
        data = await state.update_data(activity=activity, duration=duration, calories=total_cal)
        await reply_activity(message, data, db_conn)

@workout_router.message(Command("log_workout_custom"))
async def log_workout(message: Message, state: FSMContext, db_conn):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer(
            "Пожалуйста, используйте формат: /log_workout_custom <длительность> <ккал>\n"
            "Например: /log_workout_custom 30 150"
        )
        return

    user_id = message.from_user.id
    user_data = await repository.get_profile(db_conn, user_id)
    if user_data is None:
        await message.answer("Профиль не найден. Создайте профиль с помощью команды /set_profile или /set_profile_default")
        return

    value1 = parts[1]
    value2 = parts[2]

    try:
        duration = int(value1)
    except ValueError:
        await message.answer("Пожалуйста, укажите длительность в минутах целым числом.")
        return
    try:
        total_cal = int(value2)
    except ValueError:
        await message.answer("Пожалуйста, укажите расход в ккал целым числом.")
        return
    
    data = await state.update_data(activity="Ваша активность", duration=duration, calories=total_cal)
    await reply_activity(message, data, db_conn)

async def reply_activity(message: Message, data: dict[str, Any], db_conn):
    activity_str = data['activity']
    duration = data['duration']
    total_cal = data['calories']
    reply = f"{activity_str} {duration} минут - {total_cal} ккал."
    if duration >= 30:
        reply += f" Дополнительно: выпейте {duration // 30 * 500} мл воды."
    await repository.log_history(db_conn, message.from_user.id, datetime.datetime.now(datetime.timezone.utc), 'activity_minutes', duration)
    await repository.log_history(db_conn, message.from_user.id, datetime.datetime.now(datetime.timezone.utc), 'activity_calories', total_cal)
    await message.reply(reply)