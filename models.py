import datetime
from sqlalchemy import Integer, String
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
import os
from dotenv import load_dotenv
from atexit import register


# Загрузка переменных окружения
load_dotenv()
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')

engine = create_async_engine(f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}')

Session = async_sessionmaker(bind=engine, expire_on_commit=False)

Base = declarative_base()


class Base(DeclarativeBase, AsyncAttrs):
    pass

class StarWarsPerson(Base):
    __tablename__ = 'start_wars_persons'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    birth_year: Mapped[str] = mapped_column(String(128), nullable=False)
    eye_color: Mapped[str] = mapped_column(String(128), nullable=False)
    films: Mapped[str] = mapped_column(String(512), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    hair_color: Mapped[str] = mapped_column(String(32), nullable=False)
    height: Mapped[str] = mapped_column(String(128), nullable=False)
    homeworld: Mapped[str] = mapped_column(String(128), nullable=False)
    mass: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    skin_color: Mapped[str] = mapped_column(String(128), nullable=False)
    species: Mapped[str] = mapped_column(String(1024), nullable=False)
    starships: Mapped[str] = mapped_column(String(1024), nullable=False)
    vehicles: Mapped[str] = mapped_column(String(1024), nullable=False)


async def init_orm():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

register(engine.dispose)
