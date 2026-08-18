from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from consts import DB_POOL_SIZE, DB_URL

engine = create_async_engine(DB_URL, pool_size=DB_POOL_SIZE, pool_pre_ping=True)

async_session = sessionmaker(engine, class_=AsyncSession)
