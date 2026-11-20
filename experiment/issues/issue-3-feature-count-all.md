---
title: "Let count() work without a query"
type: feature
---
`db.count(query)` is handy, but when I want the total number of documents I have to remember to use
`len(db)` / `len(table)` instead, and `db.count()` just blows up:

```
TypeError: Table.count() missing 1 required positional argument: 'cond'
```

Could `count()` with no argument simply return the number of documents in the table? Counting with a
query should keep working the same way it does today.
