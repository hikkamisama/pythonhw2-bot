import asyncio
from aiogram import Bot, Dispatcher
from config import *
from middlewares import LoggingMiddleware
from db.session import get_db
from db.repository import create_history_table, create_users_table

from handlers.food.api import FatSecretApi
from handlers.workout.api import NinjasApi
from handlers.init import routers

async def main():
    bot = Bot(token=telegram_token)
    dp = Dispatcher()
    for router in routers:
        dp.include_router(router)

    conn = await get_db()
    dp['db_conn'] = conn
    dp.shutdown.register(lambda : conn.close())
    await create_users_table(conn), await create_history_table(conn)

    dp['fatsecret_api'] = FatSecretApi(client_id, client_secret, token_url, api_url, proxy, proxy_user, proxy_password)
    dp['ninjas_api'] = NinjasApi(ninjas_url, ninjas_api)

    dp.message.outer_middleware(LoggingMiddleware())
    
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())