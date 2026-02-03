## 2025-05-18 - Consistent Delete Modal Pattern
**Learning:** The application used native `confirm()` dialogs for single file deletion but a custom modal for "Delete All". Native dialogs break the "Liquid Glass" immersion and offer poor accessibility control.
**Action:** Always prefer the custom `role="alertdialog"` modal pattern used in `FilesPage` for destructive actions. It provides better context (filenames) and keyboard management.
