from datetime import datetime
import os
from dotenv import find_dotenv, load_dotenv
from sqlalchemy import Column,Integer,String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import update
from sqlalchemy.sql.sqltypes import Boolean, DateTime, Float
from sqlalchemy.orm import sessionmaker
import pytz

load_dotenv(find_dotenv(raise_error_if_not_found=True))
Base = declarative_base()

class CoinHistory(Base):
    __tablename__ = 'coin_history'
    id = Column(Integer, primary_key=True)
    update_time = Column(DateTime)
    symbol = Column(String(length=10))
    name = Column(String(length=200))
    price = Column(Float)
    bought = Column(Boolean)
    quantity = Column(Integer)

    def create_coin(self, symbol, name, price, bought, quantity):
        """Returns a coin object that is insertable into db table"""
        update_time = datetime.now(pytz.timezone('US/Eastern'))
        coin_obj = CoinHistory(update_time=update_time,
                                symbol=symbol,
                                name=name,
                                price=price,
                                bought=bought,
                                quantity=quantity)
        return coin_obj


class DBSession:
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_DATABASE")
    DB_PORT = os.getenv("DB_PORT")
    DB_USER = os.getenv("DB_USERNAME")
    DB_PSWD = os.getenv("DB_PASSWORD")

    def create_db_session(self):
        """creates a mysql db session object"""
        mysql_conn_str = f"mysql+pymysql://{self.DB_USER}:{self.DB_PSWD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        engine = create_engine(mysql_conn_str)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        self.create_tables(engine)
        return session

    def create_tables(self, engine):
        """create all tables"""
        Base.metadata.create_all(engine)
