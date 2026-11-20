---
title: "Operation to append a value to a list field"
type: feature
---
I store tags as lists, e.g. `{'name': 'post-1', 'tags': ['python']}`, and I keep writing little
lambdas to add a tag:

```python
def add_tag(tag):
    def transform(doc):
        doc.setdefault('tags', []).append(tag)
    return transform

db.update(add_tag('db'), Query().name == 'post-1')
```

`tinydb.operations` already has `increment`, `add`, `set`, `delete`... It would be great to have
something like `operations.append('tags', 'db')` that appends a value to a list field (and starts a
new list if the document doesn't have that field yet).
