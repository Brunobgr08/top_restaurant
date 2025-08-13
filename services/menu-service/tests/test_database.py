from database import SessionLocal, get_db
import pytest

def test_get_db_yields_and_closes():
    db_gen = get_db()        # chama a função geradora
    db = next(db_gen)        # executa até o yield
    assert db is not None    # verifica que o db foi retornado corretamente

    # Força a execução do bloco "finally" (db.close())
    try:
        pass
    finally:
        # finaliza o generator para acionar o finally do get_db()
        with pytest.raises(StopIteration):
            next(db_gen)