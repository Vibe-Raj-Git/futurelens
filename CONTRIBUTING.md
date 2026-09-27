# Contributing to FutureLens

This document explains the architecture of FutureLens, the
conventions the code follows, and how to extend the engine without
breaking the design principles that make it work.

If you are reading this file because you just cloned the repository,
start with the section **Getting started**. If you are about to add
a rule or a domain, read **Architecture** and **How to add a rule**
first.

---

## Table of contents

1. [What FutureLens is](#what-futurelens-is)
2. [Getting started](#getting-started)
3. [Architecture](#architecture)
4. [The six-phase semantic pipeline](#the-six-phase-semantic-pipeline)
5. [Design principles](#design-principles)
6. [How to add a rule](#how-to-add-a-rule)
7. [How to add a domain](#how-to-add-a-domain)
8. [How to add a yoga](#how-to-add-a-yoga)
9. [The weight tier](#the-weight-tier)
10. [Provenance and traceability](#provenance-and-traceability)
11. [Testing](#testing)
12. [Coding style](#coding-style)
13. [Deployment](#deployment)
14. [Common pitfalls](#common-pitfalls)

---

## What FutureLens is

FutureLens is a deterministic Jyotish forecasting engine with an
LLM interpretation layer.

The engine computes an astrological chart from birth data. It
evaluates classical Jyotish rules against that chart. It produces
typed, traceable evidence items. The LLM reads that evidence and
explains it in plain language. The LLM does not generate astrology.

Two things matter more than anything else in this project:

**Correctness.** Every number, every classification, every direction
must be traceable to a classical rule. If a fact cannot be verified
against a classical source, it does not go into the engine.

**Separation of layers.** Calculation is separate from
interpretation. Interpretation is separate from activation.
Activation is separate from forecast. The LLM only produces
explanations. It never produces facts.

If a change violates either principle, it should not be merged.

---

## Getting started

```powershell
# Clone and activate
git clone https://github.com/Vibe-Raj-Git/futurelens.git
cd futurelens
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install
pip install -e ".[dev,swiss,gemini]"

# Add your Gemini key
Copy-Item .env.example .env
# Edit .env and set GEMINI_API_KEY

# Verify
pytest -q
```

Expected: all tests pass. If Swiss Ephemeris data files are missing,
the tests will still pass using the fallback ephemeris, but the
calculations will be slightly less accurate.

To run the local development stack:

```powershell
# Terminal 1 - backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 - frontend
cd frontend
npm run dev
```

Open `http://localhost:5173/`.

To run the production container locally:

```powershell
docker compose up --build
```

Open `http://localhost:8000/`.

---

## Architecture

FutureLens is organised in five layers. Each layer depends only on
the layers below it.

```
Layer 5 — LLM explanation
    src/futurelens/llm/

Layer 4 — Domain engines
    src/futurelens/domains/

Layer 3 — Evidence graph
    src/futurelens/evidence/

Layer 2 — Natal chart
    src/futurelens/grahas/, houses/, upagraha/, dasha/, transits/,
                 yogas/, ashtakavarga/

Layer 1 — Astronomy
    src/futurelens/astronomy/
```

### Layer 1 — Astronomy

Wraps Swiss Ephemeris. Computes the ascendant, planetary positions,
sunrise, and sunset. Contains no Jyotish logic.

Files:
- `astronomy/ascendant.py` — sidereal ascendant via `swe.houses_ex`
- `astronomy/ephemeris.py` — planetary positions and rise/set times
- `astronomy/mock_ephemeris.py` — deterministic mock for tests

### Layer 2 — Natal chart

Turns astronomy into Jyotish structures.

Files:
- `grahas/` — the nine grahas with nakshatras, padas, dignity,
  combustion, retrogression, and relations
- `houses/` — whole-sign house resolution and lords
- `upagraha/` — the ten classical Upagrahas
- `dasha/` — Vimshottari Mahadasha, Antardasha, Pratyantardasha
- `transits/` — current planetary positions relative to the natal chart
- `yogas/` — detection of classical yogas
- `ashtakavarga/` — BAV and SAV computation

### Layer 3 — Evidence graph

Typed evidence items with provenance and weight tiers.

Files:
- `evidence/rules/` — the general evidence rules
- `evidence/graph.py` — aggregation, contradiction detection

### Layer 4 — Domain engines

Wealth, career, and family. Each domain runs its own rules against
a chart and produces a domain-specific report.

Files:
- `domains/wealth/`
- `domains/career/`
- `domains/family/`
- `domains/_weighting.py` — the shared weight-tier computation

### Layer 5 — LLM explanation

The system prompt, the request builder, the backends.

Files:
- `llm/prompt.py` — the system prompt and payload construction
- `llm/contract.py` — the payload safety guard
- `llm/backends/` — template, Gemini, registry
- `llm/sanitize.py` — citation redaction
- `llm/explainer.py` — the orchestration entry point

---

## The six-phase semantic pipeline

Every evidence item passes through the same six phases before it
reaches the LLM. A change that skips a phase is incomplete.

1. **Calculation** — the rule computes a fact from the chart.
2. **Direction** — PROTECTIVE, ADVERSE, or CONTEXT_INCOMPLETE.
3. **Weight** — STRUCTURAL, SUPPORTING, or MODIFIER.
4. **Semantic fields** — `subject`, `finding`, `interpretation`.
5. **Provenance** — `rule_id`, `classical_basis`, `tradition`,
   `rule_version`.
6. **Payload** — the pass-through to the LLM backend.

If you add a new rule, produce all six.

---

## Design principles

**1. Calculation is separate from interpretation.**

No interpretive logic in `astronomy/` or in the pure calculation
modules. If a function computes a longitude, it returns a longitude.
It does not decide whether the longitude is auspicious.

**2. Interpretation is separate from activation.**

A rule produces evidence. A different layer decides whether that
evidence is currently active (via dasha or transit).

**3. Every evidence item carries provenance.**

Every item has a `rule_id`, a `classical_basis`, a `tradition`, and
a `rule_version`. There are no anonymous claims.

**4. The LLM explains evidence; it does not generate astrology.**

The system prompt forbids the LLM from inventing rule IDs, dates,
events, and claims not in the evidence. The `sanitize.py` module
redacts any citation the LLM invents.

**5. Contradictions are preserved, not averaged.**

If two evidence items disagree, both are emitted, and the
contradiction is flagged. The LLM is instructed to preserve the
tension rather than resolve it.

**6. Volume does not equal importance.**

The weight tier makes this explicit. One STRUCTURAL item outweighs
many MODIFIERs.

**7. The template backend makes the project usable without an API key.**

Every feature must work with the template backend. The Gemini
backend is an enhancement, not a requirement.

---

## How to add a rule

A rule is a function that takes a chart (and sometimes a target
moment) and returns a list of `Evidence` objects.

### Step 1 — choose a rule ID

The format is:

```
<DOMAIN>-<SUBJECT>-<TYPE>-<NNN>
```

Examples:
- `WEALTH-HOUSE-LORD-NATAL-001`
- `CAREER-YOGA-PROMOTION-001`
- `FAMILY-RELATIONSHIP-001`

The NNN suffix is a three-digit number, incremented for each new
rule of the same subject and type.

### Step 2 — write the rule

Create or edit a file under `domains/<domain>/rules.py`. The rule
must return a list of `Evidence` objects.

```python
def rule_wealth_new_thing(chart) -> list[Evidence]:
    """WEALTH-NEW-THING-NATAL-001"""
    evidence: list[Evidence] = []

    for item in chart.some_collection:
        direction = Direction.PROTECTIVE
        if some_adverse_condition:
            direction = Direction.ADVERSE

        weight = weight_for_house_lord(...)

        evidence.append(Evidence(
            evidence_type=EvidenceType.UPAGRAHA_NATAL_PLACEMENT,
            direction=direction,
            domain=DOMAIN,
            upagraha=None,
            target_evidence_id=None,
            classical_strength_ratio=1.0,
            weight=weight,
            provenance=_prov(
                rule_id="WEALTH-NEW-THING-NATAL-001",
                basis="BPHS ch. 24",
                method="wealth_new_thing",
            ),
            subject=f"...",
            finding=f"...",
            interpretation=f"...",
            notes=(
                f"key=value",
                f"key=value",
            ),
        ))

    return evidence
```

### Step 3 — register the rule

Add the function to the domain's engine rule list. Open
`domains/<domain>/engine.py` and add a tuple:

```python
rule_fns = [
    ...
    ("WEALTH-NEW-THING-NATAL-001",
     lambda: wealth_rules.rule_wealth_new_thing(chart)),
]
```

### Step 4 — test

Add a test in `tests/test_<domain>_engine.py`. Test:
- The rule is evaluated (no exceptions)
- The rule produces evidence
- Every evidence item has `subject`, `finding`, `interpretation`
- Every evidence item has `weight`
- Every evidence item has `provenance.rule_id`
- Direction is one of PROTECTIVE, ADVERSE, CONTEXT_INCOMPLETE

### Step 5 — document

Add the rule to `rulebook/<NN>_<domain>.yaml` with its classical
basis and direction logic.

---

## How to add a domain

1. Create `domains/<name>/definitions.py`. Define the houses,
   significators, and their classical reasons.
2. Create `domains/<name>/rules.py`. Write the rules.
3. Create `domains/<name>/engine.py`. Write `build_<name>_report`.
4. Add a method to `chart.py`:

```python
def <name>(self, when: datetime):
    from futurelens.domains.<name>.engine import build_<name>_report
    return build_<name>_report(self, when)
```

5. Add the API endpoint in `app/main.py` if needed.
6. Add the domain to the frontend selector in `frontend/src/App.tsx`.
7. Add tests.
8. Add a Rulebook section.

The wealth, career, and family domains all follow the same structure.
Copy one of them and adapt.

---

## How to add a yoga

1. Create `yogas/rules/<yoga_name>.py`. Implement `detect(chart) ->
   YogaResult`.
2. Add the yoga to `yogas/definitions.py`.
3. Register it in `yogas/detector.py`.
4. Add the yoga to the relevant domain's `*_RELEVANT_YOGAS` tuple
   if the domain should promote it into evidence.
5. Add a test.

Use existing rules as templates. `gaja_kesari.py` is the simplest.
`dhana_yoga.py` is the most elaborate.

---

## The weight tier

Every evidence item has a `weight` field: `STRUCTURAL`, `SUPPORTING`,
or `MODIFIER`.

**STRUCTURAL** — the fundamental promise of the chart. Lordships,
yogas, own-sign placements, Lagna strength.

**SUPPORTING** — secondary indicators. Reinforce or qualify the
structural picture. Dasha activation. Benign placements in
favourable houses.

**MODIFIER** — adjustments at the margins. Combustion, Upagrahas,
transits, debilitation.

The weight is computed at emission time by the rule, using helpers
in `domains/_weighting.py`. Two helpers exist:

- `weight_for_house_lord(...)` — for house-lord placements
- `weight_for_significator(...)` — for natural significators

Simple rules use the trivial helpers:

- `weight_for_dasha()` — always SUPPORTING
- `weight_for_transit()` — always MODIFIER
- `weight_for_upagraha()` — always MODIFIER

Never hard-code `Weight.STRUCTURAL` unless the rule is a genuine yoga
or a confirmed own-sign / exalted placement.

---

## Provenance and traceability

Every evidence item carries a `Provenance` object:

```python
Provenance(
    rule_id="WEALTH-HOUSE-LORD-NATAL-001",
    rule_version="0.1",
    tradition="PHALADEEPIKA",
    classical_basis="BPHS ch. 24; Phaladeepika ch. 6",
    calculation_method="wealth_lord_natal_evaluation",
    calculation_convention="WHOLE_SIGN",
)
```

The `classical_basis` field must cite a specific classical source.
Generic phrases like "as per tradition" are not acceptable.

If the rule follows a specific commentary or a modern author, name
it in `tradition`. If it follows a variant of a classical rule,
document the variant in the rulebook.

---

## Testing

Every rule has a test. Every domain has a test file. Every layer has
at least one invariant check.

Run all tests:

```powershell
pytest -q
```

Run a single test file:

```powershell
pytest tests/test_wealth_engine.py -v
```

Run tests that match a keyword:

```powershell
pytest -k "dasha"
```

Before committing, run:

```powershell
pytest -q
```

Every test must pass. No exceptions. No skipped tests. No xfail
markers on things that should pass.

---

## Coding style

- Python 3.11 or later.
- Type hints on public functions.
- `from __future__ import annotations` at the top of every module.
- Dataclasses for value objects.
- No global state except the frozen `Conventions` object.
- No imports inside functions unless they are genuinely lazy
  (e.g., optional dependencies, avoid circular imports).
- Every module has a docstring that states what it does.
- Every rule function has a docstring with the rule ID.

Linters:

```powershell
ruff check src/
mypy src/
```

Both must pass on new code.

---

## Deployment

See `DEPLOY.md` for the GCP Cloud Run steps.

The container is a multi-stage build:
1. Node builds the Vite frontend.
2. Python installs the backend and copies the built frontend.

The final image serves both from one process on port 8000.

Secrets are passed at runtime, never baked in. The `.dockerignore`
excludes `.env` so it cannot leak into an image layer.

---

## Common pitfalls

**1. Do not parse `notes` in downstream consumers.**

Every evidence item has `subject`, `finding`, and `interpretation`.
Downstream code reads those fields. It does not parse the raw
`notes` tuple. That parsing was removed in Phase 4 and should not be
reintroduced.

**2. Do not invent rule IDs.**

The citation contract forbids the LLM from inventing rule IDs. The
same discipline applies to code. If a rule does not exist, do not
cite one that "should" exist.

**3. Do not use generic classical_basis strings.**

"Classical sources" is not acceptable. "BPHS ch. 24" is. Cite the
specific chapter or verse.

**4. Do not mix conventions silently.**

The project uses True Chitrapaksha ayanamsha, whole-sign houses,
and Vimshottari Dasha. If a rule needs a different convention, make
it explicit in the Rulebook and thread it through `Conventions`.

**5. Do not average contradictions.**

Contradictions are preserved as facts. Two conflicting evidence
items do not cancel each other. The graph flags the contradiction
and the LLM explains both sides.

**6. Do not add rules to `main.py`.**

`app/main.py` is a thin adapter. It routes HTTP requests to the
engine and serializes responses. It contains no astrological logic.

**7. Do not break the template backend.**

Any feature that works with the Gemini backend must also work with
the template backend. The template backend is the guarantee that
the project runs without an API key.

**8. Do not commit `.env`, backups, or ephemeris data accidentally.**

The `.gitignore` covers these. Do not add exceptions without a
reason. The `ephe/` folder is the one exception: the Swiss Ephemeris
data files ARE committed, because they are project assets.

---

## Questions

If a design decision is unclear, check the `rulebook/` directory.
Every rule and convention is documented there. If the rulebook does
not answer the question, open an issue on GitHub with the specific
question.

The goal is not to make the code small. The goal is to make the
code correct, traceable, and honest about what it knows and does
not know.
```