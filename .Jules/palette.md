## 2025-02-23 - Accessibility of Custom Radio Buttons
**Learning:** Using `className="hidden"` (display: none) on radio inputs removes them from the accessibility tree and tab order, making custom radio buttons completely inaccessible to keyboard users.
**Action:** Always use `sr-only` (screen-reader only) class which keeps the element in the DOM but visually hidden. Pair this with `focus-within` styling on the parent/visual container to provide clear focus indicators.
