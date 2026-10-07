import os
import asyncio

# CRITICAL: Force the test suite to use an in-memory SQLite database
# MUST be set before any app modules are imported
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///file:testdb?mode=memory&cache=shared&uri=true'

import pytest
import pytest_asyncio
from app.database import engine, Base, AsyncSessionLocal
from seed_data import seed_database

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """
    Sets up the in-memory SQLite database and seeds it exactly once 
    per test session to avoid conflicts and state bleeding.
    """
    # 1. Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    # 2. Seed the data required by tests
    await seed_database()
    
    yield
    
    # 3. Teardown
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

