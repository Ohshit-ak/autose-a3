---
title: "Search crashes on older data"
type: vague
---
Our app has been running for a couple of years and the database has some older records that were
written by previous versions of our code, so not every document looks the same. Since then, some
searches just crash with errors like

```
TypeError: '>' not supported between instances of 'str' and 'int'
```

and the whole page fails. Other searches work fine. I don't really want to migrate all the old data.
TinyDB should be more forgiving here, or at least not take my whole app down because of one weird
record.
