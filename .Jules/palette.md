## 2024-05-22 - Accessible Tabs Pattern
**Learning:** Custom tab implementations often miss semantic roles (`tablist`, `tab`, `tabpanel`), making them indistinguishable from random buttons to screen readers.
**Action:** Always add `role="tablist"` to container, `role="tab"` with `aria-selected` to triggers, and `role="tabpanel"` with `aria-labelledby` to content areas.
