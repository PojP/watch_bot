from sqlalchemy import create_engine
from config_reader import config

from sqlalchemy import MetaData, Table, String, Integer, Column, DateTime, Text, Date, Boolean, BigInteger, ForeignKey, func
from datetime import datetime
from datetime import date
from datetime import timedelta
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
    Column('time', DateTime(),nullable=False,default=func.now()),
    Column('amount_of_users',Integer(),nullable=False,default=0)
)                                                                    

search_history = Table('users_searchhistory', metadata, 
    Column('id', Integer(), primary_key=True),
    Column('user_id', ForeignKey("users_users.id"), nullable=False),
    Column('search_query', String(100),  nullable=False),
    Column('was_found', Boolean(),default=False),
)
active_time = Table('users_activetime', metadata, 
    Column('id', Integer(), primary_key=True),
    Column('user_id', ForeignKey("users_users.id"), nullable=False),
    Column('time', Date(),  nullable=False,default=func.now()),
)
movies= Table('movies_movies', metadata,
    Column('id', Integer(), primary_key=True),
    Column('title', String(200), nullable=False),
    Column('year', Integer(),  nullable=True),
    Column('tg_id', BigInteger(), nullable=False),
    Column('rating', Integer(),  nullable=True),
    )





class DB_Controller:
    def __init__(self):
        self.engine = create_engine(f"postgresql+psycopg2://{config.db_user.get_secret_value()}:{config.db_password.get_secret_value()}@{config.db_host.get_secret_value()}/{config.db_name.get_secret_value()}",
                                    echo=False, pool_size=40, max_overflow=10)
        self.engine.connect()
        metadata.create_all(self.engine)
    
    def remove_all_symbols(self,s:str):
        return s.replace('.','').replace(',','').replace(':','').lower()

    async def get_movies(self,title):
        try:
            global movies
            conn=self.engine.connect()
            sel=movies.select()
            films=conn.execute(sel).fetchall()

            all_movies=[]
            for i in films:
                if self.remove_all_symbols(title) in self.remove_all_symbols(i[1]):
                    if i[2] is not None:
                        br=[i[1]+" "+str(i[2]),i[3]]
                    else:
                        br=[i[1],i[3]]
                    all_movies.append(br)
            conn.close()
        except Exception as e:
            print(e)
            return e
        else:
            return all_movies
    async def add_movie(self,title,msg_id,year):
        try:
            conn = self.engine.connect()
            ins=movies.insert().values(
                    title=title,
                    year=year,
                    tg_id=msg_id
                    )
            conn.execute(ins)
            conn.commit()
            conn.close()
        except Exception as e:
            return e
        else:
            return True

    async def get_active_user_count(self,period):
        try:
            global active_time
            conn=self.engine.connect()
            sel=active_time.select().where((date.today()-active_time.c.time)<=period)
            res=conn.execute(sel).rowcount    
            conn.close()
        except Exception as e:
            return e
        else:
            return res
    
    async def add_search_query(self,query,user_id):
        try:
            conn=self.engine.connect()
            a=await self.get_user_info(user_id)

            ins=search_history.insert().values(
                    user_id=a[0],
                    search_query=query
                    )
            conn.execute(ins)
            conn.commit()

            conn.close()
        except Exception as e:
            print(e)
    async def get_search_history(self,treshold):
        try:
            conn=self.engine.connect()
            sel=search_history.select()
            res=conn.execute(sel).fetchall()

            oper_list=[]
            for i in res:
                if not i[3]:
                    oper_list.append(i[2])
            
            set_oper_list=list(set(oper_list))
            amount=[]

            for i in set_oper_list:
                br=[i,oper_list.count(i)]
                amount.append(br)    
            
            amount=dict(amount)
            
            sorted_amount = sorted(amount.items(), key=lambda x:x[1], reverse=True)
            amount=dict(sorted_amount)
    

            list_to_send=[]
            counter=0
            for i in amount.keys():
                if counter>treshold:
                    break
                counter+=1
                list_to_send.append(i)
            conn.close()
        except Exception as e:
            return e
        else:
            return list_to_send

    async def disable_ads(self,user_id):
        try:
            conn=self.engine.connect()
            upd=users.update().where(
                    users.c.tg_id==user_id
                    ).values(
                        ads_on=False
                            )
            conn.execute(upd)
            conn.commit()
            conn.close()
        except Exception as e:
            return e


    async def get_active_user_count_ads(self,period):
        try:
            global active_time
            conn=self.engine.connect()
            sel=active_time.select().where((date.today()-active_time.c.time)<=period)
            res=conn.execute(sel).fetchall()
            count=0
            for i in res:
                a=conn.execute(users.select().where(i[1]==users.c.id)).fetchone()
                if a[5]:
                    count+=1
            conn.close()
        except Exception as e:
            return e
        else:
            return count


    async def increment_active_users(self,user_id):
        try:
            global active_time
            conn=self.engine.connect()
            a=await self.get_user_info(user_id)
            sel=active_time.select().where(active_time.c.user_id==a[0]).where(active_time.c.time==datetime.now().date())
            res=conn.execute(sel).rowcount                                                                                                                     
            if res==0:
                
                ins=active_time.insert().values(
                        user_id=a[0]
                        )
                conn.execute(ins)
                conn.commit()
            conn.close()
        except Exception as e:
            print(e)
            return e
        else:
            return None



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
            conn.close()
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
            ins=active_time.insert().values(
                    user_id=user_id
                    )
            conn.execute(ins)
            conn.commit()
            conn.close()
        except Exception as e:
            return e
        else:
            return True
    async def get_users_count_with_ads(self):
        try:
            conn=self.engine.connect()
            sel=users.select().where(users.c.ads_on==True)
            a=conn.execute(sel).fetchall()
            conn.close()
        except Exception as e:
            return e
        else:
            return len(a)

    async def get_users_count(self):
        try:
            conn=self.engine.connect()
            sel=users.select()
            a=conn.execute(sel).fetchall()
            conn.close()
        except Exception as e:
            return e
        else:
            return len(a)
    async def get_users_tgids(self,amount):
        conn=self.engine.connect()
        sel=users.select()
        a=conn.execute(sel).fetchmany(amount)
        conn.close()
        return a
    async def get_user_info(self, user_tg_id):
        try:
            conn=self.engine.connect()
            sel=users.select().where(users.c.tg_id==user_tg_id)
            a=conn.execute(sel)
            conn.close()
        except Exception as e:
            return e
        else:
            return a.fetchone()

    
    async def add_post_id(self,post_id,time,amount_of_users):
        try:
            conn=self.engine.connect()
            ins=auto_post.insert().values(
                post_id=post_id,
                time=time,
                amount_of_users=amount_of_users
                    )
            conn.execute(ins)
            conn.commit()
            conn.close()
        except Exception as e:
            return e
        return 
    async def remove_post_id(self,id):
        try:
            conn = self.engine.connect()
            delete=auto_post.delete().where(auto_post.c.post_id==id)
            conn.execute(delete)
            conn.commit()
            conn.close()
        except Exception as e:
            return e
        return 
    async def get_all_posts(self, time=datetime.now()):
        try:
            conn=self.engine.connect()
            sel=auto_post.select().where(time>=auto_post.c.time)
            a=conn.execute(sel).fetchall()
            
            conn.close()
        except Exception as e:
            return e
        else:
            return a
db=DB_Controller()
