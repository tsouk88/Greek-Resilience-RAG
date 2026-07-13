# Domain concepts

## What the repository models
The code studies Greek regional resilience across the 2005–2022 period.
Its vocabulary comes from the RTIx framing used in the analysis scripts and generated findings:
- **Rs** — resistance to the initial shock.
- **Rc** — recovery speed.
- **D** — trajectory divergence / structural deviation after crisis.
- **RTIx** — a composite resilience-oriented score used in the downstream analysis narrative.

## Two analytical layers
### 1) Workbook-backed regional indicators
The Excel workbook contains region rows and year-by-year indicator values.
`loader.py` turns those into documents that preserve region, indicator, era, and source metadata.

### 2) Derived analytical narrative
`agent.py`, `cluster_analysis.py`, `findings.md`, and `literature_synthesis.md` layer interpretation on top of the workbook.
That layer talks about:
- resilience phases
- crisis vs. recovery periods
- national comparison rows (`Ελλάδα`)
- cluster behavior across regions
- adaptive cycle / panarchy language

## Important analytical patterns
- **Greek region fuzzy matching** is used to make user input more forgiving, especially in `/ask` and the tool functions.
- **National baseline comparison** is built into several calculations, so the region row is often interpreted relative to `Ελλάδα`.
- **Crisis-specific sheet mapping** is central to the resilience scores and uses separate sheets for economic and social views.

## Repository-specific interpretations
The generated evidence in `findings.md` and `literature_synthesis.md` repeatedly emphasizes:
- island/peripheral regions often show stronger transformative behavior in the RTIx narrative
- Attica and Central Macedonia are presented as rigid or structurally constrained metropolitan cases
- the model is framed as a response to successive shocks rather than a single crisis

## Why this matters for edits
If you change labels, sheet names, or score formulas, you are not only changing implementation details; you are also changing the analytical story the repository tells.
That means code edits often require synchronized updates to docs, generated findings, and any downstream narrative outputs.
