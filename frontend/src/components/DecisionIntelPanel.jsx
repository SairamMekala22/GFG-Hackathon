function DecisionIntelPanel({ rootCause, correlations, simulation, loading }) {
  if (!rootCause && !correlations?.length && !simulation && !loading) {
    return null;
  }

  return (
    <section className="grid gap-4 xl:grid-cols-3">
      <article className="rounded-[2rem] border border-white/10 bg-white/5 p-5 shadow-glow">
        <h3 className="font-display text-lg font-semibold text-white">Root Cause</h3>
        {rootCause?.confidence && (
          <p className="mt-2 text-xs uppercase tracking-[0.18em] text-slate-500">
            Confidence: {rootCause.confidence}
          </p>
        )}
        <div className="mt-4 space-y-3">
          {loading && !rootCause?.root_causes?.length && (
            <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-3 text-sm text-slate-400">
              Loading root-cause analysis...
            </div>
          )}
          {rootCause?.root_causes?.length ? (
            rootCause.root_causes.map((cause) => (
              <div key={cause} className="rounded-2xl border border-white/10 bg-slate-950/70 p-3 text-sm text-slate-200">
                {cause}
              </div>
            ))
          ) : (
            <p className="text-sm text-slate-400">No strong root-cause explanation available yet.</p>
          )}
        </div>
      </article>

      <article className="rounded-[2rem] border border-white/10 bg-white/5 p-5 shadow-glow">
        <h3 className="font-display text-lg font-semibold text-white">Correlations</h3>
        <div className="mt-4 space-y-3">
          {loading && !correlations?.length && (
            <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-3 text-sm text-slate-400">
              Loading correlation discovery...
            </div>
          )}
          {correlations?.length ? (
            correlations.map((item) => (
              <div key={`${item.metric_a}-${item.metric_b}`} className="rounded-2xl border border-white/10 bg-slate-950/70 p-3 text-sm text-slate-200">
                <p className="font-semibold text-white">
                  {item.metric_a} ↔ {item.metric_b}
                </p>
                <p className="mt-1 text-slate-400">Correlation: {item.value}</p>
              </div>
            ))
          ) : (
            <p className="text-sm text-slate-400">No strong numeric relationships detected yet.</p>
          )}
        </div>
      </article>

      <article className="rounded-[2rem] border border-white/10 bg-white/5 p-5 shadow-glow">
        <h3 className="font-display text-lg font-semibold text-white">Simulation</h3>
        <div className="mt-4">
          {simulation ? (
            <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-slate-200">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Scenario</p>
              <p className="mt-1 font-semibold text-white">{simulation.scenario}</p>
              <p className="mt-3 text-slate-400">
                Predicted change: {simulation.predicted_target_change}
              </p>
              <p className="mt-1 text-slate-400">
                Estimated {simulation.target_metric}: {simulation.estimated_target_value}
              </p>
              <p className="mt-3 text-xs uppercase tracking-[0.18em] text-slate-500">
                Confidence: {simulation.confidence || "unknown"}
              </p>
              <p className="mt-1 text-xs text-slate-500">
                Method: {simulation.method || "unspecified"}
              </p>
            </div>
          ) : (
            <p className="text-sm text-slate-400">Run a what-if prompt like “What if ad spend increases by 20%?”</p>
          )}
        </div>
      </article>
    </section>
  );
}

export default DecisionIntelPanel;
