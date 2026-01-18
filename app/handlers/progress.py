from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from .water import get_reply_water
from .food.handlers import get_reply_food

progress_router = Router()

@progress_router.message(Command("check_progress"))
async def check_progress(message: Message, db_conn):

    reply_water = await get_reply_water(message, False, db_conn)
    reply_food = await get_reply_food(message, db_conn)

    reply_message = " 📊 Прогресс: \n\nВода:\n" + reply_water + "\n\nКалории:\n" + reply_food
    await message.answer(reply_message)