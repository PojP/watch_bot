from sqlalchemy.ext.asyncio import create_async_engine
from config_reader import config
from sqlalchemy import MetaData, Table, String, Integer, Column, DateTime, Text, Date, Boolean, BigInteger, ForeignKey, func
from datetime import datetime
from datetime import date
from datetime import timedelta
metadata = MetaData()

users = Table('users_users', metadata, 
    Column('id', Integer(), primary_key=True),
    Column('tg_id', BigInteger(), nullable=False,unique=True),
    Column('username', String(100),  nullable=True),
    Column('referral_link', String(200), nullable=False,unique=True),
    Column('referrals', Integer(), default=0),
    Column('ads_on', Boolean(),default=True),
)
auto_post = Table('users_autopost', metadata, 
    Column('id', Integer(), primary_key=True),
    Column('post_id', BigInteger(), nullable=False,unique=True),
    Column('time', DateTime(timezone=True),nullable=False,default=func.now()),
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
series = Table('series_series', metadata,
    Column('id', Integer(), primary_key=True),
    Column('title', String(200), nullable=False),
    Column('year', Integer(),  nullable=True),
    Column('channel_link', String(200), nullable=False),
    Column('rating', Integer(),  nullable=True),
    )




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
    def remove_all_symbols(self,s:str):
        return s.replace('.','').replace(',','').replace(':','').lower()

    def movie_sorter(self, s,query):
        e_query=self.remove_all_symbols(query)
        e_s=s.copy()
        e_s[0]=self.remove_all_symbols(e_s[0])
        

        if e_s[0].startswith(e_query):
            if len(e_query)/len(e_s[0])>=0.3:
                return [s,0]
            return [s,1]
        return [s,2]

    async def get_movies(self,title):
        try:
            global movies
            async with self.engine.connect() as conn:
                sel=movies.select()
                films=(await conn.execute(sel)).fetchall()
                sel=series.select()
                series_links=(await conn.execute(sel)).fetchall()
                
                all_movies=[]                                                                                                 
                for i in films: 
                    if self.remove_all_symbols(title) in self.remove_all_symbols(i[1]):
                        if i[2] is not None:
                            br=[i[1],str(i[2]),i[3]]
                        else:
                            br=[i[1],i[3]]
                        all_movies.append(br)

                for i in series_links: 
                    if self.remove_all_symbols(title) in self.remove_all_symbols(i[1]):
                        if i[2] is not None:
                            br=[i[1],str(i[2]),i[3]]
                        else:
                            br=[i[1],i[3]]
                        all_movies.append(br)



                result=map(lambda k: self.movie_sorter(k,title),all_movies)                                                                                                              
                result=list(result)
                result=sorted(result,key=lambda k:k[1])
                all_movies=[]
                for i in result:
                    if len(i[0])==3:
                        br=[i[0][0]+" "+str(i[0][1]),i[0][2]]
                        all_movies.append(br)
                    else:
                        all_movies.append(i[0])
        except Exception as e:
            print(e)
            return e
        else:
            return all_movies



    async def get_movies_for_add(self,title,year=None):
        try:
            global movies
            async with self.engine.connect() as conn:
                sel=movies.select()
                films=(await conn.execute(sel)).fetchall()

                for i in films:
                    if self.remove_all_symbols(title) == self.remove_all_symbols(i[1]):
                        if i[2] is not None and year is not None:
                            if year==i[2]:
                                return i[3]                                                    
                        else:
                            return i[3]        
                return
        except Exception as e:
            print(e)
            return e
    async def get_series_for_add(self,title,year=None):
        try:
            async with self.engine.connect() as conn:
                sel=series.select()
                films=(await conn.execute(sel)).fetchall()

                for i in films:
                    if self.remove_all_symbols(title) == self.remove_all_symbols(i[1]):
                        if i[2] is not None and year is not None:
                            if year==i[2]:
                                return i[3]                                                    
                        else:
                            return i[3]        
                return
        except Exception as e:
            print(e)
            return e


    
    async def delete_movie(self,movie_id):
        try:
            global movies
            async with self.engine.connect() as conn:
                sel=movies.delete().where(
                        movies.c.id==movie_id
                        )
                await conn.execute(sel)
                await conn.commit()
                
        except Exception as e: 
            print(e)
            return e
        return     

    async def delete_series(self,series_id):
        try:
            async with self.engine.connect() as conn:
                sel=series.delete().where(
                        series.c.id==series_id
                        )
                await conn.execute(sel)
                await conn.commit()
                
        except Exception as e: 
            print(e)
            return e
        return     


    async def delete_movie_by_tg_id(self,tg_id):
        try:
            global movies
            async with self.engine.connect() as conn:
                sel=movies.delete().where(
                        movies.c.tg_id==tg_id
                        )
                await conn.execute(sel)
                await conn.commit()
                
        except Exception as e: 
            print(e)
            return e
        return 

    async def delete_serial_by_channel_link(self,channel_link):
        try:
            async with self.engine.connect() as conn:
                sel=series.delete().where(
                        series.c.channel_link==channel_link
                        )
                await conn.execute(sel)
                await conn.commit()
        except Exception as e: 
            print(e)
            return e
        return 


    async def add_movie(self,title,msg_id,year):
        try:
            async with self.engine.connect() as conn:
                if year is not None:
                    year=int(year)

                ins=movies.insert().values(
                    title=title,
                    year=year,
                    tg_id=msg_id
                    )
                a=await conn.execute(ins)
                await conn.commit()
        except Exception as e:
            return e
        else:
            return True
    
    async def add_serial(self, title,channel_link,year):
        try:
            async with self.engine.connect() as conn:
                if year is not None:
                    year=int(year)
                ins=series.insert().values(
                    title=title,
                    year=year,
                    channel_link=channel_link
                    )
                a=await conn.execute(ins)
                await conn.commit()
        except Exception as e:
            print(e)
            return e
        else:
            return True





    async def get_active_user_count(self,period):
        try:
            global active_time
            async with self.engine.connect() as conn:
                sel=active_time.select().where((date.today()-active_time.c.time)<=period)
                res=(await conn.execute(sel)).rowcount    
        except Exception as e:
            return e
        else:
            return res

    
    async def add_search_query(self,query,user_id):
        try:
            async with self.engine.connect() as conn:
                a=await self.get_user_info(user_id)

                ins=search_history.insert().values(
                    user_id=a[0],
                    search_query=query
                    )
                await conn.execute(ins)
                await conn.commit()

        except Exception as e:
            print(e)



    async def get_search_history(self,treshold):
        try:
            async with self.engine.connect() as conn:            
                sel=search_history.select()
                res=(await conn.execute(sel)).fetchall()

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
        except Exception as e:
            return e
        else:
            return list_to_send


    async def disable_ads(self,user_id):
        try:
            async with self.engine.connect() as conn:
                upd=users.update().where(
                    users.c.tg_id==user_id
                    ).values(
                        ads_on=False
                            )
                await conn.execute(upd)
                await conn.commit()
            
        except Exception as e:
            return e

    async def enable_ads(self,user_id):
        try:
            async with self.engine.connect() as conn:
                upd=users.update().where(
                    users.c.tg_id==user_id
                    ).values(
                        ads_on=True
                            )
                await conn.execute(upd)
                await conn.commit()
            
        except Exception as e:
            return e



    async def get_active_user_count_ads(self,period):
        try:
            global active_time
            async with self.engine.connect() as conn:
                sel=active_time.select().where((date.today()-active_time.c.time)<=period)
                res=(await conn.execute(sel)).fetchall()
                count=0
                for i in res:
                    a=(await conn.execute(users.select().where(i[1]==users.c.id))).fetchone()
                    if a[5]:
                        count+=1
            
        except Exception as e:
            return e
        else:
            return count



    async def increment_active_users(self,user_id):
        try:
            global active_time
            async with self.engine.connect() as conn:
                a=await self.get_user_info(user_id)
                sel=active_time.select().where(active_time.c.user_id==a[0]).where(active_time.c.time==datetime.now().date())
                res=(await conn.execute(sel)).rowcount                                                                                                                     
                if res==0:
                
                    ins=active_time.insert().values(
                        user_id=a[0]
                        )
                    await conn.execute(ins)                                                                                                           
                    await conn.commit()
        except Exception as e:
            print(e)
            return e
        else:
            return None




    async def increment_referrals(self,id):
        try:
            async with self.engine.connect() as conn:
                sel=users.select().where(users.c.tg_id==id)
                res=(await conn.execute(sel)).fetchone()
                stmt = users.update().values(
                referrals=res[4]+1).where(
                        users.c.tg_id == id)
                await conn.execute(stmt)
                await conn.commit()
        except Exception as e:
            return e
        else:
            return None


    async def register_user(self,user_id,username,referral_link):
        try:
            async with self.engine.connect() as conn:
                ins = users.insert().values(
                tg_id = user_id,
                username=username,
                referral_link = referral_link,
                )
                await conn.execute(ins)
                await conn.commit()
                ins=active_time.insert().values(
                    user_id=user_id
                    )
                await conn.execute(ins)
                await conn.commit()
        except Exception as e:
            return e
        else:
            return True

    async def get_users_count_with_ads(self):
        try:
            async with self.engine.connect() as conn:
                sel=users.select().where(users.c.ads_on==True)
                a=(await conn.execute(sel)).fetchall()
        except Exception as e:
            return e
        else:
            return len(a)


    async def get_users_count(self):
        try:
            async with self.engine.connect() as conn:
                sel=users.select()
                a=(await conn.execute(sel)).fetchall()
        except Exception as e:
            return e
        else:
            return len(a)
    async def get_users_tgids_ads(self,amount):
        async with self.engine.connect() as conn:
            sel =users.select().where(
                    users.c.ads_on==True
                    )
            a=(await conn.execute(sel)).fetchmany(amount)
            return a
    async def get_users_tgids(self,amount):
        async with self.engine.connect() as conn:
            sel=users.select()
            a=(await conn.execute(sel)).fetchmany(amount)
            return a
    async def get_user_info(self, user_tg_id):
        try:
            async with self.engine.connect() as conn:
                sel=users.select().where(users.c.tg_id==user_tg_id)
                a=await conn.execute(sel)
        except Exception as e:
            return e
        else:
            return a.fetchone()


    
    async def add_post_id(self,post_id,time,amount_of_users):
        try:
            async with self.engine.connect() as conn:
                ins=auto_post.insert().values(
                post_id=post_id,
                time=time,
                amount_of_users=amount_of_users
                    )
                await conn.execute(ins)
                await conn.commit()
        except Exception as e:
            return e
        return 
    async def remove_post_id(self,id):
        try:
            async with self.engine.connect() as conn:
                delete=auto_post.delete().where(auto_post.c.post_id==id)
                await conn.execute(delete)
                await conn.commit()
        except Exception as e:
            return e
        return 
    async def get_all_posts(self, time=datetime.now()):
        try:
            async with self.engine.connect() as conn:
                sel=auto_post.select().where(time>=auto_post.c.time)
                a=(await conn.execute(sel)).fetchall()
            
            
        except Exception as e:
            return e
        else:
            return a

db=DB_Controller()
