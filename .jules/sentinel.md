## 2024-05-23 - Critical: Unauthenticated Data Deletion
**Vulnerability:** The `delete-all-data` and related endpoints in `files_router.py` were unprotected, allowing unauthenticated users to wipe the entire sales database and import history.
**Learning:** Security dependencies must be explicitly applied to all destructive routes. Assumptions about "admin only" features being hidden or protected by frontend logic are dangerous.
**Prevention:** Always use `Depends(verify_admin_access)` or similar auth dependencies on any route that modifies or deletes data. Use automated tests to verify that sensitive endpoints return 401/403 when accessed without credentials.
