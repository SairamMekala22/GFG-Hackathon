import { WandSparkles } from "lucide-react";
import { useState } from "react";

function ChartEditorPanel({ onEdit, loading }) {
  const [editPrompt, setEditPrompt] = useState("Sort by revenue descending");

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!editPrompt.trim()) {
      return;
    }
    await onEdit(editPrompt);
  };

  return (
    <div className="mb-4 rounded-2xl border border-white/10 bg-white/5 p-4">
      <div className="mb-3 flex items-center gap-2 text-slate-100">
        <WandSparkles size={16} className="text-amber-300" />
        <p className="text-sm font-semibold">Chart Editor</p>
      </div>
      <form onSubmit={handleSubmit} className="space-y-3">
        <input
          value={editPrompt}
          onChange={(event) => setEditPrompt(event.target.value)}
          className="w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-slate-100 outline-none placeholder:text-slate-500 focus:border-signal"
          placeholder="Make this a stacked bar chart"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-full bg-white px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-slate-200 disabled:opacity-60"
        >
          {loading ? "Applying..." : "Apply Edit"}
        </button>
      </form>
    </div>
  );
}

export default ChartEditorPanel;
