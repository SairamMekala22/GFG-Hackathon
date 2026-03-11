import { Lightbulb } from "lucide-react";

function RecommendationPanel({ recommendations, loading }) {
  if (!loading && !recommendations?.length) {
    return null;
  }

  return (
    <section className="rounded-[2rem] border border-white/10 bg-slate-900/70 p-5 shadow-glow">
      <div className="mb-4 flex items-center gap-2">
        <Lightbulb className="text-amber-300" size={18} />
        <h2 className="font-display text-lg font-semibold text-white">
          Strategy Recommendations
        </h2>
      </div>
      {loading ? (
        <p className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
          Generating business recommendations from the current analysis context.
        </p>
      ) : (
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {recommendations.map((recommendation, index) => (
            <article
              key={`${recommendation}-${index}`}
              className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm leading-6 text-slate-200"
            >
              {recommendation}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

export default RecommendationPanel;
