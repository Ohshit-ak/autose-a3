"""Hidden acceptance tests, issue 2 (IDs skip after failed insert_multiple)."""
import pytest
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from tinydb.table import Document


def _db():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'t': 'first'})
    return db


def test_next_id_not_skipped_after_non_mapping_failure():
    db = _db()
    with pytest.raises(ValueError):
        db.insert_multiple([{'t': 'ok'}, 'oops', {'t': 'ok2'}])
    assert db.insert({'t': 'second'}) == 2


def test_next_id_not_skipped_after_duplicate_document_id_failure():
    db = _db()
    with pytest.raises(ValueError):
        db.insert_multiple([{'t': 'ok'}, Document({'t': 'dup'}, doc_id=1)])
    assert db.insert({'t': 'second'}) == 2


def test_batch_after_failure_gets_consecutive_ids():
    db = _db()
    with pytest.raises(ValueError):
        db.insert_multiple([{'a': 1}, {'a': 2}, 3])
    assert db.insert_multiple([{'b': 1}, {'b': 2}]) == [2, 3]


def test_failed_batch_inserts_nothing():
    """Guard (passes on base too)."""
    db = _db()
    with pytest.raises(ValueError):
        db.insert_multiple([{'t': 'ok'}, 'oops'])
    assert db.all() == [{'t': 'first'}]
