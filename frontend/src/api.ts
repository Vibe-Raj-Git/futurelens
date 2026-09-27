export type Domain = "WEALTH" | "CAREER" | "FAMILY";

export type LocationSuggestion = {
  label: string;
  latitude: number;
  longitude: number;
  city?: string;
  state?: string;
  country?: string;
};

export type BirthInput = {
  name: string;
  dateOfBirth: string;
  timeOfBirth: string;
  place: LocationSuggestion;
};

export type EvidenceItem = {
  summary: string;
  detail: string;
  rule_id?: string;
  classical_basis?: string;
  direction?: string;
};

export type ForecastResponse = {
  domain: Domain;
  when: string;
  title?: string;
  summary?: {
    evidence_count: number;
    supportive_count: number;
    challenging_count: number;
    contradictions: number;
  };
  supportive?: EvidenceItem[];
  challenging?: EvidenceItem[];
  timing?: Array<{
    start?: string;
    end?: string;
    title: string;
    description: string;
    rule_ids?: string[];
    direction?: string;
  }>;
  explanation?: {
    text: string;
    backend: string;
    rule_ids_cited: string[];
    evidence_count: number;
    contradiction_count: number;
  };
};

const jsonHeaders = { "Content-Type": "application/json" };

export async function searchLocations(query: string): Promise<LocationSuggestion[]> {
  const q = query.trim();
  if (q.length < 2) return [];

  const response = await fetch(`/api/locations/search?q=${encodeURIComponent(q)}`);
  if (!response.ok) throw new Error("Location search failed.");
  return response.json();
}

export async function generateForecast(
  input: BirthInput,
  domain: Domain,
): Promise<ForecastResponse> {
  const response = await fetch("/api/forecast", {
    method: "POST",
    headers: jsonHeaders,
    body: JSON.stringify({
      name: input.name,
      date_of_birth: input.dateOfBirth,
      time_of_birth: input.timeOfBirth,
      place: input.place.label,
      latitude: input.place.latitude,
      longitude: input.place.longitude,
      domain,
    }),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Forecast generation failed.");
  }
  return response.json();
}

export async function askFutureLens(
  question: string,
  input: BirthInput,
  domain?: Domain,
): Promise<{ answer: string }> {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: jsonHeaders,
    body: JSON.stringify({
      question,
      name: input.name,
      date_of_birth: input.dateOfBirth,
      time_of_birth: input.timeOfBirth,
      place: input.place.label,
      latitude: input.place.latitude,
      longitude: input.place.longitude,
      domain: domain ?? null,
    }),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Unable to answer right now.");
  }
  return response.json();
}