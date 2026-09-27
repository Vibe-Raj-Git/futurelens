@'
# FutureLens

A deterministic Jyotish forecasting engine with an AI interpretation layer.

FutureLens casts a complete Vedic chart from birth data, evaluates
classical rules against it, produces typed evidence, and explains the
evidence in plain language. The LLM never generates astrology. It only
explains evidence that has already been produced deterministically.

## Status

v0.1 - working, tested, wealth domain complete. 149 tests passing.

## What it does

Given a birth datetime and location, FutureLens computes:

- Ascendant (sidereal, Lahiri) via Swiss Ephemeris
- Whole-sign houses and their lords
- All nine grahas with longitude, sign, nakshatra, pada, retrograde, and combustion status
- All ten classical Upagrahas (Sun-derived chain + Kalavela portions)
- Vimshottari Dasha - Mahadasha, Antardasha, Pratyantardasha timeline
- Current transits with houses from Lagna and from Moon
- Evidence from classical rules, each item carrying a rule ID and classical basis
- Domain reports (Wealth in v0.1) with reasons for every direction
- Plain-language explanations with rule-ID citations

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

    # Plain-language explanation
    explanation = chart.explain_wealth(target, question="How is my wealth outlook?")
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
    transits          (current positions relative to natal chart)
        |
        v
    evidence          (typed, versioned, provenance-carrying evidence items)
        |
        v
    domains           (wealth rules, will be extended to career, etc.)
        |
        v
    llm               (contract-enforced explainer, template fallback)

## Design principles

1. Calculation is separate from interpretation.
2. Interpretation is separate from activation.
3. Activation is separate from forecast.
4. Every evidence item carries provenance: rule ID, classical basis, tradition, version.
5. The LLM explains; it does not generate astrology.
6. Contradictions are preserved, not averaged.
7. The template backend makes the project usable without an API key.

## What is not in v0.1

- Career, business, relocation, and other domain engines
- Yoga detection engine
- Ashtakavarga
- Divisional charts (D2, D9, D10, etc.)
- Real LLM backends (OpenAI, Anthropic, local models)

See rulebook/ for the specification and ARCHITECTURE.md for details.
'@ | Set-Content -Path README.md -Encoding utf8