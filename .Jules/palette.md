## 2023-10-27 - Custom Modal vs Native Confirm
**Learning:** Users find native `window.confirm()` dialogs jarring in a polished UI. Replacing them with custom "glass" modals significantly improves the perceived quality.
**Action:** Always check for `window.confirm` or `window.alert` in existing code and plan to replace them with custom UI components that match the design system.

## 2023-10-27 - Localization and Accessibility
**Learning:** When the `html lang` attribute is set to a specific language (e.g., 'ru'), all ARIA labels must match that language to ensure screen readers pronounce them correctly. Mixing English ARIA labels with Russian content creates a poor experience.
**Action:** Verify the document language before writing accessibility attributes.
