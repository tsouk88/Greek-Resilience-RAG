# Domain concepts

This repository documents and analyzes Greek regional resilience data. The code assumes the workbook encodes a specific academic model of regional performance across economic and social indicators.

## Regions

The app works with Greek administrative regions such as:

- Αττική
- Θεσσαλία
- Κρήτη
- Βόρειο Αιγαίο
- Κεντρική Μακεδονία
- Δυτική Μακεδονία
- Ήπειρος
- Ιόνια Νησιά
- Δυτική Ελλάδα
- Στερεά Ελλάδα
- Πελοπόννησος
- Νότιο Αιγαίο
- Ανατολική Μακεδονία και Θράκη

`main.py` uses fuzzy matching so users do not need exact spellings.

## Indicators

The code distinguishes two high-level indicator families:

- **economic** indicators
- **social** indicators

`agent.py` normalizes loose user input such as `econ`, `gdp`, `soc`, and `social welfare` into these two families.

## Time periods and eras

`loader.py` slices the workbook into three eras:

- `Expansion (Προ Κρίσης)` for 2005-2008
- `Crisis (Κρίση)` for 2009-2013
- `Recovery (Ανάκαμψη)` for 2014-2023

These eras are the basis for the retrieval chunks stored in Chroma.

## Crisis-specific sheets

`agent.py` and `rag.py` expect six workbook sheets:

- `Normal Οικον Βάση`
- `Normal Οικον Βάση - Crisis`
- `Normal Οικον Βάση - COVID`
- `Normal Κοινων Βάση`
- `Normal Κοινων Βάση - Crisis`
- `Normal Κοινων Βάση - COVID`

These support both the standard baseline view and crisis-oriented comparisons.

## Resilience logic

Several agent tools encode a resilience interpretation model:

- `calculate_resilience_score(...)` compares region performance to national values and labels regions as `Transformative`, `Adaptive`, or `Vulnerable`
- `calculate_rti_score(...)` uses composite indicators and median comparisons to classify regions as `Transformative`, `Adaptive`, `Emerging Transformative`, or `Vulnerable`
- `calculate_recovery_speed(...)` compares regional recovery against the national change and the regional median
- `analyze_socioeconomic_coupling(...)` checks whether economic recovery and social recovery move together
- `calculate_structural_shift(...)` compares pre-crisis, resistance, and recovery phases across economic and social series

These are not generic analytics helpers; they encode the project’s academic framing of resilience and trajectory divergence.

## Data model expectations

The workbook is expected to contain:

- a first column with region names
- indicator-year columns such as `... 2005`, `... 2013`, `... 2019`, `... 2022`
- national rows labeled `Ελλάδα`
- percentage columns such as `% Regional Change 2013-2019` and `% National Change 2013-2019`

Many functions assume those labels exist exactly and will fail if the workbook schema changes.

## Source references

- `loader.py`
- `agent.py`
- `README.md`
