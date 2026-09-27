import { useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowRight,
  BriefcaseBusiness,
  CalendarDays,
  Check,
  Clock3,
  Heart,
  LoaderCircle,
  LockKeyhole,
  MapPin,
  MessageCircle,
  Send,
  Sparkles,
  WalletCards,
  X,
} from "lucide-react";
import {
  askFutureLens,
  generateForecast,
  searchLocations,
  type BirthInput,
  type Domain,
  type EvidenceItem,
  type ForecastResponse,
  type LocationSuggestion,
} from "./api";

// ---------------------------------------------------------------------------
// PREPOPULATE
//
// Set to true to pre-fill the form with a sample birth chart for testing.
// Set to false to ship the app with empty fields.
//
// To revert to no pre-population, change this single line to:
//     const PREPOPULATE = false;
// ---------------------------------------------------------------------------
const PREPOPULATE = true;

const PREPOPULATED_BIRTH = {
  name: "Rajarshi Pathak",
  dateOfBirth: "1984-08-30",
  timeOfBirth: "12:02",
  place: {
    label: "Indore, Madhya Pradesh, India",
    latitude: 22.7196,
    longitude: 75.8577,
    city: "Indore",
    state: "Madhya Pradesh",
    country: "India",
  } as LocationSuggestion,
};

const domains: Array<{
  id: Domain;
  label: string;
  icon: typeof WalletCards;
  description: string;
  accent: string;
}> = [
  {
    id: "WEALTH",
    label: "Wealth",
    icon: WalletCards,
    description: "Money, gains, investments & financial potential",
    accent: "violet",
  },
  {
    id: "CAREER",
    label: "Career",
    icon: BriefcaseBusiness,
    description: "Work, growth & professional direction",
    accent: "blue",
  },
  {
    id: "FAMILY",
    label: "Family",
    icon: Heart,
    description: "Family, relationships & important family themes",
    accent: "rose",
  },
];

const prompts = [
  "When is my strongest career period?",
  "What does my chart indicate about wealth?",
  "Which upcoming period is important for me?",
];

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

