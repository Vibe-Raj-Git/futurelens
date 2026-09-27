# FutureLens frontend

This is the first implementation of the frozen FutureLens UI:

- Light, vibrant visual language
- Birth details: name, date, time, place
- Place autocomplete with automatic latitude/longitude returned by the backend
- Three primary areas: Wealth, Career, Family
- Forecast result area with evidence and timing
- "Ask FutureLens" astrology chat
- No product/architecture chatbot

## Run

From `frontend`:

```powershell
npm install
npm run dev
```

The Vite dev server proxies `/api/*` to `http://127.0.0.1:8000`.

## Backend API contract

The frontend expects:

### GET `/api/locations/search?q=Indore`

Return:

```json
[
  {
    "label": "Indore, Madhya Pradesh, India",
    "latitude": 22.7196,
    "longitude": 75.8577,
    "city": "Indore",
    "state": "Madhya Pradesh",
    "country": "India"
  }
]
```

### POST `/api/forecast`

Request:

```json
{
  "name": "User",
  "date_of_birth": "1990-07-15",
  "time_of_birth": "12:00",
  "place": "Indore, Madhya Pradesh, India",
  "latitude": 22.7196,
  "longitude": 75.8577,
  "domain": "WEALTH"
}
```

Return the forecast object expected by `src/api.ts`.

### POST `/api/chat`

Request contains the same birth details plus:

```json
{
  "question": "When is my strongest career period?",
  "domain": "CAREER"
}
```

Return:

```json
{ "answer": "..." }
```

The chat should be backed by the deterministic chart/evidence/timing pipeline, not by an independent astrology calculation.
