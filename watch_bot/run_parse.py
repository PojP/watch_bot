from src.db_controller import db
import asyncio
async def main():
    a=await db.disable_ads(524845066)
    print(a)
asyncio.run(main())
