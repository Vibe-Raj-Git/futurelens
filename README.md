# FutureLens

A deterministic Jyotish forecasting engine with an AI interpretation layer.

FutureLens casts a complete Vedic chart from birth data, evaluates
classical rules against it, produces typed evidence, and explains the
evidence in plain language. The LLM never generates astrology. It only
explains evidence that has already been produced deterministically.

## Status

v0.4 — working, tested. Three domain engines (wealth, career, family),
Gochara transit subsystem, SAV bindu annotations, nine yoga detectors.
All tests passing.

## What it does

Given a birth datetime and location, FutureLens computes:

- Ascendant (sidereal, Lahiri) via Swiss Ephemeris
- Whole-sign houses and their lords
- All nine grahas with longitude, sign, nakshatra, pada, retrograde,
  and combustion status
- Dignity (exaltation, debilitation, moolatrikona, own sign)
- All ten classical Upagrahas (Sun-derived chain + Kalavela portions)
- Vimshottari Dasha — Mahadasha, Antardasha, Pratyantardasha timeline
- Ashtakavarga (BAV and SAV bindus per sign)
- Current transits with houses from Lagna and from Moon
- Full classical Gochara — favourable/unfavourable verdicts, Vedha
  cancellation, SAV modulation, aspects on natal houses, motion
  state, Sade Sati phases
- Nine yogas including Dhana Yoga at full classical scope
- Evidence from classical rules, each item carrying a rule ID,
  classical basis, weight tier, and semantic fields
- Domain reports (Wealth, Career, Family) with reasons for every
  direction
- Plain-language explanations with rule-ID citations

See `ROADMAP.md` for what's shipped and what's planned.
See `ARCHITECTURE.md` for the layer structure and design principles.

## Install

    cd C:\D\Automation\advanced_kundali
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -e ".[dev,swiss]"
    pytest -q

## Quick start

    from datetime import datetime, timezone
    from futurelens import cast_chart

    chart = cast_chart(
        datetime(1990, 7, 15, 6, 30, tzinfo=timezone.utc),
        latitude=19.0760,
        longitude=72.8777,
    )

    target = datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc)

    # Dasha chain at a moment
    moment = chart.dasha_at(target)
    print(moment.mahadasha_lord, moment.antardasha_lord)

    # Current transits
    transits = chart.transits_at(target)
    print(transits.positions["SATURN"].house_from_lagna)

    # Evidence graph
    graph = chart.evidence(target)

    # Wealth domain report
    wealth = chart.wealth(target)
    print(wealth.summary())

    # Plain-language explanation (template backend, no API key)
    explanation = chart.explain_wealth(target, question="How is my wealth outlook?")
    print(explanation.text)

    # With a real LLM (requires GEMINI_API_KEY in .env)
    explanation = chart.explain_wealth(
        target,
        question="How is my wealth outlook?",
        backend="gemini",
    )
    print(explanation.text)

## Architecture

    birth data
        |
        v
    astronomy         (Swiss Ephemeris: ascendant, sunrise/sunset, grahas)
        |
        v
    houses            (whole-sign resolver)
        |
        v
    upagrahas         (Sun-derived chain + Kalavela portions)
        |
        v
    dasha             (Vimshottari Mahadasha / Antardasha / Pratyantardasha)
        |
        v
    ashtakavarga      (BAV + SAV bindus per sign)
        |
        v
    transits          (current positions relative to natal chart)
        |
        v
    gochara           (classical transit verdicts with Vedha and SAV)
        |
        v
    yogas             (nine detectors, each returning presence + conditions)
        |
        v
    evidence          (typed, versioned, provenance-carrying evidence items)
        |
        v
    domains           (wealth, career, family rules)
        |
        v
    llm               (contract-enforced explainer, template + Gemini backends)

## Design principles

1. Calculation is separate from interpretation.
2. Interpretation is separate from activation.
3. Activation is separate from forecast.
4. Every evidence item carries provenance: rule ID, classical basis,
   tradition, version.
5. The LLM explains; it does not generate astrology.
6. Contradictions are preserved, not averaged.
7. The template backend makes the project usable without an API key.

## What is not in v0.4

- Shadbala (six-fold strength)
- Divisional charts (D2, D4, D7, D9, D10, and others)
- Pratyantardasha-based timing windows
- Yoga expansion beyond the current nine
- Yoga detection rules beyond the current nine

See `ROADMAP.md` for the full list of planned work.

## Rulebook

See `rulebook/` for the specification of calculation conventions,
engines, and domain rules.

## Deployment

See `DEPLOY.md` for Docker and Cloud Run deployment.

## Contributing

See `CONTRIBUTING.md` for development workflow and conventions.