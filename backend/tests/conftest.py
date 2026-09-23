import pytest
import pytest_asyncio
from app.database.database import init_db

@pytest_asyncio.fixture(autouse=True, scope="function")
async def setup_test_db():
    await init_db()
    yield
