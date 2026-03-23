import { useState } from "react";
import { analyzeStock } from "./api/biothrone";
import type { AnalysisResult } from "./api/biothrone";

const SUGGESTIONS = [
  "Should I invest in Moderna?",
  "Analyze Eli Lilly and Co",
  "Is Regeneron a good buy?",
  "What's your view on CRISPR Therapeutics?",
];

const DECISION_STYLES: Record<string, { bg: string; text: string; dot: string }> = {
  BUY:   { bg: "bg-emerald-500/15", text: "text-emerald-400", dot: "bg-emerald-400" },
  HOLD:  { bg: "bg-yellow-500/15",  text: "text-yellow-400",  dot: "bg-yellow-400"  },
  SELL:  { bg: "bg-red-500/15",     text: "text-red-400",     dot: "bg-red-400"     },
  AVOID: { bg: "bg-orange-500/15",  text: "text-orange-400",  dot: "bg-orange-400"  },
};

function getDecisionStyle(decision: string) {
  return DECISION_STYLES[decision.toUpperCase()] ?? DECISION_STYLES["HOLD"];
}

function confidenceColor(confidence: number) {
  if (confidence >= 70) return "bg-emerald-500";
  if (confidence >= 40) return "bg-yellow-500";
  return "bg-red-500";
}

export default function App() {
  const [input, setInput] = useState("");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [query, setQuery] = useState("");

  async function handleSubmit(q: string) {
    if (!q.trim() || loading) return;

    setResult(null);
    setError("");
    setLoading(true);
    setSubmitted(true);
    setQuery(q);

    try {
      const data = await analyzeStock(q);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not reach the server. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  function handleFormSubmit(e: React.FormEvent) {
    e.preventDefault();
    handleSubmit(input);
  }

  function handleReset() {
    setSubmitted(false);
    setResult(null);
    setError("");
    setInput("");
    setLoading(false);
    setQuery("");
  }

  return (
    <div className="min-h-screen bg-[#080A0E] text-white flex flex-col" style={{ fontFamily: "'DM Mono', monospace" }}>

      {/* Ambient background */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-20%] left-[10%] w-[500px] h-[500px] rounded-full bg-emerald-900/20 blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[5%] w-[400px] h-[400px] rounded-full bg-teal-900/15 blur-[100px]" />
      </div>

      <div className="relative z-10 flex flex-col min-h-screen max-w-3xl mx-auto w-full px-6 py-12">

        {/* Header */}
        <header className="mb-16">
          <h1
            className="text-5xl font-extrabold tracking-tight text-white leading-none mb-2"
            style={{ fontFamily: "'Syne', sans-serif" }}
          >
            Biothrone
          </h1>
          <p className="text-zinc-500 text-sm">AI-powered biotech investment intelligence</p>
        </header>

        {/* Main content */}
        {!submitted ? (
          <div className="flex-1 flex flex-col">
            <form onSubmit={handleFormSubmit} className="mb-10">
              <div className="relative">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask about any biotech stock..."
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-5 py-4 pr-32 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-emerald-500/50 focus:bg-white/8 transition-all duration-200"
                />
                <button
                  type="submit"
                  disabled={!input.trim()}
                  className="absolute right-2 top-1/2 -translate-y-1/2 bg-emerald-500 hover:bg-emerald-400 disabled:bg-zinc-700 disabled:text-zinc-500 text-black text-xs font-semibold px-4 py-2 rounded-lg transition-all duration-150 tracking-wide"
                >
                  ANALYZE
                </button>
              </div>
            </form>

            <div>
              <p className="text-zinc-600 text-xs tracking-widest uppercase mb-4">Suggestions</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => { setInput(s); handleSubmit(s); }}
                    className="text-left text-xs text-zinc-400 bg-white/3 hover:bg-white/7 border border-white/8 hover:border-emerald-500/30 rounded-lg px-4 py-3 transition-all duration-150 hover:text-emerald-300"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          </div>

        ) : (

          <div className="flex-1 flex flex-col">

            {/* Query label */}
            <div className="flex items-start justify-between mb-8 gap-4">
              <div>
                <p className="text-zinc-600 text-xs tracking-widest uppercase mb-1">Query</p>
                <p className="text-white text-sm">{query}</p>
              </div>
              <button
                onClick={handleReset}
                className="shrink-0 text-xs text-zinc-500 hover:text-white border border-white/10 hover:border-white/30 px-3 py-1.5 rounded-lg transition-all duration-150"
              >
                ← New query
              </button>
            </div>

            {/* Loading state */}
            {loading && (
              <div className="flex-1 bg-white/3 border border-white/8 rounded-xl p-6">
                <div className="flex items-center gap-2 mb-5">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-xs tracking-widest uppercase text-zinc-500">Analyzing...</span>
                </div>
                <div className="flex gap-1.5 items-center">
                  {[0, 1, 2].map((i) => (
                    <div
                      key={i}
                      className="w-1 h-1 rounded-full bg-emerald-500 animate-bounce"
                      style={{ animationDelay: `${i * 0.15}s` }}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Error state */}
            {error && !loading && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-6">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            {/* Result card */}
            {result && !loading && (
              <div className="flex flex-col gap-4">

                {/* Ticker + Decision */}
                <div className="bg-white/3 border border-white/8 rounded-xl p-6 flex items-center justify-between gap-6">
                  <div>
                    <p className="text-zinc-600 text-xs tracking-widest uppercase mb-1">Ticker</p>
                    <p className="text-white text-3xl font-bold tracking-wider" style={{ fontFamily: "'Syne', sans-serif" }}>
                      {result.ticker.toUpperCase()}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-zinc-600 text-xs tracking-widest uppercase mb-2">Decision</p>
                    <span className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-bold tracking-widest uppercase ${getDecisionStyle(result.decision).bg} ${getDecisionStyle(result.decision).text}`}>
                      <span className={`w-2 h-2 rounded-full ${getDecisionStyle(result.decision).dot}`} />
                      {result.decision}
                    </span>
                  </div>
                </div>

                {/* Confidence */}
                <div className="bg-white/3 border border-white/8 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-3">
                    <p className="text-zinc-600 text-xs tracking-widest uppercase">Confidence</p>
                    <p className="text-white text-sm font-semibold">{result.confidence}%</p>
                  </div>
                  <div className="w-full h-2 bg-white/8 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-700 ${confidenceColor(result.confidence)}`}
                      style={{ width: `${result.confidence}%` }}
                    />
                  </div>
                </div>

                {/* Reasoning */}
                <div className="bg-white/3 border border-white/8 rounded-xl p-6">
                  <p className="text-zinc-600 text-xs tracking-widest uppercase mb-4">Reasoning</p>
                  <p className="text-zinc-300 text-sm leading-relaxed whitespace-pre-wrap">{result.reasoning}</p>
                </div>

              </div>
            )}

          </div>
        )}

        {/* Footer */}
        <footer className="mt-12 pt-6 border-t border-white/5">
          <p className="text-zinc-700 text-xs text-center">
            Not financial advice · For research purposes only
          </p>
        </footer>

      </div>
    </div>
  );
}