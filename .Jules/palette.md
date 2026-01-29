# Palette's Journal

## 2025-02-18 - Verifying Accessibility in Data-Dependent Components
**Learning:** Testing accessible states (like button roles on cards) can be flaky if dependent on live backend data that might fail or change.
**Action:** When verifying UX components that depend on external data, use network interception (e.g., Playwright's `route.abort()`) to force the application into known states (like Mock Data or Error states) to guarantee the UI element exists for verification.
