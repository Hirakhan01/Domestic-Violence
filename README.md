# Domestic Homicide in England & Wales — Investigative Dossier

A data-driven case-file website built on the ONS Homicide Index, covering eleven years of domestic homicide statistics (2014–15 to 2024–25) across England and Wales.

---

## What this is

This project presents cleaned, structured data from the ONS Homicide Index appendix tables (year ending March 2025) in an investigative dossier format — designed to read as credible and analytically serious rather than decorative. The visual language draws on case-file aesthetics: manila tones, monospace annotation, stamped callouts, and a chain-of-custody methodology section.

The current release is a single-file HTML prototype (`dossier-preview.html`). The Next.js site is in progress.

---

## Pages

| Tab | Content |
|-----|---------|
| 01 — Overview | Headline KPIs, eleven-year domestic homicide trend by sex pairing, analyst note |
| 02 — Who and how | Victim-suspect relationship breakdowns for female and male victims; partner/ex-partner trend |
| 03 — Circumstances | What sparked acquainted-victim homicides; quarrel/revenge trend over time |
| 04 — The justice gap | Murder convictions vs. no-suspect-charged over eleven years; conviction and unsolved rates |
| 05 — Methodology | Chain-of-custody documentation: source, cleaning pipeline, known issues, data limitations |

---

## Data pipeline

### Source
`homicideinenglandandwalesappendixtablesyemar2025finalv2.xlsx` — ONS Homicide Index, year ending March 2025. Not included in this repository (publicly available from the ONS website).

### Cleaning
`clean_homicide_data.py` reads four worksheets from the ONS workbook and outputs four long-format CSVs:

| CSV | Source sheet | Contents |
|-----|-------------|----------|
| `domestic_trends.csv` | Table 34 | Domestic homicide counts by victim sex, suspect sex, year |
| `victim_relationships.csv` | Worksheet 14 | Victim-suspect relationship by victim sex and year |
| `suspect_outcomes.csv` | Table 25 | Court outcomes and uncharged cases by year |
| `circumstances.csv` | Worksheet 17 | Circumstance of killing for acquainted/unacquainted victims by year |

Key cleaning steps:
- Fixed row targeting to handle merged headers and varying layout between sheets
- Stripped ONS footnote markers (`[note 12]`, `[x]`) via regex; suppressed cells set to `0` and flagged
- Reshaped wide-format (one column per year) into long-format (`category, year, count`)
- Verified reshaped totals against ONS published summary commentary

### Analysis
`analyze_homicide_data.py` reads the four CSVs and derives:
- Year-on-year and decade-long percentage changes
- Sex-pairing shares and trends
- Conviction and unsolved rates
- Narrative summary points

Output: `findings.json` — the single source of truth consumed by the website.

### Known issue caught during cleaning
An early pass on the suspect-outcomes worksheet mis-set the starting column index, shifting every year's count one position left. This was caught because the resulting 2014–15 murder conviction figure didn't match the ONS published commentary. The fix was a one-line column offset correction. Documented here rather than quietly buried.

---

## Tech stack

### Current prototype
- Plain HTML/CSS/JS — single self-contained file, no build step
- [Chart.js 4.4.1](https://www.chartjs.org/) via CDN — line and bar charts
- [IBM Plex Mono](https://fonts.google.com/specimen/IBM+Plex+Mono), [Spectral](https://fonts.google.com/specimen/Spectral), [Inter](https://fonts.google.com/specimen/Inter) via Google Fonts

### Planned Next.js site
- Next.js (App Router)
- Tailwind CSS — same design tokens as the prototype
- Recharts / D3 — per chart as fits
- Deployed via Vercel

---

## Design tokens

```css
--paper:      #EFEAE0   /* page background */
--card:       #F7F3E9   /* panel background */
--ink:        #211F1C   /* primary text */
--ink-mute:   #6B665A   /* secondary text, labels */
--rule:       #C9BFA8   /* light borders */
--rule-strong:#A89F8C   /* stronger dividers */
--stamp:      #8C2F2A   /* red accent — callouts, stamps */
--stamp-bg:   #F3E3DF   /* stamp background */
--sage:       #54624A   /* green accent — positive/declining trend */
--sage-bg:    #E7EBE0   /* sage background */
```

Fonts: `Spectral` (serif headings and body), `IBM Plex Mono` (labels, tabs, monospace annotations), `Inter` (general UI).

---

## Features

- **Cross-page sex filter** — persistent All / Female victims / Male victims toggle that updates KPI cards and relationship tables across panels. Circumstances and justice-gap panels surface a note where the source data isn't split by sex, rather than fabricating a breakdown.
- **Evidence tags** — angled `IBM Plex Mono` callouts with dotted leader lines on the 64% female-victim/male-partner KPI and the justice-gap chart.
- **Analyst note** — first-person interpretive paragraph on the Overview panel, styled distinctly from the auto-generated narrative blocks.
- **Methodology tab** — chain-of-custody framing with a numbered processing log and an honest account of the column-misalignment bug caught during cleaning.
- **Live timestamp** — footer renders the current date from `new Date()` on load.

---

## Running locally

No build step required for the prototype:

```bash
# Just open the file in a browser
open dossier-preview.html
```

For the Next.js site (once scaffolded):

```bash
npm install
npm run dev
# → http://localhost:3000
```

---

## Deploying

**Netlify Drop (quickest)**
Drag `dossier-preview.html` onto [app.netlify.com/drop](https://app.netlify.com/drop) — live URL in under 30 seconds, no account required.

**GitHub Pages**
Push to a repo, enable Pages under Settings → live at `yourusername.github.io/repo-name`.

**Vercel (for the Next.js site)**
```bash
vercel
```

---

## Data caveats

- All counts are for England and Wales only — no sub-national breakdown is available at source.
- Counts below ONS suppression thresholds appear as `0` in the CSVs and are flagged.
- The circumstances and suspect-outcomes tables are not split by victim sex in the published ONS data. The sex filter on those panels is intentionally inert.
- The `relationships` totals (155 female victims, 366 male victims) are drawn from Worksheet 14 and include cases where the relationship was not known or no suspect was charged — they are not domestic-homicide-only figures.

---

## Source

ONS Homicide Index, appendix tables, year ending March 2025.
Publicly available at [ons.gov.uk](https://www.ons.gov.uk/peoplepopulationandcommunity/crimeandjustice/datasets/appendixtableshomicideinenglandandwales).

---

*This project is a portfolio piece. It does not represent official ONS or Home Office analysis.*
