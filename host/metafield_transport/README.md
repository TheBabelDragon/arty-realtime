# metafield_transport

Host-side sketch for ADR-002. MetaField (or a thin adapter) should depend on this API, not on AXI/Zmod details.

```python
from metafield_transport import Eclypse

e = Eclypse("192.168.1.50")
e.configure(sample_rate=1_000_000, channels=[0, 1, 2, 3], mode="FEATURE")
e.start()
e.bind_data()
frame = e.read()   # DataFrame with sequence + timestamp_ticks
```

When the board is not present, `command()` / `read()` raise or return `None` — fine for unit tests of framing.

Copy or vendor this package into the MetaField repo under `metafield/transport/` when ready to wire `observe()`.
