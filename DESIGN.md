# DESIGN.md — Dashboard PDAD // SIMPLE CLEAN

<!-- impeccable:design-schema 1 -->

## World

**Simple Clean** (user-requested "simple alternative"; follows Buku SOP and Data Terminal rounds). A calm, legible work surface: the Duktek reads the numbers and finds the answer without fighting the furniture. Heavy metaphors are refused (no stamp, no barcode, no chapter book) — clarity is the whole identity.

## Mode

**Operate.** The Duktek completes a task — find the handling steps for a kendala, read SLA status, trace tickets. Scanability and calm consistency outrank expression.

## Palette

| Token | Hex | Role |
|---|---|---|
| `--sc-bg` | `#FAFAF8` | Near-white neutral ground |
| `--sc-card` | `#FFFFFF` | Card surface |
| `--sc-line` | `#E6E6E1` | Hairline border |
| `--sc-line-strong` | `#D4D4CE` | Strong border |
| `--sc-ink` | `#1A1D21` | Primary text |
| `--sc-ink-dim` | `#6B7280` | Secondary text |
| `--sc-ink-faint` | `#9CA3AF` | Placeholder / meta |
| `--sc-blue` | `#2563EB` | Action / focus / primary |
| `--sc-green` | `#16A34A` | OK / status |
| `--sc-amber` | `#B45309` | Watch / count |
| `--sc-red` | `#DC2626` | Critical (reserved) |

Color strategy: **Restrained** — neutrals plus one blue accent for actions and focus; green/amber carry semantic status only.

## Typography

- **Face:** system-ui stack (`ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto`) — no font import, crisp native rendering.
- **Numerals:** `font-feature-settings: "tnum" 1, "zero" 1` — tabular throughout.
- **Scale:** page title 1.45rem/700; KPI value 1.7rem/700; body 0.87–0.95rem; labels 0.7–0.75rem/600; section eyebrow 0.72rem/600 tracked +0.08em uppercase.

## Shape & Components

- **Corners:** 8–10px radius (cards, inputs, buttons) — soft modern, not pill, not square.
- **Slim header:** app name + blue dot accent, muted readout (ticket count · date window · freshness) on the right.
- **KPI card:** white card, hairline border, subtle shadow; uppercase label, 1.7rem value (tone optional), faint sub-line.
- **Result card:** white card, hairline border, 10px radius; title + amber count head row; blue uppercase domain eyebrow; summary; numbered `<ol>` steps; amber 💡 note with top hairline. Hover darkens border.
- **Search hero:** full-width input (white, 8px, blue focus ring) with clear placeholder; example chips as small buttons below when empty.
- **Empty state:** dashed-border card, centered faint message.
- **Buttons:** solid blue, white text, 8px radius; hover darkens.
- **Sidebar:** white, right hairline; app masthead, radio nav (4 pages), `FILTER` section (date, kategori, duktek), ticket counter.

## Typographic / Layout Rhythm

- Section eyebrows `UPPERCASE` gray before each block.
- One spacing rhythm: ~10px cards, ~20px section gaps, more space above headings than below.
- Charts sit in white cards with hairline border + padding.

## Navigation / Topology

4 pages (radio in sidebar), Cari Solusi default:

1. `🔍 Cari Solusi` — hero: KPI row (4) → search input → Panduan result cards → Tiket terkait table. Example chips on empty state.
2. `📊 Ringkasan` — KPI row, tren line chart, kategori bar chart, top masalah/pelapor tables.
3. `⏱ SLA & Kinerja` — KPI row, bucket bar chart, SLA-per-kategori, kinerja per duktek.
4. `📋 Eksplorasi Tiket` — filter inputs (pelapor/masalah/nomor), full table, CSV download.

## Interaction & State

- **Focus:** blue border + soft blue ring (12% alpha).
- **Buttons:** example chips fill the search input and rerun (session_state `scan_fill` → `scan_input`).
- **Hover:** primary buttons darken; radio labels get blue-soft background; result cards darken border.
- **Tabs:** active tab blue-soft background + blue text.
- **State language:** empty input = example chips; no match = dashed note; counts in section eyebrows.

## Responsive

- Full-bleed wide layout; KPI row collapses to 4-up → stacks on narrow viewports via Streamlit columns.
- Charts and tables stretch to container; charts in white cards.

## Implementation Notes (Streamlit)

- Light neutral theme via `.streamlit/config.toml` (`base="light"`, white/neutral palette, `font="sans serif"`) **plus** CSS injection with `!important` overrides (background, inputs, buttons, sidebar, dataframes, tabs, charts).
- All custom HTML escaped via `html.escape` (user data rendered safely).
- `width="stretch"` used (no deprecated `use_container_width`).
- No external font import — system-ui stack, instant load.
- Data cached `ttl=3600`; `probis` empty → `-` per user document convention.

## Anti-Patterns Guarded

- No heavy theme metaphors (this round is deliberately plain).
- No Inter-everywhere → native system-ui stack.
- No purple-blue gradients → flat palette with one blue.
- No card-in-card → flat result cards.
- No gray text on colored backgrounds → dim ink only on white/near-white.
- No thick side-tab borders → plain hairline cards (detector-verified).
