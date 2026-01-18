from aiogram.fsm.state import State, StatesGroup

class Profile_form(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity_goal = State()
    city = State()
    calorie_goal = State()

class Workout_form(StatesGroup):
    activity = State()
    duration = State()
    calories = State()

class Food_form(StatesGroup):
    grams = State()
    calories_per_100g = State()
