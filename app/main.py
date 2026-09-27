"""
FutureLens API.

This module is an adapter between the HTTP layer and the FutureLens
calculation engine. It contains no astrological logic. All
interpretation is produced by futurelens itself.

Endpoints
---------
GET  /health
GET  /api/locations/search?q=...
POST /api/forecast
POST /api/chat
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from futurelens.chart import cast_chart
from futurelens.llm.explainer import explain


# --------------------------------------------------------------------------
# App
# --------------------------------------------------------------------------

app = FastAPI(
    title="FutureLens API",
    version="0.3.0",
    description=(
        "Deterministic Jyotish engine with an AI interpretation "
        "layer. The API exposes pre-computed evidence and "
        "natural-language explanations."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------
# Static location data
# --------------------------------------------------------------------------

LOCATIONS: list[dict] = [
    {"label": "Indore, Madhya Pradesh, India", "latitude": 22.7196, "longitude": 75.8577, "city": "Indore", "state": "Madhya Pradesh", "country": "India"},
    {"label": "Mumbai, Maharashtra, India", "latitude": 19.0760, "longitude": 72.8777, "city": "Mumbai", "state": "Maharashtra", "country": "India"},
    {"label": "Delhi, India", "latitude": 28.6139, "longitude": 77.2090, "city": "Delhi", "state": "Delhi", "country": "India"},
    {"label": "Kolkata, West Bengal, India", "latitude": 22.5726, "longitude": 88.3639, "city": "Kolkata", "state": "West Bengal", "country": "India"},
    {"label": "Bengaluru, Karnataka, India", "latitude": 12.9716, "longitude": 77.5946, "city": "Bengaluru", "state": "Karnataka", "country": "India"},
    {"label": "Chennai, Tamil Nadu, India", "latitude": 13.0827, "longitude": 80.2707, "city": "Chennai", "state": "Tamil Nadu", "country": "India"},
    {"label": "Hyderabad, Telangana, India", "latitude": 17.3850, "longitude": 78.4867, "city": "Hyderabad", "state": "Telangana", "country": "India"},
    {"label": "Pune, Maharashtra, India", "latitude": 18.5204, "longitude": 73.8567, "city": "Pune", "state": "Maharashtra", "country": "India"},
    {"label": "Ahmedabad, Gujarat, India", "latitude": 23.0225, "longitude": 72.5714, "city": "Ahmedabad", "state": "Gujarat", "country": "India"},
    {"label": "Jaipur, Rajasthan, India", "latitude": 26.9124, "longitude": 75.7873, "city": "Jaipur", "state": "Rajasthan", "country": "India"},
    {"label": "Lucknow, Uttar Pradesh, India", "latitude": 26.8467, "longitude": 80.9462, "city": "Lucknow", "state": "Uttar Pradesh", "country": "India"},
    {"label": "Varanasi, Uttar Pradesh, India", "latitude": 25.3176, "longitude": 82.9739, "city": "Varanasi", "state": "Uttar Pradesh", "country": "India"},
    {"label": "London, United Kingdom", "latitude": 51.5074, "longitude": -0.1278, "city": "London", "country": "United Kingdom"},
    {"label": "New York, NY, USA", "latitude": 40.7128, "longitude": -74.0060, "city": "New York", "state": "NY", "country": "USA"},
    {"label": "San Francisco, CA, USA", "latitude": 37.7749, "longitude": -122.4194, "city": "San Francisco", "state": "CA", "country": "USA"},
    {"label": "Dubai, UAE", "latitude": 25.2048, "longitude": 55.2708, "city": "Dubai", "country": "UAE"},
    {"label": "Singapore", "latitude": 1.3521, "longitude": 103.8198, "city": "Singapore", "country": "Singapore"},
    {"label": "Sydney, NSW, Australia", "latitude": -33.8688, "longitude": 151.2093, "city": "Sydney", "state": "NSW", "country": "Australia"},
]


# --------------------------------------------------------------------------
# Request and response models
# --------------------------------------------------------------------------

DomainName = Literal["WEALTH", "CAREER", "FAMILY"]
BackendName = Literal["template", "gemini"]


class LocationSuggestion(BaseModel):
    label: str
    latitude: float
    longitude: float
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None


class ForecastRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    date_of_birth: str = Field(..., description="ISO date, e.g. 1990-07-15")
    time_of_birth: str = Field(..., description="HH:MM, e.g. 12:00")
    place: str = Field(..., min_length=1)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    domain: DomainName = "WEALTH"
    timezone_offset_minutes: Optional[int] = None
    target_datetime: Optional[str] = None


class EvidenceItem(BaseModel):
    """
    A single evidence item.

    summary  - one-line human-readable description
    detail   - full key=value detail string (for the "why" panel)
    rule_id  - the rule that produced this item
    classical_basis - the classical source cited by the rule
    direction - PROTECTIVE or ADVERSE
    """
    summary: str
    detail: str
    rule_id: Optional[str] = None
    classical_basis: Optional[str] = None
    direction: Optional[str] = None


class Summary(BaseModel):
    evidence_count: int
    supportive_count: int
    challenging_count: int
    contradictions: int


class Explanation(BaseModel):
    text: str
    backend: str
    rule_ids_cited: list[str]
    evidence_count: int
    contradiction_count: int


class ForecastResponse(BaseModel):
    domain: str
    when: str
    title: str
    summary: Summary
    supportive: list[EvidenceItem]
    challenging: list[EvidenceItem]
    timing: list[dict] = []
    explanation: Explanation


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    date_of_birth: str
    time_of_birth: str
    place: str
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    domain: Optional[DomainName] = None
    timezone_offset_minutes: Optional[int] = None
    target_datetime: Optional[str] = None
    backend: BackendName = "template"


class ChatResponse(BaseModel):
    answer: str
    backend: str
    rule_ids_cited: list[str] = []


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _parse_birth_moment(
    date_of_birth: str,
    time_of_birth: str,
    timezone_offset_minutes: Optional[int],
) -> datetime:
    """Convert a local birth date and time into a UTC datetime."""
    try:
        local_dt = datetime.fromisoformat(f"{date_of_birth}T{time_of_birth}")
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid birth date or time: {date_of_birth!r} "
                f"{time_of_birth!r}."
            ),
        ) from exc

    offset = timezone_offset_minutes if timezone_offset_minutes is not None else 330
    tz = timezone(timedelta(minutes=offset))

    if local_dt.tzinfo is None:
        local_dt = local_dt.replace(tzinfo=tz)

    return local_dt.astimezone(timezone.utc)


def _parse_target_moment(target_datetime: Optional[str]) -> datetime:
    """Parse the target moment, defaulting to now (UTC)."""
    if not target_datetime:
        return datetime.now(timezone.utc)
    try:
        dt = datetime.fromisoformat(target_datetime)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid target_datetime: {target_datetime!r}.",
        ) from dt
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _evidence_to_item(e) -> EvidenceItem:
    """
    Convert an Evidence object into an EvidenceItem for the API.

    The rule author has already populated subject / finding /
    interpretation. This function does not parse notes and does not
    reconstruct semantic text from rule IDs.
    """
    return EvidenceItem(
        summary=e.subject or e.finding or e.provenance.rule_id,
        detail=" | ".join(e.notes) if e.notes else "",
        rule_id=e.provenance.rule_id,
        classical_basis=e.provenance.classical_basis,
        direction=e.direction.value,
    )


def _build_report(chart, domain: str, when: datetime):
    """Route to the correct domain engine."""
    if domain == "WEALTH":
        return chart.wealth(when)
    if domain == "CAREER":
        return chart.career(when)
    if domain == "FAMILY":
        from futurelens.domains.family.engine import build_FAMILY_report
        return build_FAMILY_report(chart, when)
    raise HTTPException(status_code=400, detail=f"Unsupported domain: {domain}")


# --------------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok", "service": "futurelens", "version": "0.3.0"}


@app.get("/api/locations/search", response_model=list[LocationSuggestion])
def search_locations(q: str = Query(..., min_length=2)):
    query = q.strip().lower()
    matches: list[LocationSuggestion] = []
    for loc in LOCATIONS:
        haystack = " ".join(
            str(loc.get(k, "")) for k in ("label", "city", "state", "country")
        ).lower()
        if query in haystack:
            matches.append(LocationSuggestion(**loc))
    return matches


@app.post("/api/forecast", response_model=ForecastResponse)
def forecast(payload: ForecastRequest) -> ForecastResponse:
    birth_moment = _parse_birth_moment(
        payload.date_of_birth,
        payload.time_of_birth,
        payload.timezone_offset_minutes,
    )
    target_moment = _parse_target_moment(payload.target_datetime)

    try:
        chart = cast_chart(
            when=birth_moment,
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Chart calculation failed: {exc}",
        ) from exc

    try:
        report = _build_report(chart, payload.domain, target_moment)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Domain report failed for {payload.domain}: {exc}",
        ) from exc

    supportive = [
        _evidence_to_item(e)
        for e in report.evidence
        if e.direction.value == "PROTECTIVE"
    ]
    challenging = [
        _evidence_to_item(e)
        for e in report.evidence
        if e.direction.value == "ADVERSE"
    ]

    summary = Summary(
        evidence_count=len(report.evidence),
        supportive_count=len(supportive),
        challenging_count=len(challenging),
        contradictions=len(report.contradictions),
    )

    try:
        explanation_result = explain(report, backend="gemini")
    except Exception:
        try:
            explanation_result = explain(report, backend="template")
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Explanation failed: {exc}",
            ) from exc

    return ForecastResponse(
        domain=payload.domain,
        when=target_moment.isoformat(),
        title=f"{payload.domain.title()} Forecast",
        summary=summary,
        supportive=supportive,
        challenging=challenging,
        timing=[],
        explanation=Explanation(
            text=explanation_result.text,
            backend=explanation_result.backend,
            rule_ids_cited=list(explanation_result.rule_ids_cited),
            evidence_count=explanation_result.evidence_count,
            contradiction_count=explanation_result.contradiction_count,
        ),
    )


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    birth_moment = _parse_birth_moment(
        payload.date_of_birth,
        payload.time_of_birth,
        payload.timezone_offset_minutes,
    )
    target_moment = _parse_target_moment(payload.target_datetime)
    domain = payload.domain or "WEALTH"

    try:
        chart = cast_chart(
            when=birth_moment,
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Chart calculation failed: {exc}",
        ) from exc

    try:
        report = _build_report(chart, domain, target_moment)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Domain report failed for {domain}: {exc}",
        ) from exc

    try:
        explanation_result = explain(
            report,
            question=payload.question,
            backend=payload.backend,
        )
    except Exception as exc:
        try:
            explanation_result = explain(
                report,
                question=payload.question,
                backend="template",
            )
        except Exception:
            raise HTTPException(
                status_code=500,
                detail=f"Explanation failed: {exc}",
            ) from exc

    return ChatResponse(
        answer=explanation_result.text,
        backend=explanation_result.backend,
        rule_ids_cited=list(explanation_result.rule_ids_cited),
    )