---
type: Domain model
title: Domain concepts
description: Greek regional resilience model — the 13 regions and national baseline, the Expansion/Crisis/Recovery era timeline, the RTIx resistance/recovery/divergence metrics and vulnerability-adjusted classification, and the adaptive-cycle framing the analysis scripts and agent tools encode.
tags: [domain, resilience, rti, greek-regions, eras, vulnerability-index, adaptive-cycle, classification]
verified:
  - by: openwiki/0.4.3
    at: 2026-09-01T11:19:44.752Z
sources:
  - id: openwiki-source-ea70eb6c045047448e446296
    resource: repo://.gitignore
  - id: openwiki-source-eca60e2ced68ba99bd0ac710
    resource: repo://agent.py
  - id: openwiki-source-a8c63260b711c81dc8d31ae6
    resource: repo://cluster_analysis.py
  - id: openwiki-source-e1d4438011ac1fee7dcab58d
    resource: repo://loader.py
  - id: openwiki-source-833e692518af9eeaf8564cc6
    resource: repo://main.py
  - id: openwiki-source-d37a7a6f6bf2bc7a45be6269
    resource: repo://rag.py
generated: { by: "openwiki/0.4.3", at: "2026-09-01T11:19:44.752Z" }
---

# Domain concepts

The repository studies **Greek regional resilience across 2005–2022** through the lens of a workbook-driven academic model. The workbook is the source of truth; the agent tools and indexing pipeline turn its rows into two things: retrievable region/indicator/era chunks (ChromaDB) and a set of computed resilience metrics and classifications. The vocabulary below is what the tools, the `system_prompt`, and the generated narrative all share.

## Greek regions and the national baseline

The system works with the 13 Greek administrative regions plus a national baseline row `Ελλάδα`. The 13-region list is hard-coded in `main.py` for `/ask` fuzzy enrichment and is also the population of regions the agent tools operate over (excluding the `Ελλάδα` national row):

- Αττική
- Κεντρική Μακεδονία
- Δυτική Μακεδονία
- Ανατολική Μακεδονία και Θράκη (abbreviated ΑΜΘ in `cluster_analysis.py`)
- Ήπειρος
- Θεσσαλία
- Ιόνια Νησιά
- Δυτική Ελλάδα
- Στερεά Ελλάδα
- Πελοπόννησος
- Βόρειο Αιγαίο
- Νότιο Αιγαίο
- Κρήτη

`Ελλάδα` is the **national baseline**. It is treated specially in every scoring tool: a region's metrics are computed, then compared to the national row's same columns. In `loader.py`, `rag.py`, `calculate_rti_score`, `calculate_rtix_score`, and `cluster_analysis.py`, the `Ελλάδα` row is either excluded from regional medians/clusters or used as the comparison anchor. Tools resolve loose user phrasing to exact region names via `thefuzz.process.extractOne` with a score threshold of 70; `main.py`'s `/ask` path uses `thefuzz.fuzz.partial_ratio` above 80 against this 13-region list.

## Eras and crisis periods

The workbook is sliced into three eras used for both retrieval and analysis. `loader.py` defines the year ranges; `agent.py`'s `search_regions` maps user terms (English and Greek) to the canonical era labels.

<!-- openwiki: mermaid parse failed and this diagram was converted to a text fence so it does not break rendering. Fix the diagram source and restore the mermaid fence. Parser error: Heuristic: an unescaped angle bracket inside a label breaks rendering; rephrase the label. -->
```text
flowchart LR
    EXP["Expansion (Προ Κρίσης)<br/>2005-2008"] --> CRS["Crisis (Κρίση)<br/>2009-2013"]
    CRS --> REC["Recovery (Ανάκαμψη)<br/>2014-2023"]
    REC -.-> COVID["COVID sub-shock<br/>2019-2020 inside Recovery"]
```

*Figure: the era/phase model. The long Recovery era (2014–2023) carries an internal COVID sub-shock (2019–2020) that the crisis-specific sheets and tools model separately from the 2008–2013 financial crisis.*

- **Expansion (Προ Κρίσης)** — 2005, 2006, 2007, 2008 (pre-crisis baseline).
- **Crisis (Κρίση)** — 2009–2013 (the financial crisis resistance window).
- **Recovery (Ανάκαμψη)** — 2014–2023 (recovery window; 2020–2022 is the COVID-era recovery sub-window).

The crisis-specific analysis also distinguishes the **financial crisis** (resistance window 2008–2013, recovery 2013–2019) from the **COVID crisis** (resistance 2019–2020, recovery 2020–2022). `calculate_crisis_comparison` compares resistance across the two shocks to measure a "learning effect."

