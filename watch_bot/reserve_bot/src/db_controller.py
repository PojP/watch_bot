from sqlalchemy.ext.asyncio import create_async_engine
from config_reader import config
from sqlalchemy import MetaData, Table, String, Integer, Column


metadata = MetaData()

reserve_list=Table('reverve_bot_list',metadata,
    Column('id',Integer(),primary_key=True),
    Column('user_id',String(200),nullable=False,unique=False),
    Column('reserve_bot_id',String(200),nullable=False,unique=False))



class DB_Controller:
    def __init__(self):
        self.engine = create_async_engine(f"postgresql+asyncpg://{config.db_user.get_secret_value()}:{config.db_password.get_secret_value()}@{config.db_host.get_secret_value()}/{config.db_name.get_secret_value()}",
                                    echo=False, pool_size=40, max_overflow=10)
        print(config.db_user.get_secret_value())
        self.user=config.db_user.get_secret_value()
    async def init(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
            print('all added')
        await self.engine.dispose()
    
    async def add_user_to_reserve_list(self,user_id,bot):
        try:
            async with self.engine.connect() as conn:
                if await self.check_reserve_following(user_id,bot):
                    ins=reserve_list.insert().values(
                            user_id=str(user_id),
                            reserve_bot_id=bot,
                            )
                    await conn.execute(ins)
                    await conn.commit()
                    return
        except Exception as e:
            return "Problem in database"
    async def check_reserve_following(self,user_id,bot):
        try:
            async with self.engine.connect() as conn:
                sel=reserve_list.select().where(
                        reserve_list.c.user_id==str(user_id),
                        reserve_list.c.reserve_bot_id==bot
                        )
                a=(await conn.execute(sel)).rowcount
                print(a)
                if a >0:
                    return False
                return True
        except Exception as e:
            print(a)
            return e
    

db=DB_Controller()
