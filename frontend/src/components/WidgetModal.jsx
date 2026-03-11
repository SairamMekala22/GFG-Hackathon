import { Maximize2, MessageSquarePlus, Minimize2, X } from "lucide-react";
import { useState } from "react";
import ChartEditorPanel from "./ChartEditorPanel";
import ChartWidget from "./ChartWidget";

function WidgetModal({
  widget,
  annotations,
  onAddAnnotation,
  onClose,
  onChartTypeChange,
  onExplainChart,
  onEditChart,
  editLoading
}) {
  const [note, setNote] = useState("");

  if (!widget) {
    return null;
  }

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!note.trim()) {
      return;
    }
    onAddAnnotation(widget.id, note.trim());
    setNote("");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-sm">
      <div className="grid h-[88vh] w-full max-w-7xl gap-4 rounded-[2rem] border border-white/10 bg-[#040816] p-4 shadow-glow lg:grid-cols-[minmax(0,1.5fr)_340px]">
        <div className="flex min-h-0 flex-col rounded-[1.75rem] border border-white/10 bg-white/5 p-4">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                Expanded analysis
              </p>
              <h2 className="font-display text-2xl font-semibold text-white">
                {widget.title}
              </h2>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-4 py-2 text-sm text-slate-100 hover:bg-white/20"
            >
              <Minimize2 size={16} />
              Close
            </button>
          </div>
          <div className="min-h-0 flex-1">
            <ChartWidget
              widget={widget}
              expanded
              onChartTypeChange={onChartTypeChange}
              onExplainChart={onExplainChart}
            />
          </div>
        </div>

        <aside className="flex min-h-0 flex-col rounded-[1.75rem] border border-white/10 bg-slate-950/80 p-4">
          <ChartEditorPanel
            onEdit={(editPrompt) => onEditChart?.(widget, editPrompt)}
            loading={editLoading}
          />
          <div className="mb-4 flex items-center gap-2 text-slate-100">
            <MessageSquarePlus size={18} className="text-signal" />
            <h3 className="font-display text-lg font-semibold">Annotations</h3>
          </div>

          <form onSubmit={handleSubmit} className="mb-4 space-y-3">
            <textarea
              value={note}
              onChange={(event) => setNote(event.target.value)}
              rows={4}
              placeholder="Add an observation, risk, or takeaway for this chart."
              className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-100 outline-none placeholder:text-slate-500 focus:border-signal"
            />
            <button
              type="submit"
              className="inline-flex items-center gap-2 rounded-full bg-signal px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-sky-300"
            >
              <MessageSquarePlus size={16} />
              Add Annotation
            </button>
          </form>

          <div className="min-h-0 flex-1 space-y-3 overflow-auto">
            {annotations?.length ? (
              annotations.map((annotation, index) => (
                <div
                  key={`${widget.id}-annotation-${index}`}
                  className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-200"
                >
                  <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-slate-500">
                    <Maximize2 size={12} />
                    Chart note
                  </div>
                  <p>{annotation}</p>
                </div>
              ))
            ) : (
              <div className="rounded-2xl border border-dashed border-white/10 bg-white/5 p-4 text-sm text-slate-400">
                No annotations yet. Use this panel to capture decisions, anomalies, and talking points.
              </div>
            )}
          </div>
        </aside>
      </div>
      <button
        type="button"
        onClick={onClose}
        className="absolute right-6 top-6 rounded-full border border-white/10 bg-white/10 p-2 text-slate-200 hover:bg-white/20"
      >
        <X size={16} />
      </button>
    </div>
  );
}

export default WidgetModal;
