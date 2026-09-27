New-Item -ItemType Directory -Force -Path docs | Out-Null
@'
# FutureLens Quickstart

## 1. Install

    cd C:\D\Automation\advanced_kundali
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -e ".[dev,swiss]"

## 2. Verify

    pytest -q

Should report 149 passing.

## 3. Cast a chart

    from datetime import datetime, timezone
    from futurelens import cast_chart

    chart = cast_chart(
        datetime(1990, 7, 15, 6, 30, tzinfo=timezone.utc),
        latitude=19.0760,
        longitude=72.8777,
    )

## 4. Ask about wealth

    target = datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc)
    explanation = chart.explain_wealth(target, question="How is my wealth outlook?")
    print(explanation.text)

## 5. Plug in a real LLM

Implement the LLMBackend protocol:

    from futurelens.llm.backends.base import LLMBackend
    from futurelens.llm.contract import LLMRequest, LLMResponse

    class MyBackend:
        name = "my-backend"

        def generate(self, request: LLMRequest) -> LLMResponse:
            # Call your LLM here using request.system_prompt and request.user_prompt.
            # Return an LLMResponse with text and cited rule IDs.
            ...

    explanation = chart.explain_wealth(target, backend=MyBackend())

## 6. Add a domain

See ARCHITECTURE.md.

## 7. Explore the Rulebook

The rulebook/ directory contains the specification. Every rule
implemented in code should have a corresponding rulebook entry.
'@ | Set-Content -Path docs\quickstart.md -Encoding utf8