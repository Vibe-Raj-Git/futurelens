# FutureLens Architecture

## Layers

### Layer 1 — Astronomy

- `futurelens.astronomy.ascendant` — Sidereal ascendant via Swiss
  Ephemeris
- `futurelens.astronomy.ephemeris` — Swiss Ephemeris provider for
  grahas, sunrise, sunset
- `futurelens.astronomy.mock_ephemeris` — deterministic test double

### Layer 2 — Natal chart

- `futurelens.grahas` — the nine grahas with nakshatra derivation,
  dignity (`is_exalted`, `is_debilitated`, `is_own_sign`,
  `is_moolatrikona`, `is_strong_in_sign`), relations (`conjunct`,
  `mutual_aspect`, `exchange`), and formatting
- `futurelens.houses.resolver` — whole-sign houses and lords
  (Parashara)
- `futurelens.upagraha` — Sun-derived chain (`sun_chain.py`) and
  Kalavela portions (`kalavela.py`)
- `futurelens.dasha` — Vimshottari Mahadasha / Antardasha /
  Pratyantardasha
- `futurelens.ashtakavarga` — BAV and SAV tables, per-graha and
  summed; `compute_ashtakavarga(chart)` returns a report with
  `.sav.bindus_by_sign` indexed by sign
- `futurelens.transits` — current transit positions relative to
  natal chart (raw positions)
- `futurelens.gochara` — classical transit evaluation: favourable /
  unfavourable tables, Vedha, SAV modulation, aspects on natal
  houses, motion state, Sade Sati. Produces `GocharaTransit` objects
  with a five-level verdict
- `futurelens.yogas` — nine yoga detectors, each returning a
  `YogaResult` with `present`, `conditions_met`, `conditions_failed`
- `futurelens.chart.cast_chart` — the top-level pipeline

### Layer 3 — Evidence

- `futurelens.evidence.rules` — individual rule modules implementing
  the `EvidenceRule` protocol
- `futurelens.evidence.graph` — the aggregator with subject-aware
  contradiction detection. Two evidence items contradict only if
  they share a domain, have opposite directions, and derive the same
  subject from their notes

### Layer 4 — Domains

Each domain is a self-contained engine with its own houses,
significators, rule set, and weighting.

- `futurelens.domains.wealth` — wealth domain (houses 2, 5, 9, 11)
- `futurelens.domains.career` — career domain (houses 10, 6, 2, 11)
- `futurelens.domains.family` — family domain (houses 2, 4, 5, 7,
  9, 12)
- `futurelens.domains._weighting` — shared weighting helpers

Each domain produces evidence items carrying the full semantic
triple (`subject`, `finding`, `interpretation`), a `weight`
(`STRUCTURAL` / `SUPPORTING` / `MODIFIER` / `STRONG_MODIFIER`),
and provenance (`rule_id`, `rule_version`, `tradition`,
`classical_basis`).

### Layer 5 — Explanation

- `futurelens.llm.contract` — the payload safety guard
  (`assert_payload_safe`)
- `futurelens.llm.prompt` — the strict system prompt and the
  request builder. Translates deterministic evidence into the
  semantic payload the LLM receives. The system prompt states the
  weight hierarchy, the priority rules per domain, the citation
  contract, and the no-event-predictions rule
- `futurelens.llm.backends` — pluggable backends: `template`
  (deterministic, no dependencies), `gemini` (via `google-genai`),
  registry for lookup
- `futurelens.llm.explainer` — the orchestration entry point

### Validation

- `futurelens.validation.invariants` — cross-cutting assertions that
  hold across all charts (e.g. dasha timeline monotonicity, SAV
  total = 337)

## Data flow

birth data (datetime, latitude, longitude)
|
v
astronomy (Swiss Ephemeris: ascendant, sunrise/sunset, grahas)
|
v
natal chart (whole-sign houses, lords, upagrahas, nakshatras)
|
v
derived layers (dasha timeline, ashtakavarga, transits, gochara, yogas)
|
v
evidence (typed, versioned, provenance-carrying items;
subject-aware contradiction detection)
|
v
domain engines (wealth / career / family evaluate their rules
against the chart and filter gochara and yoga
evidence to their house set)
|
v
semantic payload (subject / finding / interpretation triple per
evidence item; weight tier preserved)
|
v
LLM request (system prompt + user prompt + JSON payload)
|
v
backend (template OR gemini)
|
v
Explanation (text + rule_ids_cited + evidence_count +
contradiction_count + backend)

