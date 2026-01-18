from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from typing import Match
from states import Profile_form
import db.repository as repository
from config import defaults

setup_router = Router()

@setup_router.message(Command("set_profile"))
async def set_profile(message: Message, state: FSMContext):
    await state.set_state(Profile_form.weight)
    await message.answer("Введите ваш вес (в кг):")

@setup_router.message(Command("set_profile"))
async def set_profile(message: Message, state: FSMContext):
    await state.set_state(Profile_form.weight)
    await message.answer("Введите ваш вес (в кг):")

@setup_router.message(Profile_form.weight, F.text.regexp(r"^(\d+)$").as_("digits"))
async def process_weight(message: Message, state: FSMContext, digits: Match[str]):
    await state.update_data(weight=int(digits[0]))
    await state.set_state(Profile_form.height)
    await message.answer("Введите ваш рост (в см):")

@setup_router.message(Profile_form.height, F.text.regexp(r"^(\d+)$").as_("digits"))
async def process_height(message: Message, state: FSMContext, digits: Match[str]):
    await state.update_data(height=int(digits[0]))
    await state.set_state(Profile_form.age)
    await message.answer("Введите ваш возраст (полных лет):")

@setup_router.message(Profile_form.age, F.text.regexp(r"^(\d+)$").as_("digits"))
async def process_age(message: Message, state: FSMContext, digits: Match[str]):
    await state.update_data(age=int(digits[0]))
    await state.set_state(Profile_form.activity_goal)
    await message.answer("Введите ваш целевой уровень активности (в минутах):")

@setup_router.message(Profile_form.activity_goal, F.text.regexp(r"^(\d+)$").as_("digits"))
async def process_activity_goal(message: Message, state: FSMContext, digits: Match[str]):
    await state.update_data(activity_goal=int(digits[0]))
    await state.set_state(Profile_form.city)
    await message.answer("Введите ваш город (на английском языке):")

@setup_router.message(Profile_form.city)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(Profile_form.calorie_goal)
    await message.answer("Введите целевое потребление (в ккал):")

@setup_router.message(Profile_form.calorie_goal, F.text.regexp(r"^(\d+)$").as_("digits"))
async def process_calorie_goal(message: Message, state: FSMContext, digits: Match[str], db_conn):
    data = await state.update_data(calorie_goal=int(digits[0]))

    calorie_goal = data.get("calorie_goal")
    if calorie_goal is None:
        calorie_goal = 10 * data.get("weight", defaults['weight']) + 6.25 * data.get("height", defaults['height']) - 5 * data.get("age", defaults['age'])
    
    water_norm = data.get("weight", defaults['weight']) * 30

    await repository.set_profile(
        db_conn,
        message.from_user.id,
        data.get("height", defaults['height']),
        data.get("weight", defaults['weight']),
        data.get("age", defaults['age']),
        data.get("city", defaults['city']),
        calorie_goal,
        water_norm,
        data.get("activity_goal", defaults['activity_goal'])
    )
    await state.clear()
    await message.answer("Профиль заполнен.")

@setup_router.message(Command("set_profile_default"))
async def set_profile(message: Message, db_conn):
    await repository.set_profile(
        db_conn,
        message.from_user.id,
        **defaults
    )
    await message.answer("Профиль заполнен.")