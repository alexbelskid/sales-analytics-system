## 2024-05-22 - Manual Drag-and-Drop Accessibility
**Learning:** Custom drag-and-drop zones (divs) often miss keyboard accessibility (tabIndex, onKeyDown, role='button') compared to libraries like react-dropzone.
**Action:** When auditing custom file uploaders, always verify they can be triggered via keyboard (Enter/Space).