## Indicators and the normalization helper

Two indicator families are first-class:

- **economic** — read from `Normal Οικον Βάση` sheets and the composite `Σύνθετος Οικονομικός Δείκτης`.
- **social** — read from `Normal Κοινων Βάση` sheets and the composite `Σύνθετος Κοινωνικός Δείκτης`.

`normalize_indicator(indicator_type)` in `agent.py` maps loose user input to these families: `economical`, `econ`, `economy`, `gdp` → `economic`; `societal`, `soc`, `society`, `social welfare` → `social`; anything else is returned unchanged (which is how `calculate_rtix_score`'s `composite` branch stays reachable). Six workbook sheets back this split — the base sheets plus `- Crisis` and `- COVID` variants for each family.

## The core RTIx metrics: Rs, Rc, D

The resilience vocabulary is built on three primitive deltas, all derived from a per-family **composite indicator** column (`Σύνθετος Οικονομικός/Κοινωνικός Δείκτης`):

- **Rs (Resistance)** — `composite[2013] − composite[2008]`. Resistance to the initial (financial) shock.
- **Rc (Recovery)** — `composite[2019] − composite[2013]`. Recovery speed after the financial crisis.
- **D (Divergence)** — `(composite[2022] − composite[2005])_region − (composite[2022] − composite[2005])_national`. Structural trajectory divergence from the national baseline across the whole 2005–2022 span.

These are computed identically in `calculate_rti_score` and `calculate_rtix_score`. Regional medians of Rc and D (excluding `Ελλάδα`) are the comparison anchors for the RTI classification; the national row is the comparison anchor for D itself.

## The RTIx score and its vulnerability adjustment

`calculate_rtix_score(region, indicator_type)` composes the three primitives into a single score and then penalizes it for vulnerability:

```
RTIx          = 0.50*D + 0.30*Rc + 0.20*Rs
RTIx_adjusted = RTIx * (1 - v_norm)
```

where the **vulnerability normalization** `v_norm` is derived from a region's negative resistance across both shocks, scaled by the worst region:

- `fin_vuln = |Resistance (2008-2013)|` if that resistance is negative, else 0
- `cov_vuln = |Resistance (2019-2020)|` if that resistance is negative, else 0
- `cvs = 0.5*fin_vuln + 0.5*cov_vuln`
- `v_norm = cvs / max(cvs over all regions)` (0 if the max is 0)

So a more vulnerable region has its RTIx pulled *down* by up to `(1 − v_norm)`. The classification is applied to the **adjusted** score:

<!-- openwiki: mermaid parse failed and this diagram was converted to a text fence so it does not break rendering. Fix the diagram source and restore the mermaid fence. Parser error: Heuristic: an unescaped angle bracket inside a label breaks rendering; rephrase the label. -->
```text
flowchart TD
    S{"RTIx_adjusted ?"} --> A["> 2: Strongly Transformative"]
    S --> B["> 0: Moderately Transformative"]
    S --> C["> -2: Stagnant"]
    S --> D["<= -2: Declining Trajectory"]
```

*Figure: RTIx classification thresholds applied to the vulnerability-adjusted RTIx score.*

`calculate_rtix_score` also supports an `indicator_type` of `composite`, which reads the `RTI_Composite` column from the economic base sheet rather than either family's composite indicator.

## Related scoring tools and their classifications

### `calculate_rti_score` — median-based trajectory classification
Uses the same Rs/Rc/D primitives but classifies against the **regional medians** of Rc and D (excluding `Ελλάδα`):

| Rc vs median Rc | D vs median D | Classification |
|---|---|---|
| > median | > median | Transformative |
| > median | ≤ median | Adaptive |
| ≤ median | > median | Emerging Transformative |
| ≤ median | ≤ median | Vulnerable |

### `calculate_resilience_score` — national-baseline classification and the sheet→crisis map
Compares a region's resistance and recovery to the national row's corresponding percentage columns and classifies as **Transformative** (both above national), **Adaptive** (either above), or **Vulnerable** (neither). The tool selects the sheet and columns via a `(indicator_type, crisis_type)` map. `financial` and `crisis` collapse onto the same `- Crisis` sheets; `covid` uses the `- COVID` sheets:

| indicator | crisis | sheet | resistance col | recovery col | national % cols |
|---|---|---|---|---|---|
| economic | financial / crisis | `Normal Οικον Βάση - Crisis` | `Resistance (2008-2013)` | `Recovery (2013-2019)` | `% National Change 2008-2013` / `% National Change 2013-2019` |
| economic | covid | `Normal Οικον Βάση - COVID` | `Resistance (2019-2020)` | `Recovery (2020-2022)` | `% National Change 2019-2020` / `% National Change 2020-2021` |
| social | financial / crisis | `Normal Κοινων Βάση - Crisis` | `Resistance (2008-2013)` | `Recovery (2013-2019)` | same economic-crisis pattern |
| social | covid | `Normal Κοινων Βάση - COVID` | `Resistance (2019-2020)` | `Recovery (2020-2022)` | same economic-covid pattern |

`indicator_type` is validated to `economic`/`social` (via `normalize_indicator`); `crisis_type` is validated against `crisis`, `covid`, `financial`. Invalid inputs return an error string rather than raising.

### `calculate_recovery_speed` — recovery-speed labels
Compares regional `% Regional Change 2013-2019` against both the national `% National Change 2013-2019` and the regional median of the same column, yielding **Strong Recovery** (above both), **Solid Recovery** (above national only), **Partial Recovery** (above median only), or **Critical State** (below both).

### `calculate_vulnerability_index` — standalone vulnerability label
Computes the same `cvs = 0.5*fin_vuln + 0.5*cov_vuln` used inside RTIx and classifies it directly: **High Vulnerability (Systemic Fragility)** if `cvs > 15`, **Moderate Vulnerability (Sensitive to Shocks)** if `cvs > 5`, else **Low Vulnerability (Robust Structure)**.

### `calculate_crisis_comparison` — learning effect
`Learning Delta = Resistance (2019-2020) − Resistance (2008-2013)`. Verdict: `> 5` → **Strong Learning Effect**; `> 0` → **Moderate Improvement**; else → **Structural Vulnerability**. The agent `system_prompt` flags any Learning Delta outside `±5` as a signal to prioritize.

### `analyze_socioeconomic_coupling` and `calculate_structural_shift`
- `analyze_socioeconomic_coupling` compares regional economic vs social `% Regional Change 2013-2019` against their national counterparts, labeling **Balanced Recovery**, **Social Lag**, **Economic Lag**, or **Double Decline**.
- `calculate_structural_shift` compares pre-crisis/resistance/recovery phase values across the financial and COVID windows for both families, emitting adaptive-cycle traits like *More Robust*, *Faster Recovery*, *Structural Shift*, and *Competitive*.

## Adaptive-cycle framing

The agent `system_prompt` instructs the model to interpret findings through **Adaptive Cycle Theory**, using the phases **Release (Ω)**, **Reorganization (α)**, **Exploitation (r)**, and **Conservation (K)**, and to conclude each analysis with a verdict of *Transformative Resilience* or *Adaptive Recovery*. The research protocol is a three-phase state machine — exploratory, diagnostic, synthesis — that always ends by archiving the verdict via `save_finding`.

`cluster_analysis.py` (a tracked offline script, unlike its gitignored PNG outputs) hard-codes the 13 regions' Rs/Rc/D values and KMeans-clusters them into four named archetypes: **Δομική Στασιμότητα** (Structural Stagnation), **Τουριστικός Μετασχηματισμός** (Tourism Transformation), **Αναδυόμενη Προσαρμογή** (Emerging Adaptation), and **Μητροπολιτικό Παράδοξο** (Metropolitan Paradox).

## Source-of-truth and generated-artifact boundaries

- **Workbook** (`data/stats.xlsx` via `FILE_PATH`) is the source of truth. `loader.py` and every workbook-reading tool assume exact Greek sheet and column labels (`Resistance (2008-2013)`, `% Regional Change 2013-2019`, `Σύνθετος Οικονομικός Δείκτης`, etc.). Schema drift breaks both indexing and tools.
- **`findings.md`, `literature_synthesis.md`, and `deepresearch.py` are gitignored generated artifacts**, not tracked source. They are produced by the agent (`save_finding`) or by `deepresearch.py` and should not be treated as authoritative; do not cite them as evidence of system behavior.
- **`cluster_analysis.py` is tracked**, but its outputs (`cluster_scatter.png`, `cluster_radar.png`) are gitignored. Its region-score values are hard-coded from the generated `findings.md`, so it documents the narrative rather than re-deriving it from the workbook.

Changing region labels, sheet names, or any of the score formulas changes the analytical story the repository tells, not just implementation details — such edits usually require synchronized updates to the workbook, the indexing pipeline, the agent tools, and any downstream narrative.
