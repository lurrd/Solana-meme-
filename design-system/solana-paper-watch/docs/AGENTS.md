# UI work instructions — Solana Paper Watch

Before authoring or changing any UI in this design system, read:

1. ../README.md for product scope, visual direction, component patterns, and safety language.
2. ../tokens.css for the authoritative design tokens.

## Required use

- Use the `--sw-*` tokens for all colors, type, spacing, shape, focus, and motion. Do not create a competing palette or hard-code visual values when a token exists.
- Keep the persistent **PAPER MODE** state and the full simulation/data-quality notice visible on market and portfolio screens.
- Label simulated balances, positions, entries, exits, and P&L as simulated. Never add wallet connection, transaction signing, private-key/seed-phrase collection, or live-order controls.
- Use positive/negative colors only for directional data, and pair color with an explicit sign or label.
- Include freshness and uncertainty states; unknown data must not be rendered as zero.
- Preserve keyboard access, visible focus, semantic labels, readable contrast, narrow-screen behavior, and reduced-motion support.

The existing repository is a Python CLI watcher. Do not alter its paper-trading behavior or imply that a dashboard has been implemented just by adding these design files.
