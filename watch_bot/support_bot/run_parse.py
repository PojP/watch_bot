from src.db_controller import db
import asyncio
async def main():
    a=await db.get_movies_for_add("Лолита")
    print(a)
asyncio.run(main())