text

## SAV composition

Sarvashtakavarga bindus are a sign-level quantity (12 rasis, 337
total). They enter the reading in three places:

1. **Natal house-lord findings.** Each house-lord rule reports the
   SAV bindu count of the sign the house falls in. Phrasing is
   sign-explicit: *"The 2nd house falls in Sagittarius, which holds
   30 SAV bindus (VERY_STRONG)."*
2. **Gochara transit findings.** Each Gochara item reports the SAV
   bindu count of the transited sign.
3. **Domain weighting.** SAV is one input to house-lord weighting,
   not a verdict.

The `Chart.ashtakavarga()` method caches the report on the instance,
so the three domain engines and the Gochara engine share one
computation.

## Yoga promotion flow

Yoga detectors run once per chart via `detect_yogas(chart)`,
returning a `YogaReport`. Each domain declares a
`<DOMAIN>_RELEVANT_YOGAS` tuple in its `definitions.py`. The
`<DOMAIN>-YOGA-PROMOTION-001` rule iterates the tuple, and any
yoga with `present=True` is promoted to a `STRUCTURAL` evidence
item in that domain. The classical basis from the yoga definition
carries through to the evidence provenance.

The LLM prompt states domain-specific priorities (for WEALTH,
prefer Dhana Yoga and Lakshmi Yoga over Raja Yoga) so the model
leads with the domain-relevant structural finding when several are
present.

## Adding a new domain

1. Create `futurelens/domains/<name>/definitions.py` with houses,
   significators, reasons, and a `<DOMAIN>_RELEVANT_YOGAS` tuple.
2. Create `futurelens/domains/<name>/rules.py` with rule functions.
   Each returns a list of `Evidence`, populating the semantic
   triple and the `notes` fields.
3. Create `futurelens/domains/<name>/engine.py` with a
   `build_<name>_report(chart, when)` function.
4. Add a `chart.<name>()` method in `chart.py`.
5. Add an `explain_<name>()` convenience method in `chart.py` if
   desired.
6. Add tests.
7. Document the rules in `rulebook/`.

## Adding a new rule

1. Choose a `rule_id` that matches the existing naming scheme:
   `<DOMAIN>-<TOPIC>-<KIND>-<NNN>`.
2. Cite the classical basis (`BPHS ch. X`, `Phaladeepika ch. Y`).
3. Implement the rule as a function returning a list of `Evidence`.
   Populate `subject`, `finding`, `interpretation`, and any
   subject-derivation notes needed for contradiction detection.
4. Assign a `weight` tier: `STRUCTURAL`, `SUPPORTING`, `MODIFIER`,
   or `STRONG_MODIFIER`.
5. Wire it into the relevant domain engine.
6. Add tests for positive and negative cases. If the rule detects a
   yoga, test against a reference chart and a regression chart.
7. Document the rule in `rulebook/`.

## Adding a new yoga

1. Create `futurelens/yogas/rules/<yoga_name>.py` with a `detect(chart)
   -> YogaResult` function.
2. Add the definition to `futurelens/yogas/definitions.py` (id,
   name, classical_basis, category).
3. Register the detector in `futurelens/yogas/detector.py`'s
   `ALL_DETECTORS` tuple.
4. If the yoga is domain-relevant, add its ID to the appropriate
   `<DOMAIN>_RELEVANT_YOGAS` tuple.
5. Add tests. Test-first where possible: write the failing test on
   a known chart, then implement the detector.

## Design principles

1. Calculation is separate from interpretation.
2. Interpretation is separate from activation.
3. Activation is separate from forecast.
4. Every evidence item carries provenance: rule ID, classical basis,
   tradition, version.
5. The LLM explains; it does not generate astrology.
6. Contradictions are preserved, not averaged.
7. The template backend makes the project usable without an API key.