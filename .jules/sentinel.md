## 2026-01-12 - Missing Administrative Authentication
**Vulnerability:** The destructive endpoint `DELETE /api/files/delete-all-data` (and others) was publicly accessible without any authentication, allowing anyone to wipe the entire database.
**Learning:** The application lacked a centralized administrative authentication mechanism (like an Admin Key) despite having "admin-only" functionality.
**Prevention:** Always verify authentication and authorization for destructive endpoints. Implemented `verify_admin_access` dependency using `X-Admin-Key` header.
