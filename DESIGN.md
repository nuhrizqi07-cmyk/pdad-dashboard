# DESIGN.md — Dashboard PDAD // TERMINAL

<!-- impeccable:design-schema 1 -->

## World

**Data Terminal** (challenger `ikeda-datamatics`, seed 02dade84). The dashboard is a data terminal, not a brochure: every ticket is a signal frame, every SLA is an instrument reading, every search is a scan across the known solution space. Refuses the category default of rounded pastel cards on a white page.

## Mode

**Operate.** The Duktek completes a task: find the handling steps for a kendala, read SLA status, trace tickets. Scanability, consistency and the real usage scene outrank expression.

## Palette

| Token | Hex | Role |
|---|---|---|
| `--dt-bg` | `#0B0F14` | Near-black blue field (ground) |
| `--dt-panel` | `#121A22` | Slate panel |
| `--dt-panel2` | `#0F151C` | Sidebar / deeper panel |
| `--dt-line` | `#1F2A36` | Hairline border |
| `--dt-ink` | `#E8EEF5` | Primary text |
| `--dt-ink-dim` | `#8FA3B8` | Secondary text / labels |
| `--dt-amber` | `#FFB454` | Watch / SLA / counts |
| `--dt-green` | `#4ADE80` | Clear / OK / status |
| `--dt-red` | `#F87171` | Critical (reserved) |
| `--dt-cyan` | `#22D3EE` | Action / focus / accent |
| `--dt-violet` | `#A78BFA` | Reserved accent |

Color strategy: **Restrained** — neutrals plus one action accent (cyan); amber/green carry semantic status, not decoration. Color commits at region scale (KPI side bars, section eyebrows, frame corners), never scattered accents.

## Typography

- **Face:** JetBrains Mono (Google Fonts), fallback Fira Code / Cascadia Code / ui-monospace stack.
- **Numerals:** `font-feature-settings: "tnum" 1, "zero" 1` — tabular throughout.
- **Scale:** KPI value 1.9rem/800; page title 1.7rem/800; section eyebrow 0.72rem/700 tracked +0.16em; body 0.82–0.95rem; micro-labels 0.66–0.68rem tracked +0.12–0.14em uppercase.

## Shape & Components

- **Corners:** square (`border-radius: 0`) everywhere — cards, inputs, buttons, frames, dataframes.
- **Header bar:** bordered slate strip; brand `PDAD://TERMINAL` (cyan), readout `FRAMES · WINDOW · MODE OPERATE · SIG ONLINE` (green/amber).
- **KPI instrument card:** uppercase micro-label, 1.9rem tabular value, sub-line, 6px colored right-edge bar (cyan default; amber/green semantic).
- **Barcode bar-field:** `repeating-linear-gradient` strip, 26px, 55% opacity — section separator ornament.
- **Sine divider:** inline SVG double-wave (cyan + dim), 26px, full width.
- **Solution frame card:** flat slate, 1px border, cyan corner brackets (`::before`/`::after`, 2px, top-left + bottom-right); title + amber ticket count head row; cyan uppercase domain eyebrow; summary; numbered `<ol>` steps; amber note block with dashed top border.
- **Empty state:** dashed-border slab, centered `■ message`.
- **Buttons:** flat slate, cyan 1px border, uppercase tracked label; hover inverts (cyan fill, dark text).

## Typographic / Layout Rhythm

- Section eyebrows `▸ LABEL` in cyan uppercase before each block.
- One spacing rhythm: ~10px between cards, ~22px section gaps, more space above headings than below.
- Sidebar = `PDAD::NAV` radio (4 pages), `// FILTER GLOBAL` (date, kategori, duktek), frame counter footer.

## Navigation / Topology

4 pages (radio in sidebar), SCAN SOLUSI default:

1. `▚ SCAN SOLUSI` — hero: KPI instrument row (4) → barcode → scan input → solution frames → signal traces table.
2. `▤ RINGKASAN` — KPI row, tren line chart, kategori bar chart, top masalah/pelapor dataframes.
3. `⏱ SLA & KINERJA` — KPI row, bucket bar chart, SLA-per-kategori, kinerja per duktek.
4. `▦ EKSPLORASI` — filter inputs (pelapor/masalah/nomor), full dataframe, CSV download.

## Interaction & State

- **Focus:** input focus ring = cyan 1px + glow (the active "scan" state).
- **Buttons:** example scan chips fill the query and rerun (session_state `scan_fill` → `scan_input`).
- **Hover:** buttons invert to cyan fill; radio labels turn cyan.
- **Tabs:** active tab cyan underline.
- **State language:** empty = `TUNGGU INPUT…` frame; no match = dashed empty slab; results count in section eyebrow.

## Responsive

- Full-bleed 1440px layout (`layout="wide"`); KPI row collapses to 4-up → stacks on narrow viewports via Streamlit columns.
- Charts and dataframes stretch to container.

## Implementation Notes (Streamlit)

- Dark theme forced via `.streamlit/config.toml` (`base="dark"`, palette mapped to theme tokens, `font="monospace"`) **plus** CSS injection with `!important` overrides on `stAppViewContainer`, inputs, buttons, sidebar, dataframes, tabs.
- All custom HTML escaped via `html.escape` (user data rendered safely).
- `use_container_width` avoided; `width="stretch"` used.
- Google Fonts `@import` in CSS; system monospace fallback covers offline.
- Data cached `ttl=3600`; `probis` empty → `-` per user document convention.

## Anti-Patterns Guarded

- No Inter-everywhere → JetBrains Mono only.
- No purple-blue gradients → flat hex palette.
- No card-in-card → flat slabs, no nested cards.
- No gray text on colored backgrounds → dim ink only on dark slate.
- No thick side-tab borders → corner brackets instead (detector-verified).
- No rounded everything → radius 0 globally.
