from src.db_controller import db
import asyncio

async def g():
    a=await db.get_active_user_by_entering(3)
    print(a)
asyncio.run(g())

