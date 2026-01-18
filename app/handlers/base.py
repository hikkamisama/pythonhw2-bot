from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

base_router = Router()

@base_router.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("Добро пожаловать! Я ваш бот.\nВведите /help для списка команд.")

@base_router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(
        '''Доступные команды:
- Общие:
    - /start - Начало работы
    - /help - Показать это сообщение
- Настройка профиля:
    - /set_profile - Настройка профиля
    - /set_profile_default - Настройка профиля по умолчанию (можно изменить далее)
- Логирование:
    - Вода:
        - /log_water - Логирование приема воды. Формат: /log_water <количество воды в мл>
    - Еда:
        - /log_food - Логирование приема пищи (поиск по базе данных на английском языке). Формат: /log_food <еда для поиска>
        - /log_food_custom - Логирование приема пищи (пользовательское уточнение калорий). Формат: /log_food_custom <ккал>
    - Тренировки:    
        /log_workout - Логирование тренировок (поиск базе данных активности на английском языке). Формат: /log_workout <активность для поиска> <длительность>
        /log_workout_custom - Логирование тренировок (пользовательское уточнение времени и калорий). Формат: /log_workout_custom <длительность> <ккал>
- Прогресс:
    - /check_progress - Посмотреть текущий прогресс'''
    )