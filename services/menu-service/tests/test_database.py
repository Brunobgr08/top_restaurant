from database import SessionLocal, get_db
import pytest

def test_get_db_yields_and_closes():
    db_gen = get_db()
    db = next(db_gen)
    assert db is not None

    try:
        pass
    finally:
        with pytest.raises(StopIteration):
            next(db_gen)