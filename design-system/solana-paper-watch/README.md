# Solana Paper Watch — Design System

**Slug:** `solana-paper-watch`  
**Version:** 1.0  
**Status:** foundation for a future companion dashboard; the current repository is a Python CLI watcher.

## Product scope

This system is for a calm, information-first interface that can help someone inspect Solana meme-token pairs and understand a simulated portfolio. It does not turn the existing watcher into a trading app. The watcher is explicitly paper-only: it places no real trades, does not access wallets, and uses public market data that may be delayed or incomplete.

## Design direction: Signal, not spectacle

Use a dark, legible market-monitoring surface with restrained mint and violet accents. Keep dense market data scannable without borrowing casino patterns: no flashing gain effects, urgency timers, confetti, or oversized speculative-return claims. Reserve green and red for positive and negative movement, not brand decoration. Do not use Solana logos or imply official affiliation.

## Foundations

Import `tokens.css` as the source of truth for color, type, spacing, shape, and focus tokens. Use the system sans stack for interface copy and the monospace stack for addresses, prices, and aligned financial values. Prefer tabular numerals and align numeric columns to the decimal/right edge.

| Role | Token | Use |
| --- | --- | --- |
| App canvas | `--sw-bg` | Main page background |
| Raised surface | `--sw-surface` | Cards, panels, tables |
| Primary text | `--sw-text` | Headings and primary values |
| Secondary text | `--sw-muted` | Explanations, labels, timestamps |
| Mint accent | `--sw-accent` | Selected navigation, focus, key actions |
| Violet accent | `--sw-accent-alt` | Secondary emphasis and chart identity |
| Positive / negative | `--sw-positive` / `--sw-negative` | Signed market movement and P&L only |
| Warning | `--sw-warning` | Stale or incomplete data, risk notices |

## Core patterns

### Application shell

Use a compact top bar with product name, a persistent **PAPER MODE** badge, and the last successful data-refresh time. On wide screens, pair the watchlist with a portfolio summary; on narrow screens, stack these sections and preserve the paper-mode disclosure near the top.

### Paper-mode disclosure

Show a readable notice on every market or portfolio view: **Simulation only — no real trades or wallet access. Market data can be delayed or incomplete.** Do not reduce this to an icon, tooltip, or footer-only note.

### Summary metric

A metric panel contains a short label, a prominent value, and a muted context line. Label balances as **Simulated cash** or **Paper portfolio value**. Do not label simulation values as funds, account balances, or realized profits.

### Token pair row

Show symbol and token name, shortened mint/pair address with an accessible copy action, price, liquidity, 24-hour volume, 1-hour change, pair age, and data freshness where available. Keep values in predictable columns. Unknown values display **—** or **Unknown**, never zero by implication.

### Change and P&L badges

Include an explicit sign and unit, for example **+2.4%** or **−1.8%**. Use both text and color to communicate direction. Do not use green/red as the only signal, and do not animate routine price refreshes.

### Paper position row

Show entry price, current mark, simulated size, unrealized P&L, and holding duration. Label every position as simulated. Explain that a position may not have a current mark if its pair is absent from search results.

### Search, filters, and states

Search and filter controls should expose the active thresholds (liquidity, 24-hour volume, pair age). Loading states should preserve column labels; empty states should explain whether filters may be too strict; errors should show the last successful refresh and a retry path without suggesting a trade.

## Interaction and language

- Use **Watch**, **Inspect**, **Paper entry**, and **Paper exit** for simulated actions; never use unqualified **Buy**, **Sell**, **Trade now**, or **Connect wallet**.
- No wallet connection, signing, private-key, seed-phrase, or real order controls belong in this system.
- Confirm destructive actions such as clearing local paper history, and state exactly what data will be removed.
- Show refresh timestamps in a human-readable local time with UTC available in detail views.
- Avoid language that promises returns, implies a validated strategy, or frames paper results as predictive.

## Responsive and accessible behavior

- At narrow widths, keep symbol, price, and signed change visible; allow secondary metrics to wrap or move into a detail row rather than shrinking text.
- Use semantic headings, table headers, labels, and buttons. Every icon-only control needs an accessible name.
- Keep text and controls readable against their surfaces, provide a visible keyboard-focus ring, and respect reduced-motion preferences.
- Do not encode status by color alone; add a sign, label, icon with accessible text, or explanatory copy.

## Do / avoid

**Do:** prioritize freshness, provenance, thresholds, and simulation status; use consistent financial formatting; show uncertainty plainly.  
**Avoid:** meme-coin hype styling, flashing price ticks, fake exchange affordances, profit guarantees, and live-trading implications.
