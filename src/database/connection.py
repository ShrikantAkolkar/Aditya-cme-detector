import asyncio
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from src.config import config
import logging

logger = logging.getLogger(__name__)

# Database engine
engine = None
SessionLocal = None
Base = declarative_base()

async def init_database():
    """Initialize database connection and create tables"""
    global engine, SessionLocal
    
    database_url = config.database_url
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
    
    engine = create_async_engine(
        database_url,
        pool_size=config.get('database.pool_size', 10),
        max_overflow=config.get('database.max_overflow', 20),
        echo=config.get('system.debug', False)
    )
    
    SessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # Import models to ensure they're registered
    from src.models.particle_data import ParticleData
    from src.models.cme_event import CMEEvent
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database initialized successfully")

@asynccontextmanager
async def get_db_session():
    """Get database session with automatic cleanup"""
    if SessionLocal is None:
        await init_database()
    
    async with SessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

async def close_database():
    """Close database connections"""
    global engine
    if engine:
        await engine.dispose()
        logger.info("Database connections closed")