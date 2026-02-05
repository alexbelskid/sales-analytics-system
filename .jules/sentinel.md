## 2024-10-26 - [CRITICAL] Unprotected Admin Endpoints
**Vulnerability:** Critical destructive endpoints (delete all data) in `files_router.py` were completely unprotected, allowing unauthenticated API access.
**Learning:** `verify_admin_access` was assumed to be protecting these endpoints based on memory/docs, but was not actually applied or even implemented in the codebase.
**Prevention:** Always verify security controls by inspecting the code, not just documentation. Use automated tests to assert that sensitive endpoints return 401/403 without credentials.
