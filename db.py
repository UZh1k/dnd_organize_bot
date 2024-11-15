from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from consts import DB_URL

engine = create_async_engine(DB_URL)

async_session = async_sessionmaker(engine)
