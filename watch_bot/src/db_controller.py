from django.db.models import BigIntegerField
from sqlalchemy import create_engine
from config_reader import config

from sqlalchemy import MetaData, Table, String, Integer, Column, Text, DateTime, Boolean, BigInteger, ForeignKey
from datetime import datetime
metadata = MetaData()

users = Table('users_users', metadata, 
    Column('id', Integer(), primary_key=True),
    Column('tg_id', BigInteger(), nullable=False,unique=True),
    Column('username', String(100),  nullable=False),
    Column('referral_link', String(200), nullable=False,unique=True),
    Column('referrals', Integer(), default=0),
    Column('ads_on', Boolean(),default=True),
)
auto_post = Table('users_autopost', metadata, 
    Column('id', Integer(), primary_key=True),
    Column('post_id', BigInteger(), nullable=False,unique=True),
)
button_links = Table('users_buttonlinks', metadata, 
    Column('id', Integer(), primary_key=True),
    Column('post', ForeignKey("users_autopost.id"), nullable=False),
    Column('url', String(200),  nullable=False),
)
search_history = Table('users_searchhistory', metadata, 
    Column('id', Integer(), primary_key=True),
    Column('user', ForeignKey("users_users.id"), nullable=False),
    Column('search_query', String(100),  nullable=False),
    Column('was_found', Boolean(),default=False),
)
active_time = Table('users_activetime', metadata, 
    Column('id', Integer(), primary_key=True),
    Column('user', ForeignKey("users_users.id"), nullable=False),
    Column('time', DateTime(),  nullable=False,default=datetime.now),
)
movies= Table('movies_movies', metadata,
    Column('id', Integer(), primary_key=True),
    Column('title', String(200), nullable=False),
    Column('year', Integer(),  nullable=False),
    Column('tg_id', BigInteger(), nullable=False),
    Column('rating', Integer(),  nullable=True),
    )





class DB_Controller:
    def __init__(self):
        self.engine = create_engine(f"postgresql+psycopg2://{config.db_user.get_secret_value()}:{config.db_password.get_secret_value()}@{config.db_host.get_secret_value()}/{config.db_name.get_secret_value()}",
                                    echo=True, pool_size=6, max_overflow=10)
        self.engine.connect()
        metadata.create_all(self.engine)

    async def get_movie(self,title):
        pass
    
    async def send_movie(self,title,tg_id,year):
        pass

    async def increment_referrals(self,id):
        try:
            conn = self.engine.connect()
            sel=users.select().where(users.c.tg_id==id)
            res=conn.execute(sel).fetchone()
            stmt = users.update().values(
                referrals=res[4]+1).where(
                        users.c.tg_id == id)
            conn.execute(stmt)
            conn.commit()
        except Exception as e:
            return e
        else:
            return None

    async def register_user(self,user_id,username,referral_link):
        try:
            conn=self.engine.connect()
            ins = users.insert().values(
                tg_id = user_id,
                username=username,
                referral_link = referral_link,
                )
            conn.execute(ins)
            conn.commit()
        except Exception as e:
            return e
        else:
            return True
    
    
    
    async def get_user_info(self, user_tg_id):
        try:
            conn=self.engine.connect()
            sel=users.select().where(users.c.tg_id==user_tg_id)
            a=conn.execute(sel)
        except Exception as e:
            return e
        else:
            return a.fetchone()

db=DB_Controller()
