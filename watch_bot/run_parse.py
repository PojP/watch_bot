from src.db_controller import db
import asyncio
async def main():
    a=await db.increment_active_users(123)
asyncio.run(main())
