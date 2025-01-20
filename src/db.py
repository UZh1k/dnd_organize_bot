from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from consts import DB_URL, DB_POOL_SIZE

engine = create_async_engine(DB_URL, pool_size=DB_POOL_SIZE, pool_pre_ping=True)

async_session = sessionmaker(engine, class_=AsyncSession)
