"""Hidden acceptance tests, issue 1 (stale table state after drop_table / drop_tables).
Never shown to any agent. Run against the PR head (see run_hidden.sh)."""
from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage


def _setup():
    db = TinyDB(storage=MemoryStorage)
    users = db.table('users')
    users.insert({'name': 'ann'})
    users.insert({'name': 'bob'})
    q = where('name') == 'ann'
    assert users.search(q) == [{'name': 'ann'}]  # warm the query cache
    return db, users, q


def test_search_and_count_empty_after_drop_table():
    db, users, q = _setup()
    db.drop_table('users')
    assert users.search(q) == []
    assert users.count(q) == 0


def test_ids_restart_after_drop_table():
    db, users, q = _setup()
    db.drop_table('users')
    assert users.insert({'name': 'cat'}) == 1


def test_held_table_is_fresh_after_drop_tables():
    db, users, q = _setup()
    db.drop_tables()
    assert users.search(q) == []
    assert users.insert({'name': 'cat'}) == 1


def test_other_tables_unaffected_by_drop_table():
    """Guard (passes on base too)."""
    db, users, q = _setup()
    other = db.table('other')
    other.insert({'name': 'ann'})
    assert other.search(q) == [{'name': 'ann'}]
    db.drop_table('users')
    assert other.search(q) == [{'name': 'ann'}]
