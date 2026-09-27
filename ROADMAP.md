# FutureLens Roadmap

A deterministic Jyotish forecasting engine with an AI interpretation
layer. The LLM explains evidence produced by classical rule engines.
It does not generate astrology.

Current version: **v0.4**

This document tracks what is shipped, what is in progress, and what
is planned. It is updated at the close of every development session.

---

## Shipped

### v0.1 — Foundation

- Sidereal ascendant (Lahiri) via Swiss Ephemeris
- Whole-sign houses and their lords (Parashara)
- All nine grahas with longitude, sign, nakshatra, pada, retrograde,
  combustion
- All ten classical Upagrahas (Sun-derived chain + Kalavela portions)
- Vimshottari Dasha: Mahadasha, Antardasha, Pratyantardasha timeline
- Current transits relative to natal chart
- Evidence graph with subject-aware contradiction detection
- Wealth domain engine
- LLM explainer with template backend
- Rule-ID citation contract enforced

### v0.2 — Family domain and evidence tiering

- Family domain engine (six houses: 2, 4, 5, 7, 9, 12)
- Weight-tiered evidence: STRUCTURAL / SUPPORTING / MODIFIER /
  STRONG_MODIFIER
- Contradiction preservation, not averaging
- Semantic evidence fields: subject, finding, interpretation
  populated at rule-emission time

### v0.3 — Gochara subsystem and LLM production layer

- Full classical Gochara: Jupiter, Saturn, Rahu, Ketu as the four
  slow transiting grahas
- Two reference frames: house from Chandra Lagna (primary),
  house from Lagna (secondary)
- Favourable/unfavourable tables per Phaladeepika ch. 26
- Vedha cancellation for all four slow grahas
- SAV bindu support for the transited sign
- Aspects cast by transiting graha on natal houses
- Direct / retrograde / near-station detection
- Sade Sati as a specific Saturn case with three phases
- Five-level verdict: STRONGLY_FAVOURABLE ... STRONGLY_UNFAVOURABLE
- Integration into wealth, career, and family domain engines
- Multi-stage Dockerfile, container runs on Cloud Run
- FastAPI serves built Vite frontend in production
- Gemini backend via google-genai

### v0.4 — Ashtakavarga in the reading, Dhana Yoga at full scope

- SAV bindu annotation on natal house-lord findings, sign-explicit
  phrasing ("The 2nd house falls in Sagittarius, which holds 30 SAV
  bindus (VERY_STRONG).")
- Ashtakavarga report cached on the Chart instance; shared across
  all consumers
- Dhana Yoga detector extended to full classical scope:
  - shared lordship of two or more wealth houses
  - wealth lord occupying a wealth house
  - wealth lord in own sign while in a wealth house
  - disqualifier flags (weakened_by_*) preserved, not suppressed
- Prompt priority for domain-specific structural findings
  (Dhana Yoga > Raja Yoga for wealth; validated end-to-end via
  Gemini)
- Career domain engine

---

## In progress

None currently. v0.4 is complete.

---

## Next — Stage 3: Shadbala

The six-fold strength framework. Largest remaining gap in
interpretive depth.

- **Sthana Bala** — positional strength (uchcha, saptavargaja,
  ojhayugma, kendra, drekkana)
- **Dig Bala** — directional strength
- **Kala Bala** — temporal strength (natonnata, paksha, tribhaga,
  varsha-masa-dina-hora, ayana, yuddha)
- **Chesta Bala** — motional strength (retrogression as a positive,
  not a negative)
- **Naisargika Bala** — natural strength (Sun strongest, Saturn
  weakest)
- **Drik Bala** — aspectual strength

Output: total in rupas. Classical threshold: 300 rupas for a graha
to deliver its promise. Once computed, every existing rule that
reasons about strength ("in own sign = strong") gains a
quantitative follow-up ("Shadbala 420 rupas = delivers").

Estimated scope: 400–600 lines plus tests.

---

## After Shadbala

### Stage 4a — D9 Navamsa

The one divisional chart that affects every rule. A graha strong in
D1 but weak in D9 promises less than it appears. A graha weak in D1
but strong in D9 gets upgraded. Adding D9 to the engine means every
existing strength judgment acquires a confirmation layer.

### Stage 4b — D2 Hora, D10 Dasamsa

Domain-specific divisional charts:

- **D2 Hora** — wealth
- **D10 Dasamsa** — career
- **D7 Saptamsa** — children
- **D4 Chaturthamsa** — property

Each is a mathematical transform of the D1 longitudes. The
interpretive rules matter more than the transform.

### Stage 5 — Pratyantardasha timing windows

Combine Mahadasha lord, Antardasha lord, and supportive transit to
identify forecasting windows. The level of timing granularity a
practising astrologer actually uses.

### Stage 6 — Yoga expansion

Currently nine yogas. The classical set is roughly forty. Additions:

- Kuja Dosha (Mangal Dosha)
- Shakata Yoga
- Daridra Yoga
- Amala Yoga (full definition)
- Chamara Yoga
- Sarala Yoga
- Vimala Yoga
- Vasumati Yoga
- All three Nabhasa Yogas
- Remaining Dhana Yoga variants from BPHS ch. 24

---

## Refinements (not blocking)

- **Gemini SDK migration** — use `Chat.send_message` instead of
  `Models.generate_content` to silence the AFC deprecation warning
- **Reading regeneration script** — one command to regenerate all
  three domain readings for the reference chart, so prompt changes
  are validated in one step
- **SAV value surfacing in the LLM reading** — currently Gemini sees
  SAV bindus in the evidence but does not always cite them
- **Rulebook expansion** — Gochara, Ashtakavarga, and yoga engines
  are not yet documented in `rulebook/`
- **`_sav_strength_label` deduplication** — the same helper is
  duplicated in wealth, career, and family rule files; should move
  to `domains/_weighting.py`

---

## Not yet implemented

The following are classical apparatus that a complete Jyotish
product would eventually include. They are not on the near-term
roadmap.

- Shodasha-varga (all sixteen divisional charts)
- Shadbala's full sub-component set (partial Shadbala is Stage 3)
- Bhava-bala (house strength proper, distinct from SAV)
- Ishta and Kashta Phala
- Yogas beyond the classical forty
- Muhurta (electional astrology)
- Prashna (horary astrology)
- Varshaphala (annual chart / Tajika)
- Nadi-based forecasting
- Jaimini system (Chara Dasha, Karakas, Rashi Drishti)
- KP (Krishnamurti Paddhati) system

---

## Design principles

These are fixed. Any change requires an explicit decision.

1. Calculation is separate from interpretation.
2. Interpretation is separate from activation.
3. Activation is separate from forecast.
4. Every evidence item carries provenance: rule ID, classical basis,
   tradition, version.
5. The LLM explains; it does not generate astrology.
6. Contradictions are preserved, not averaged.
7. The template backend makes the project usable without an API key.

---

## Version history

| Version | Date | Highlights |
|---|---|---|
| v0.1 | — | Foundation: D1 chart, Vimshottari, wealth domain |
| v0.2 | — | Family domain, weight tiering, semantic fields |
| v0.3 | — | Gochara subsystem, Docker, Gemini backend |
| v0.4 | 2026-09-27 | SAV in reading, Dhana Yoga full scope, career domain |