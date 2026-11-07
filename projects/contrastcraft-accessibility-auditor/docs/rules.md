# Rule catalog

- `document-language`, `document-title`: basic document metadata.
- `image-alt`, `image-input-alt`: alternative text presence (not semantic correctness).
- `input-label`: explicit label or ARIA label presence.
- `duplicate-id`, `aria-reference`: reference integrity.
- `accessible-name`: basic text or aria-label on buttons and links.
- `link-href`: warning for anchors without destinations.
- `zoom-disabled`: viewport zoom restriction.
- `deprecated-font`: legacy presentational element warning.

These checks are heuristics, not exhaustive WCAG conformance tests.
