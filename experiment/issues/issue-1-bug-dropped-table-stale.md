---
title: "Table still returns old documents after drop_table()"
type: bug
---
In our tests we keep a reference to a table, and reset the data between test cases with
`db.drop_table(...)` (or `db.drop_tables()`). After the drop, the table object still finds the old
documents with `search()` and `count()`, even though `all()` and `len()` say the table is empty.
New documents also continue the old ID sequence instead of starting at 1 like a fresh table.

```python
from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage

db = TinyDB(storage=MemoryStorage)
users = db.table('users')
users.insert({'name': 'ann'})
users.insert({'name': 'bob'})
print(users.search(where('name') == 'ann'))   # [{'name': 'ann'}]

db.drop_table('users')

print(users.all())                            # []           (ok)
print(users.search(where('name') == 'ann'))   # [{'name': 'ann'}]   <- expected []
print(users.count(where('name') == 'ann'))    # 1                   <- expected 0
print(users.insert({'name': 'cat'}))          # 3                   <- expected 1
```

Looks like some cached state survives the drop. TinyDB 4.9.0.
