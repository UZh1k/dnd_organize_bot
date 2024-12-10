from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from consts import DB_URL, DB_POOL_SIZE

engine = create_async_engine(DB_URL, pool_size=DB_POOL_SIZE)

async_session = async_sessionmaker(engine)
