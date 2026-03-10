import { useState } from "react";

function SimulationPanel({ onSimulate, loading }) {
  const [scenario, setScenario] = useState("What if revenue increases by 15%?");

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!scenario.trim()) {
      return;
    }
    await onSimulate(scenario);
  };

  return (
    <section className="rounded-[2rem] border border-white/10 bg-white/5 p-5 shadow-glow">
      <h2 className="font-display text-xl font-semibold text-white">What-If Simulation</h2>
      <p className="mt-1 text-sm text-slate-400">
        Explore hypothetical changes with a simple decision simulation model.
      </p>
      <form onSubmit={handleSubmit} className="mt-4 flex flex-col gap-3 md:flex-row">
        <input
          value={scenario}
          onChange={(event) => setScenario(event.target.value)}
          className="flex-1 rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-slate-100 outline-none placeholder:text-slate-500 focus:border-signal"
          placeholder="What if ad spend increases by 20%?"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-full bg-amber-300 px-5 py-3 text-sm font-semibold text-slate-950 hover:bg-amber-200 disabled:opacity-60"
        >
          {loading ? "Simulating..." : "Run Simulation"}
        </button>
      </form>
    </section>
  );
}

export default SimulationPanel;
