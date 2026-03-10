function DatasetSummary({ profile }) {
  if (!profile) {
    return null;
  }

  return (
    <section className="rounded-[2rem] border border-white/10 bg-white/5 p-5 shadow-glow">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="font-display text-xl font-semibold text-white">Dataset Summary</h2>
          <p className="text-sm text-slate-400">
            {profile.table_name} with {profile.row_count} rows and {profile.columns.length} columns
          </p>
        </div>
        <div className="flex flex-wrap gap-2 text-xs text-slate-300">
          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5">
            {profile.has_date_column ? "Time-aware dataset" : "No date column detected"}
          </span>
          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5">
            {profile.numeric_like_columns.length} metric columns
          </span>
        </div>
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        {profile.columns.map((column) => (
          <span
            key={column.name}
            className="rounded-full border border-signal/20 bg-signal/10 px-3 py-1.5 text-xs text-sky-100"
          >
            {column.name}
          </span>
        ))}
      </div>

      {!!profile.sample_rows?.length && (
        <div className="overflow-auto rounded-2xl border border-white/10 bg-slate-950/60">
          <table className="min-w-full text-left text-xs text-slate-200">
            <thead className="bg-slate-950/90 text-slate-400">
              <tr>
                {Object.keys(profile.sample_rows[0]).map((column) => (
                  <th key={column} className="px-3 py-2 font-semibold uppercase tracking-wide">
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {profile.sample_rows.map((row, index) => (
                <tr key={index} className="border-t border-white/5">
                  {Object.keys(profile.sample_rows[0]).map((column) => (
                    <td key={`${index}-${column}`} className="px-3 py-2 text-slate-300">
                      {String(row[column] ?? "")}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default DatasetSummary;
