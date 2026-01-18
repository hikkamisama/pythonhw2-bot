import aiosqlite
import os


async def get_db():
    db_path = os.path.dirname(os.path.abspath(__file__)) + '/tracking_bot.db'
    conn = await aiosqlite.connect(db_path)
    return conn