export default function App() {
  const [name, setName] = useState(
    PREPOPULATE ? PREPOPULATED_BIRTH.name : ""
  );
  const [dateOfBirth, setDateOfBirth] = useState(
    PREPOPULATE ? PREPOPULATED_BIRTH.dateOfBirth : ""
  );
  const [timeOfBirth, setTimeOfBirth] = useState(
    PREPOPULATE ? PREPOPULATED_BIRTH.timeOfBirth : ""
  );
  const [placeQuery, setPlaceQuery] = useState(
    PREPOPULATE ? PREPOPULATED_BIRTH.place.label : ""
  );
  const [place, setPlace] = useState<LocationSuggestion | null>(
    PREPOPULATE ? PREPOPULATED_BIRTH.place : null
  );
  const [suggestions, setSuggestions] = useState<LocationSuggestion[]>([]);
  const [selectedDomain, setSelectedDomain] = useState<Domain>("WEALTH");
  const [loadingLocations, setLoadingLocations] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [error, setError] = useState("");
  const [chatOpen, setChatOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [chatAnswer, setChatAnswer] = useState("");
  const [chatLoading, setChatLoading] = useState(false);

  const locationTimer = useRef<number | undefined>(undefined);

  const birthInput = useMemo<BirthInput | null>(() => {
    if (!name || !dateOfBirth || !timeOfBirth || !place) return null;
    return { name, dateOfBirth, timeOfBirth, place };
  }, [name, dateOfBirth, timeOfBirth, place]);

  useEffect(() => {
    if (locationTimer.current) window.clearTimeout(locationTimer.current);

    // Do not clear the selected place when the query still matches it.
    // This preserves a pre-populated place on first render.
    if (place && placeQuery === place.label) {
      setSuggestions([]);
      return;
    }

    setPlace(null);

    if (placeQuery.trim().length < 2) {
      setSuggestions([]);
      return;
    }

    locationTimer.current = window.setTimeout(async () => {
      try {
        setLoadingLocations(true);
        const results = await searchLocations(placeQuery);
        setSuggestions(results);
      } catch {
        setSuggestions([]);
      } finally {
        setLoadingLocations(false);
      }
    }, 300);

    return () => {
      if (locationTimer.current) window.clearTimeout(locationTimer.current);
    };
  }, [placeQuery, place]);

  function selectLocation(item: LocationSuggestion) {
    setPlace(item);
    setPlaceQuery(item.label);
    setSuggestions([]);
  }

  async function handleForecast() {
    if (!birthInput) {
      setError("Please complete your name, birth date, birth time and birth place.");
      return;
    }
    setError("");
    setGenerating(true);
    setForecast(null);

    try {
      const result = await generateForecast(birthInput, selectedDomain);
      setForecast(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to generate the forecast.");
    } finally {
      setGenerating(false);
    }
  }

  async function handleAsk(text = question) {
    const q = text.trim();
    if (!q || !birthInput) {
      if (!birthInput) setError("Complete your birth details before asking about your chart.");
      return;
    }

    setQuestion(q);
    setChatAnswer("");
    setError("");
    setChatLoading(true);

    try {
      const result = await askFutureLens(q, birthInput, selectedDomain);
      setChatAnswer(result.answer);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to answer right now.");
    } finally {
      setChatLoading(false);
    }
  }

  const domain = domains.find((item) => item.id === selectedDomain)!;

  return (
    <div className="min-h-screen overflow-x-hidden bg-[#fbfcff] text-slate-950">
      <div className="pointer-events-none fixed inset-0 -z-10">
        <div className="absolute left-[-12rem] top-[-10rem] h-[30rem] w-[30rem] rounded-full bg-violet-200/40 blur-3xl" />
        <div className="absolute right-[-10rem] top-[12rem] h-[28rem] w-[28rem] rounded-full bg-fuchsia-200/35 blur-3xl" />
        <div className="absolute bottom-[-14rem] left-[35%] h-[30rem] w-[30rem] rounded-full bg-blue-100/50 blur-3xl" />
      </div>

      <header className="mx-auto flex max-w-6xl items-center justify-between px-5 py-6 sm:px-8">
        <div className="flex items-center gap-3">
          <div className="brand-mark">
            <Sparkles size={19} strokeWidth={2.4} />
          </div>
          <span className="text-xl font-extrabold tracking-tight">FutureLens</span>
        </div>
        <div className="privacy-pill">
          <LockKeyhole size={14} />
          Private
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-5 pb-20 sm:px-8">
        <section className="mx-auto max-w-4xl pt-8 text-center sm:pt-12">
          <div className="eyebrow">
            <Sparkles size={14} />
            Deterministic astrology + intelligent explanation
          </div>
          <h1 className="mt-5 text-5xl font-black leading-[0.98] tracking-[-0.045em] sm:text-7xl">
            See what your chart
            <span className="gradient-text block">says about your future.</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-base leading-7 text-slate-600 sm:text-lg">
            Enter your birth details and explore the areas of life that matter to you.
          </p>
        </section>

        <section className="form-card mt-12">
          <div className="mb-7 flex items-start justify-between gap-4">
            <div>
              <h2 className="text-xl font-extrabold tracking-tight">Tell us about yourself</h2>
              <p className="mt-1 text-sm text-slate-500">
                Your details are used to construct your birth chart.
              </p>
            </div>
            <div className="privacy-pill hidden sm:flex">
              <LockKeyhole size={14} />
              Private
            </div>
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            <Field label="Your name">
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter your name"
                className="input"
              />
            </Field>

            <Field label="Date of birth">
              <div className="input-wrap">
                <CalendarDays size={18} />
                <input
                  type="date"
                  max={todayIso()}
                  value={dateOfBirth}
                  onChange={(e) => setDateOfBirth(e.target.value)}
                  className="input input-icon"
                />
              </div>
            </Field>

            <Field label="Time of birth">
              <div className="input-wrap">
                <Clock3 size={18} />
                <input
                  type="time"
                  value={timeOfBirth}
                  onChange={(e) => setTimeOfBirth(e.target.value)}
                  className="input input-icon"
                />
              </div>
            </Field>

            <Field label="Place of birth">
              <div className="relative">
                <div className={`input-wrap ${place ? "input-selected" : ""}`}>
                  <MapPin size={18} />
                  <input
                    value={placeQuery}
                    onChange={(e) => setPlaceQuery(e.target.value)}
                    placeholder="Start typing a city or place"
                    className="input input-icon"
                    autoComplete="off"
                  />
                  {loadingLocations && <LoaderCircle className="animate-spin" size={17} />}
                  {place && !loadingLocations && <Check className="text-emerald-500" size={18} />}
                </div>

                {suggestions.length > 0 && (
                  <div className="location-menu">
                    {suggestions.map((item) => (
                      <button
                        type="button"
                        key={`${item.label}-${item.latitude}-${item.longitude}`}
                        onClick={() => selectLocation(item)}
                        className="location-option"
                      >
                        <span className="location-icon"><MapPin size={16} /></span>
                        <span className="min-w-0 text-left">
                          <span className="block truncate font-semibold text-slate-800">{item.label}</span>
                          <span className="block text-xs text-slate-400">
                            {item.latitude.toFixed(4)}, {item.longitude.toFixed(4)}
                          </span>
                        </span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </Field>
          </div>

          <div className="mt-8">
            <div className="mb-3 flex items-end justify-between">
              <div>
                <p className="text-sm font-bold text-slate-700">What would you like to explore?</p>
                <p className="mt-1 text-xs text-slate-400">Choose one area to start your forecast.</p>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              {domains.map((item) => {
                const Icon = item.icon;
                const active = selectedDomain === item.id;
                return (
                  <button
                    type="button"
                    key={item.id}
                    onClick={() => setSelectedDomain(item.id)}
                    className={`domain-card ${active ? "domain-card-active" : ""}`}
                  >
                    <div className={`domain-icon ${item.accent}`}>
                      <Icon size={21} />
                    </div>
                    <div className="mt-5 text-left">
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-extrabold">{item.label}</h3>
                        {active && <span className="selected-badge">Selected</span>}
                      </div>
                      <p className="mt-2 min-h-10 text-sm leading-5 text-slate-500">{item.description}</p>
                      <div className={`mt-5 flex items-center gap-1 text-sm font-bold ${active ? "text-violet-600" : "text-slate-400"}`}>
                        Explore <ArrowRight size={15} />
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {error && (
            <div className="mt-5 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">
              {error}
            </div>
          )}

          <button
            type="button"
            onClick={handleForecast}
            disabled={generating}
            className="primary-button mt-7"
          >
            {generating ? (
              <>
                <LoaderCircle className="animate-spin" size={19} />
                Reading your chart...
              </>
            ) : (
              <>
                Generate my {domain.label.toLowerCase()} forecast
                <ArrowRight size={20} />
              </>
            )}
          </button>

          <p className="mt-3 text-center text-xs text-slate-400">
            Your birth location is resolved to geographic coordinates automatically.
          </p>
        </section>

        {forecast && (
          <section className="result-card mt-8">
            <div className="flex flex-wrap items-start justify-between gap-5">
              <div>
                <div className="eyebrow">Your {domain.label} reading</div>
                <h2 className="mt-3 text-3xl font-black tracking-tight">
                  {forecast.title ?? `${domain.label} forecast`}
                </h2>
              </div>
              <div className="rounded-full bg-slate-100 px-3 py-1.5 text-xs font-bold text-slate-500">
                {forecast.when}
              </div>
            </div>

            {forecast.summary && (
              <p className="mt-5 max-w-3xl text-base leading-7 text-slate-600">
                {forecast.summary.evidence_count} evidence items •{" "}
                {forecast.summary.supportive_count} supportive •{" "}
                {forecast.summary.challenging_count} challenging •{" "}
                {forecast.summary.contradictions} contradictions
              </p>
            )}

            {forecast.explanation && (
              <div className="mt-7 rounded-2xl border border-violet-100 bg-violet-50/40 p-6">
                <div className="flex items-center gap-2">
                  <Sparkles size={16} className="text-violet-500" />
                  <h3 className="text-xs font-extrabold uppercase tracking-[0.14em] text-violet-700">
                    Reading
                  </h3>
                </div>
                <p className="mt-3 whitespace-pre-wrap text-[15px] leading-7 text-slate-700">
                  {forecast.explanation.text}
                </p>
                <p className="mt-3 text-[11px] font-bold text-slate-400">
                  {forecast.explanation.rule_ids_cited.length} rules cited · backend:{" "}
                  {forecast.explanation.backend}
                </p>
              </div>
            )}

            <div className="mt-7 grid gap-5 md:grid-cols-2">
              <EvidenceBlock title="Supportive indications" items={forecast.supportive ?? []} positive />
              <EvidenceBlock title="Challenging indications" items={forecast.challenging ?? []} />
            </div>

            {forecast.timing && forecast.timing.length > 0 && (
              <div className="mt-7">
                <h3 className="text-lg font-extrabold">Important periods</h3>
                <div className="mt-3 grid gap-3 md:grid-cols-2">
                  {forecast.timing.map((period, index) => (
                    <div key={`${period.title}-${index}`} className="timing-card">
                      <div className="flex items-center justify-between gap-3">
                        <h4 className="font-extrabold">{period.title}</h4>
                        <Clock3 size={17} className="text-violet-500" />
                      </div>
                      <p className="mt-2 text-sm leading-6 text-slate-600">{period.description}</p>
                      {(period.start || period.end) && (
                        <p className="mt-3 text-xs font-bold text-violet-600">
                          {period.start ?? "—"} {period.end ? `→ ${period.end}` : ""}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        )}

        <section className="chat-card mt-10">
          <div className="chat-glow" />
          <div className="relative z-10">
            <div className="flex items-start gap-4">
              <div className="chat-icon"><Sparkles size={21} /></div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-2xl font-black tracking-tight">Ask FutureLens</h2>
                  <span className="live-pill">AI</span>
                </div>
                <p className="mt-1 text-sm text-slate-500">
                  Ask anything about your chart, your future, or an important period.
                </p>
              </div>
            </div>

            <div className="mt-6 flex flex-wrap gap-2">
              {prompts.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  onClick={() => {
                    setChatOpen(true);
                    setQuestion(prompt);
                  }}
                  className="prompt-chip"
                >
                  {prompt}
                </button>
              ))}
            </div>

            <div className="mt-5 flex items-center gap-3 rounded-2xl border border-slate-200 bg-white p-2 shadow-sm">
              <MessageCircle className="ml-2 shrink-0 text-slate-400" size={19} />
              <input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onFocus={() => setChatOpen(true)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleAsk();
                }}
                placeholder="Ask a question about your chart..."
                className="min-w-0 flex-1 bg-transparent px-1 py-3 text-sm outline-none placeholder:text-slate-400"
              />
              <button
                type="button"
                onClick={() => handleAsk()}
                disabled={chatLoading}
                className="send-button"
              >
                {chatLoading ? <LoaderCircle className="animate-spin" size={18} /> : <Send size={18} />}
              </button>
            </div>

            {chatOpen && (chatAnswer || chatLoading) && (
              <div className="chat-answer">
                <div className="mb-3 flex items-center justify-between">
                  <span className="text-xs font-extrabold uppercase tracking-[0.14em] text-violet-600">FutureLens</span>
                  <button type="button" onClick={() => { setChatAnswer(""); setChatOpen(false); }} className="text-slate-400 hover:text-slate-700">
                    <X size={17} />
                  </button>
                </div>
                {chatLoading ? (
                  <div className="flex items-center gap-2 text-sm text-slate-500">
                    <LoaderCircle className="animate-spin" size={17} />
                    Reviewing your chart and relevant evidence...
                  </div>
                ) : (
                  <p className="whitespace-pre-wrap text-[15px] leading-7 text-slate-700">{chatAnswer}</p>
                )}
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

function Field({ label, children }: { label: string; children: import("react").ReactNode }) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-bold text-slate-700">{label}</span>
      {children}
    </label>
  );
}

function EvidenceBlock({
  title,
  items,
  positive = false,
}: {
  title: string;
  items: EvidenceItem[];
  positive?: boolean;
}) {
  return (
    <div className="evidence-block">
      <h3 className="text-sm font-extrabold">{title}</h3>
      {items.length === 0 ? (
        <p className="mt-3 text-sm text-slate-400">No items supplied.</p>
      ) : (
        <div className="mt-3 space-y-3">
          {items.map((item, index) => (
            <details
              key={`${item.rule_id}-${index}`}
              className="evidence-row"
            >
              <summary className="flex cursor-pointer list-none items-start gap-3">
                <span className={`evidence-dot ${positive ? "positive" : "negative"}`} />
                <div className="min-w-0 flex-1">
                  <p className="text-sm leading-6 text-slate-700">{item.summary}</p>
                  {item.rule_id && (
                    <p className="mt-1 text-[11px] font-bold text-slate-400">
                      {item.rule_id}
                    </p>
                  )}
                </div>
              </summary>
              <div className="ml-6 mt-2 rounded-lg bg-slate-50 p-3 text-[11px] leading-5 text-slate-500">
                <p>{item.detail}</p>
                {item.classical_basis && (
                  <p className="mt-2 font-bold text-slate-400">
                    Source: {item.classical_basis}
                  </p>
                )}
              </div>
            </details>
          ))}
        </div>
      )}
    </div>
  );
}