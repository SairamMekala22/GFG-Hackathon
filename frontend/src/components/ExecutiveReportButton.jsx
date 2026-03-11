import { Download, FileText, X } from "lucide-react";

function ExecutiveReportButton({
  loading,
  report,
  onGenerate,
  onClose,
  onDownloadPdf,
  onDownloadMarkdown
}) {
  return (
    <>
      <button
        type="button"
        onClick={onGenerate}
        disabled={loading}
        className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-4 py-2 text-sm font-medium text-slate-100 transition hover:bg-white/20 disabled:cursor-not-allowed disabled:opacity-60"
      >
        <FileText size={16} />
        {loading ? "Generating Report..." : "Generate Executive Report"}
      </button>

      {report && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-sm">
          <div className="w-full max-w-4xl rounded-[2rem] border border-white/10 bg-[#040816] p-5 shadow-glow">
            <div className="mb-4 flex items-start justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                  Executive report preview
                </p>
                <h2 className="font-display text-2xl font-semibold text-white">
                  Dashboard Decision Memo
                </h2>
              </div>
              <button
                type="button"
                onClick={onClose}
                className="rounded-full border border-white/10 bg-white/10 p-2 text-slate-200 hover:bg-white/20"
              >
                <X size={16} />
              </button>
            </div>

            <div className="grid gap-3 md:grid-cols-3">
              <button
                type="button"
                onClick={onDownloadPdf}
                className="inline-flex items-center justify-center gap-2 rounded-full bg-signal px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-sky-300"
              >
                <Download size={16} />
                Download PDF
              </button>
              <button
                type="button"
                onClick={onDownloadMarkdown}
                className="inline-flex items-center justify-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-100 hover:bg-white/10"
              >
                <FileText size={16} />
                Download Markdown
              </button>
              <button
                type="button"
                onClick={onClose}
                className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-100 hover:bg-white/10"
              >
                Close Preview
              </button>
            </div>

            <div className="mt-5 max-h-[65vh] overflow-auto rounded-[1.5rem] border border-white/10 bg-slate-950/70 p-5">
              <div className="space-y-5 text-sm text-slate-200">
                <section>
                  <h3 className="font-display text-lg font-semibold text-white">Executive Summary</h3>
                  <p className="mt-2 leading-7">{report.report?.executive_summary}</p>
                </section>

                {[
                  ["Key Insights", report.report?.key_insights],
                  ["Anomalies", report.report?.anomalies],
                  ["Root Causes", report.report?.root_causes],
                  ["Recommendations", report.report?.recommendations],
                  ["Forecast", report.report?.forecast]
                ].map(([title, values]) => (
                  <section key={title}>
                    <h3 className="font-display text-lg font-semibold text-white">{title}</h3>
                    <div className="mt-3 space-y-2">
                      {(values?.length ? values : ["No items available."]).map((value, index) => (
                        <div
                          key={`${title}-${index}`}
                          className="rounded-2xl border border-white/10 bg-white/5 p-3 leading-6"
                        >
                          {value}
                        </div>
                      ))}
                    </div>
                  </section>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default ExecutiveReportButton;
