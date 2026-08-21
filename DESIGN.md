# DESIGN.md — Dashboard PDAD // BUKU SOP

<!-- impeccable:design-schema 1 -->

## World

**Buku SOP** (user-pinned direction; replaces Data Terminal, seed 02dade84). The dashboard is the unit's own SOP manual made live — a book of answers the Duktek opens every day, where each kendala has a numbered handling procedure. It is an official document, not a screen: chapter numbering, margin steps, ink-stamp marks, ruled dividers.

## Mode

**Operate** (with a Read flavor). The Duktek completes a task — find the handling steps for a kendala, read SLA status, trace tickets — in the register of the office's own procedures.

## Palette

| Token | Hex | Role |
|---|---|---|
| `--sop-bg` | `#F5EFE0` | Cream paper field (ground) |
| `--sop-panel` | `#FBF7EC` | Panel / card paper |
| `--sop-panel2` | `#EDE4CE` | Sidebar aged paper |
| `--sop-line` | `#D8CDB2` | Hairline rule |
| `--sop-line-strong` | `#B9AB8A` | Strong border |
| `--sop-ink` | `#23314F` | Navy ink (primary text) |
| `--sop-ink-dim` | `#66708A` | Secondary text / labels |
| `--sop-red` | `#B23A2F` | Stamp red (action / accent) |
| `--sop-gold` | `#A87F2D` | Annotation / watch |
| `--sop-green` | `#2F7D4F` | Clear / OK |
| `--sop-teal` | `#1F6F8F` | Katalog labels |

Color strategy: **Restrained** — paper + navy ink, one saturated accent (stamp red) used as ink marks, gold/green for status. Red appears as stamp-like marks (chapter eyebrows, entry numbers, TERVERIFIKASI stamp), never as a scattered highlight.

## Typography

- **Chapter titles / headings:** Source Serif 4 (900/700) — the document voice.
- **Body / UI / labels:** Source Sans 3 (400/600/700), tabular numerals via `font-feature-settings: "tnum" 1`.
- **Form values / entry numbers:** JetBrains Mono (700) — reads as typed form fields.
- **Scale:** KPI value 1.9rem/900 serif; page title 1.7rem/900; section eyebrow 0.78rem/700 tracked +0.14em uppercase red; body 0.84–0.85rem; micro-labels 0.66–0.72rem tracked +0.14–0.22em uppercase.

## Shape & Components

- **Corners:** square (`border-radius: 0`) — document edges.
- **Document header:** bordered block: kicker (unit, red tracked caps) → serif title → italic subtitle → meta row (nomor dok, edisi, data, status) → red circular **TERVERIFIKASI ink stamp** (rotated −8°, 118px, double-ring) top-right.
- **KPI form-field entry:** uppercase micro-label, 1.9rem serif value, sub-line, 2px bottom rule in tone (red/navy/gold/green).
- **Solution entry card:** 1px border + 3px navy top rule; serif title; meta row (teal katalog caps + red ticket count); italic summary; numbered steps `<ol>` with **margin column counters** (decimal-leading-zero, mono); gold ANOTASI block with dotted top border; red serif entry number (01–08) in left margin.
- **Ruled divider:** `◆` diamond between single rule and double rule.
- **Empty state:** dashed-border blank form note, italic, `— msg —`.
- **Buttons:** outlined navy, uppercase tracked; hover inverts to navy fill.
- **Inputs:** borderless with 2px navy bottom rule (form field); focus turns red; mono value.

## Typographic / Layout Rhythm

- Chapter eyebrows `BAB I · …` red tracked caps before each block; chart/dataframe sections numbered `PASAL 1..7`.
- One spacing rhythm: ~10px cards, ~22px section gaps, more space above headings.
- Sidebar = `BUKU SOP` serif masthead + `DAFTAR ISI` radio (BAB I–IV) + `// LAMPIRAN FILTER` (tanggal, kategori, duktek) + entry counter.

## Navigation / Topology

4 chapters (radio in sidebar), BAB I default:

1. `BAB I — SCAN SOLUSI` — hero: KPI entry row (4) → ruled divider → search form (`LANGKAH 0 — ISI LEMBAR PENCARIAN`) → solution entries (numbered pasal) → appendix tickets table.
2. `BAB II — RINGKASAN` — KPI row, tren line chart, kategori bar chart, top masalah/pelapor dataframes.
3. `BAB III — SLA & KINERJA` — KPI row, bucket bar chart, SLA-per-kategori, kinerja per duktek.
4. `BAB IV — EKSPLORASI` — filter inputs (pelapor/masalah/nomor), full dataframe, CSV download.

## Interaction & State

- **Focus:** input bottom rule turns stamp red (active "writing on the form" state).
- **Buttons:** example scan chips fill the search form and rerun (session_state `scan_fill` → `scan_input`).
- **Hover:** buttons invert to navy fill; radio labels turn red.
- **Tabs:** active tab red underline.
- **State language:** empty form = `Lembar pencarian kosong…`; no match = dashed blank note; result count in chapter eyebrow.

## Responsive

- Full-bleed wide layout; KPI row collapses to 4-up → stacks on narrow viewports via Streamlit columns.
- Charts and dataframes stretch to container; chart canvases get panel paper + hairline border.

## Implementation Notes (Streamlit)

- Light paper theme via `.streamlit/config.toml` (`base="light"`, cream palette, `font="sans serif"`) **plus** CSS injection with `!important` overrides (background, inputs, buttons, sidebar, dataframes, tabs, charts).
- All custom HTML escaped via `html.escape` (user data rendered safely).
- `width="stretch"` used (no deprecated `use_container_width`).
- Google Fonts `@import` (Source Serif 4 / Source Sans 3 / JetBrains Mono); system fallbacks cover offline.
- Data cached `ttl=3600`; `probis` empty → `-` per user document convention.

## Anti-Patterns Guarded

- No generic cream+serif+terracotta AI look → the world is a **specific** official SOP manual: chapter numbering, margin step counters, ink-stamp mark, document meta block. These devices carry the identity, not a palette alone.
- No Inter-everywhere → Source Sans 3 / Source Serif 4 / JetBrains Mono.
- No purple-blue gradients → flat ink palette.
- No card-in-card → flat document entries.
- No gray text on colored backgrounds → dim ink only on paper.
- No thick side-tab borders → top-rule + margin counters instead (detector-verified).
- No rounded everything → radius 0 globally.
