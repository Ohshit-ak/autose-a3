"""Hidden acceptance tests, issue 4 (operations.append)."""
from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage


def _db():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'p1', 'tags': ['python']})
    db.insert({'name': 'p2'})
    db.insert({'name': 'p3', 'tags': []})
    return db


def test_append_to_existing_list():
    from tinydb.operations import append
    db = _db()
    db.update(append('tags', 'db'), where('name') == 'p1')
    assert db.get(where('name') == 'p1')['tags'] == ['python', 'db']


def test_append_creates_list_when_field_missing():
    from tinydb.operations import append
    db = _db()
    db.update(append('tags', 'new'), where('name') == 'p2')
    assert db.get(where('name') == 'p2')['tags'] == ['new']


def test_append_only_touches_matching_documents():
    from tinydb.operations import append
    db = _db()
    db.update(append('tags', 'x'), where('name') == 'p3')
    assert db.get(where('name') == 'p3')['tags'] == ['x']
    assert db.get(where('name') == 'p1')['tags'] == ['python']
    assert 'tags' not in db.get(where('name') == 'p2')
