## 2026-01-15 - Async Blocking I/O
**Learning:** `pandas.read_csv` and `read_excel` are synchronous and blocking. In FastAPI async routes, this blocks the main event loop, causing the entire server to freeze while reading large files.
**Action:** Always wrap CPU-bound or blocking I/O (like pandas read operations) in `asyncio.to_thread()` within async endpoints.
