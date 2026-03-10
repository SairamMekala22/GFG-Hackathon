function DataQualityPanel({ report }) {
  if (!report) {
    return null;
  }

  return (
    <section className="rounded-[2rem] border border-white/10 bg-white/5 p-5 shadow-glow">
      <div className="mb-4">
        <h2 className="font-display text-xl font-semibold text-white">Data Quality</h2>
        <p className="text-sm text-slate-400">
          Automatic checks for missing values, duplicates, type inconsistencies, and outliers.
        </p>
      </div>

      <div className="grid gap-3 md:grid-cols-4">
        <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Missing Fields</p>
          <p className="mt-2 text-2xl font-semibold text-white">
            {Object.keys(report.missing_values || {}).length}
          </p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Duplicate Rows</p>
          <p className="mt-2 text-2xl font-semibold text-white">{report.duplicates || 0}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Type Issues</p>
          <p className="mt-2 text-2xl font-semibold text-white">
            {Object.keys(report.inconsistent_types || {}).length}
          </p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Outlier Columns</p>
          <p className="mt-2 text-2xl font-semibold text-white">
            {Object.keys(report.outliers || {}).length}
          </p>
        </div>
      </div>

      {!!report.warnings?.length && (
        <div className="mt-4 space-y-2">
          {report.warnings.map((warning) => (
            <div
              key={warning}
              className="rounded-2xl border border-amber-300/20 bg-amber-400/10 p-3 text-sm text-amber-100"
            >
              {warning}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

export default DataQualityPanel;
