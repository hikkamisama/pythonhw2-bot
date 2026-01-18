from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import datetime
from states import Food_form
import db.repository as repository
from config import admin_id

food_router = Router()

async def get_reply_food(message: Message, db_conn):
    user_id = message.from_user.id
    progress = await repository.check_progress(db_conn, user_id)

    calorie_intake = progress['food_intake']
    calorie_goal = progress['calorie_goal']
    activity_calories = progress['activity_calories']

    result_message = (
        f"- Потреблено: {calorie_intake} из {calorie_goal} ккал."
    )
    result_message += f"\n- Сожжено: {activity_calories}."
    result_message += f"\n- Баланс: {calorie_intake - activity_calories}."
    result_message += f"\n- Остаток: {calorie_goal - (calorie_intake - activity_calories)}."

    return result_message

@food_router.message(Command("log_food"))
async def log_food(message: Message, state: FSMContext, db_conn, fatsecret_api):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "Пожалуйста, используйте формат: /log_food <еда>\n"
            "Например: /log_food banana bread"
        )
        return
    food = parts[1]
    user_id = message.from_user.id
    user_data = await repository.get_profile(db_conn, user_id)
    if user_data is None:
        await message.answer("Профиль не найден. Создайте профиль с помощью команды /set_profile или /set_profile_default")
        return
    calories_per_100g, api_error = await fatsecret_api.search(food)
    if len(api_error) and message.from_user.id == admin_id:
        await message.answer("Во время исполнения поиска еды возникли ошибки:" + '\n\n'.join(api_error))
    elif calories_per_100g is None:
        await message.answer("На ваш запрос не нашлось информации в базе данных. Попробуйте еще раз или используйте команду /log_food_custom")
    else:
        await state.update_data(calories_per_100g=calories_per_100g)
        await state.set_state(Food_form.grams)
        await message.answer(f"{food} - это {calories_per_100g} ккал на 100 грамм. Пожалуйста, укажите количество граммов, потребленных в прием пищи. Например: 150")

@food_router.message(Food_form.grams)
async def process_grams(message: Message, state: FSMContext, db_conn):
    try:
        grams = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, укажите количество граммов целым числом. Например: 150")
        return
    data = await state.update_data(grams=grams)
    await state.clear()
    total_cal = round(data['grams'] / 100 * data['calories_per_100g'])
    await repository.log_history(db_conn, message.from_user.id, datetime.datetime.now(datetime.timezone.utc), 'food', total_cal)
    reply_food = await get_reply_food(message, db_conn)
    reply = f"Записано {total_cal} калорий\n" + reply_food
    await message.answer(reply)

@food_router.message(Command("log_food_custom"))
async def log_food(message: Message, db_conn):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "Пожалуйста, используйте формат: /log_food_custom <ккал>\n"
            "Например: /log_food_сustom 150"
        )
        return
    try:
        total_cal = int(parts[1])
    except ValueError:
        await message.answer("Пожалуйста, укажите калории целым числом.")
        return
    await repository.log_history(db_conn, message.from_user.id, datetime.datetime.now(datetime.timezone.utc), 'food', total_cal)
    reply_food = await get_reply_food(message, db_conn)
    reply = f"Записано {total_cal} калорий\n" + reply_food
    await message.answer(reply)