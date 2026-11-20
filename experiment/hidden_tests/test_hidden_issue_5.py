"""Hidden acceptance tests, issue 5 (vague: searches crash on heterogeneous data).
Encodes the conservative interpretation: a document whose field cannot be compared
simply does not match, and the search returns the comparable matches."""
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def _db():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'age': 30}, {'age': 'thirty'}, {'age': None}, {'age': 12}, {'name': 'x'}])
    return db


def test_greater_than_on_mixed_types_does_not_raise():
    assert _db().search(Query().age > 18) == [{'age': 30}]


def test_less_equal_and_less_than_on_mixed_types():
    db = _db()
    assert db.search(Query().age <= 12) == [{'age': 12}]
    assert db.search(Query().age < 100) == [{'age': 30}, {'age': 12}]


def test_greater_equal_with_string_operand_on_mixed_types():
    db = _db()
    assert db.search(Query().age >= 'a') == [{'age': 'thirty'}]


def test_homogeneous_comparisons_unchanged():
    """Guard (passes on base too)."""
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'v': 1}, {'v': 2}, {'v': 3}])
    assert db.search(Query().v > 1) == [{'v': 2}, {'v': 3}]
    assert db.count(Query().v >= 1) == 3
