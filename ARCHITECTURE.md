@'
# FutureLens Architecture

## Layers

### Layer 1 - Astronomy

futurelens.astronomy.ascendant - Sidereal ascendant via Swiss Ephemeris.
futurelens.astronomy.ephemeris - Swiss Ephemeris provider for grahas, sunrise, sunset.

### Layer 2 - Natal chart

futurelens.grahas - the nine grahas with nakshatra derivation.
futurelens.houses.resolver - whole-sign houses and lords.
futurelens.upagraha - Sun-derived chain and Kalavela portions.
futurelens.dasha - Vimshottari Mahadasha / Antardasha / Pratyantardasha.
futurelens.transits - current positions relative to natal chart.
futurelens.chart.cast_chart - the top-level pipeline.

### Layer 3 - Evidence

futurelens.evidence.rules - individual rules implementing the EvidenceRule protocol.
futurelens.evidence.graph - the aggregator with subject-aware contradiction detection.

### Layer 4 - Domains

futurelens.domains.wealth - the wealth domain engine.

### Layer 5 - Explanation

futurelens.llm.contract - the payload safety guard.
futurelens.llm.prompt - the strict system prompt and request builder.
futurelens.llm.backends - pluggable backends (template in v0.1).
futurelens.llm.explainer - the orchestration entry point.

## Data flow

1. cast_chart() computes everything deterministic.
2. A user asks a question about a moment.
3. The relevant domain engine evaluates its rules and produces a WealthReport.
4. The report is turned into an LLMRequest with a sanitized payload.
5. A backend (template or real LLM) generates a response.
6. The response is returned as an Explanation.

## Adding a new domain

1. Create futurelens/domains/<name>/definitions.py with houses, planets, reasons.
2. Create futurelens/domains/<name>/rules.py with rule functions.
3. Create futurelens/domains/<name>/engine.py with a build_<name>_report function.
4. Add a chart.<name>() method in chart.py.
5. Add tests.
6. Document the rules in rulebook/.

## Adding a new rule

1. Choose a rule_id that matches the existing naming scheme.
2. Cite the classical basis.
3. Implement the rule as a function returning a list of Evidence.
4. Wire it into the relevant domain engine.
5. Add tests for positive and negative cases.
6. Document the rule in rulebook/.
'@ | Set-Content -Path ARCHITECTURE.md -Encoding utf8