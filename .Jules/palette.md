## 2025-02-18 - Keyboard Accessibility for Interactive Cards
**Learning:** Highly styled, interactive "cards" (using `div`s with `onClick`) are a common pattern in dashboard designs but often exclude keyboard users completely.
**Action:** When identifying these patterns, adding `role="button"`, `tabIndex={0}`, and `onKeyDown` (for Enter/Space) immediately restores accessibility without requiring a full refactor to semantic `<button>` elements (which might break complex flex/grid layouts). Don't forget visual focus states!
