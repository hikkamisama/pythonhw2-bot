from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import db.repository as repository
from config import admin_id

admin_router = Router()

@admin_router.message(Command("get_users"))
async def get_users(message: Message, db_conn):
    if message.from_user.id == admin_id:
        ans = await repository.read_users(db_conn)
        await message.answer(str(ans))
    else:
        await message.answer("У вас нет прав на эту команду")

@admin_router.message(Command("delete_users"))
async def delete_users(message: Message, db_conn):
    if message.from_user.id == admin_id:
        await repository.delete_user_history(db_conn)
        await message.answer("Данные о пользователях удалены")
    else:
        await message.answer("У вас нет прав на эту команду")
