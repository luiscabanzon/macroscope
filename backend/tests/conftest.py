import os
import sys
from pathlib import Path
import pytest
import pytest_asyncio

# Ensure backend root is on sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.database import get_connection, init_db

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture
def load_fixture(fixtures_dir: Path):
    def _loader(filename: str) -> str:
        filepath = fixtures_dir / filename
        return filepath.read_text(encoding="utf-8")
    return _loader


@pytest_asyncio.fixture
async def test_db(tmp_path: Path):
    """Provides an initialized temporary SQLite database path."""
    db_file = tmp_path / "test_macroscope.db"
    db_path = str(db_file)
    await init_db(db_path)
    return db_path


@pytest_asyncio.fixture
async def db_conn(test_db: str):
    """Provides an active async connection to the test database."""
    async with get_connection(test_db) as conn:
        yield conn
