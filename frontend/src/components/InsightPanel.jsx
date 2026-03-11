import { Sparkles } from "lucide-react";
import SummaryCards from "./SummaryCards";

function InsightPanel({ insight, sql, chartType, dataset, error, summaryCards, loading }) {
  return (
    <div className="space-y-4">
      <SummaryCards cards={summaryCards} />
      <aside className="rounded-[2rem] border border-white/10 bg-slate-900/70 p-5 shadow-glow">
        <div className="mb-4 flex items-center gap-2">
          <Sparkles className="text-amber-300" size={18} />
          <h2 className="font-display text-lg font-semibold text-white">
            AI Insights
          </h2>
        </div>

        {error ? (
          <p className="rounded-2xl border border-red-400/20 bg-red-400/10 p-4 text-sm text-red-100">
            {error}
          </p>
        ) : (
          <div className="space-y-4">
            <p className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm leading-6 text-slate-200">
              {insight || "Run a prompt to see an executive summary."}
            </p>
            {loading && (
              <div className="rounded-2xl border border-sky-400/20 bg-sky-400/10 p-4 text-sm text-sky-100">
                Loading deeper insights, root-cause analysis, and correlations...
              </div>
            )}
            <div className="grid gap-3 text-xs text-slate-400 md:grid-cols-3">
              <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
                <p className="mb-1 text-slate-500">Visualization</p>
                <p className="font-semibold uppercase tracking-wide text-slate-200">
                  {chartType || "N/A"}
                </p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
                <p className="mb-1 text-slate-500">Dataset</p>
                <p className="font-semibold text-slate-200">{dataset || "default"}</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
                <p className="mb-1 text-slate-500">Generated SQL</p>
                <p className="line-clamp-3 font-mono text-[11px] text-slate-200">
                  {sql || "Awaiting query"}
                </p>
              </div>
            </div>
          </div>
        )}
      </aside>
    </div>
  );
}

export default InsightPanel;
