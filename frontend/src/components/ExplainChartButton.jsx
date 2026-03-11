import { Sparkles } from "lucide-react";

function ExplainChartButton({ onClick, loading }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={loading}
      className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-200 transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-60"
    >
      <Sparkles size={14} />
      {loading ? "Explaining..." : "Explain Chart"}
    </button>
  );
}

export default ExplainChartButton;
