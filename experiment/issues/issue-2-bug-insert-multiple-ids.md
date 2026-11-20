---
title: "Document IDs skip numbers after a failed insert_multiple"
type: bug
---
When `insert_multiple` fails half way (one of the items in my batch was bad), nothing is inserted —
good — but the next document I insert gets an ID that skips over the IDs the failed batch would have
used. We use doc IDs as visible ticket numbers, so the gaps confuse our users.

```python
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

db = TinyDB(storage=MemoryStorage)
db.insert({'t': 'first'})                # -> 1
try:
    db.insert_multiple([{'t': 'ok'}, 'oops not a dict', {'t': 'ok2'}])
except ValueError:
    pass
print(db.insert({'t': 'second'}))        # -> 3, expected 2
```

Same thing happens when the batch fails because one of the `Document`s has an ID that already
exists. I'd expect a failed batch to leave everything exactly as it was, including the next ID.
