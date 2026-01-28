## 2026-01-15 - Unsecured Administrative Endpoints
**Vulnerability:** The `DELETE /api/files/delete-all-data` and `DELETE /api/files/all-sales` endpoints were publicly accessible, allowing anyone to wipe the entire database without authentication.
**Learning:** Destructive endpoints were added to a router without adding a dependency for authentication. Additionally, the `/api/files/all-sales` endpoint was unreachable because it was defined after a dynamic route `/{file_id}`, masking the vulnerability (but also the feature) until it was tested.
**Prevention:**
1. Always apply `dependencies=[Depends(verify_admin_access)]` or similar to administrative routers or endpoints.
2. Define static routes before dynamic routes (e.g., `/{file_id}`) to avoid shadowing.
3. Use tests to verify access control on sensitive endpoints.
