"""Hidden acceptance tests, issue 3 (count() without a query)."""
from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage


def _db():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'a': 1}, {'a': 2}, {'a': 1}])
    return db


def test_count_without_query_counts_all_documents():
    assert _db().table('_default').count() == 3


def test_db_level_count_without_query():
    assert _db().count() == 3


def test_count_without_query_on_empty_table():
    db = TinyDB(storage=MemoryStorage)
    assert db.table('empty').count() == 0


def test_count_with_query_unchanged():
    """Guard (passes on base too)."""
    assert _db().count(where('a') == 1) == 2
