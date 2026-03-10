import {
  Bar,
  BarChart,
  Brush,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import { Expand } from "lucide-react";
import { useMemo, useState } from "react";

const COLORS = ["#38bdf8", "#22c55e", "#f59e0b", "#f97316", "#a78bfa", "#fb7185"];
const PLOT_OPTIONS = [
  { value: "line", label: "Line" },
  { value: "bar", label: "Bar" },
  { value: "pie", label: "Pie" },
  { value: "scatter", label: "Scatter" },
  { value: "table", label: "Table" }
];

function ChartWidget({ widget, onFilterChange, onMaximize, onChartTypeChange, expanded = false }) {
  const [hiddenKeys, setHiddenKeys] = useState([]);
  const { title, chartType, data, metadata } = widget;

  const keys = useMemo(() => {
    const xAxis = metadata?.x_axis;
    return Object.keys(data?.[0] || {}).filter((key) => key !== xAxis);
  }, [data, metadata]);

  const visibleKeys = keys.filter((key) => !hiddenKeys.includes(key));
  const supportedPlotOptions = useMemo(() => {
    const hasNumeric = keys.length > 0;
    const hasXAxis = Boolean(metadata?.x_axis);
    return PLOT_OPTIONS.filter((option) => {
      if (option.value === "pie") {
        return hasNumeric;
      }
      if (option.value === "scatter") {
        return keys.length > 1;
      }
      if (option.value === "line" || option.value === "bar") {
        return hasNumeric && hasXAxis;
      }
      return true;
    });
  }, [keys, metadata]);

  const handleLegendClick = (entry) => {
    const key = entry.dataKey;
    setHiddenKeys((current) =>
      current.includes(key) ? current.filter((item) => item !== key) : [...current, key]
    );
  };

  const renderCartesianChart = () => {
    const commonProps = {
      data,
      margin: { top: 10, right: 20, left: 0, bottom: 0 }
    };

    const series = visibleKeys.map((key, index) =>
      chartType === "line" ? (
        <Line
          key={key}
          type="monotone"
          dataKey={key}
          stroke={COLORS[index % COLORS.length]}
          strokeWidth={3}
          dot={{ r: 3 }}
          activeDot={{ r: 6 }}
        />
      ) : chartType === "scatter" ? (
        <Scatter
          key={key}
          name={key}
          dataKey={key}
          fill={COLORS[index % COLORS.length]}
        />
      ) : (
        <Bar
          key={key}
          dataKey={key}
          fill={COLORS[index % COLORS.length]}
          radius={[8, 8, 0, 0]}
        />
      )
    );

    const Chart = {
      line: LineChart,
      bar: BarChart,
      scatter: ScatterChart
    }[chartType] || BarChart;

    return (
      <ResponsiveContainer width="100%" height="100%">
        <Chart {...commonProps}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey={metadata?.x_axis} stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip
            contentStyle={{
              backgroundColor: "#020617",
              borderColor: "rgba(148, 163, 184, 0.25)",
              borderRadius: "16px"
            }}
          />
          <Legend onClick={handleLegendClick} />
          {series}
          {(chartType === "line" || chartType === "bar") && (
            <Brush
              dataKey={metadata?.x_axis}
              height={24}
              stroke="#38bdf8"
              onChange={(range) => onFilterChange?.(widget.id, range)}
            />
          )}
        </Chart>
      </ResponsiveContainer>
    );
  };

  const renderPie = () => {
    const valueKey = visibleKeys[0];
    return (
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Tooltip
            contentStyle={{
              backgroundColor: "#020617",
              borderColor: "rgba(148, 163, 184, 0.25)",
              borderRadius: "16px"
            }}
          />
          <Legend onClick={handleLegendClick} />
          <Pie
            data={data}
            dataKey={valueKey}
            nameKey={metadata?.x_axis}
            innerRadius={55}
            outerRadius={95}
            paddingAngle={2}
          >
            {data.map((entry, index) => (
              <Cell key={`${entry[metadata?.x_axis]}-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
    );
  };

  const renderTable = () => {
    const columns = Object.keys(data?.[0] || {});
    return (
      <div className="h-full overflow-auto rounded-2xl border border-white/10 bg-slate-900/50">
        <table className="min-w-full text-left text-xs text-slate-200">
          <thead className="sticky top-0 bg-slate-950/95 text-slate-400">
            <tr>
              {columns.map((column) => (
                <th key={column} className="px-3 py-2 font-semibold uppercase tracking-wide">
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, rowIndex) => (
              <tr key={`${title}-${rowIndex}`} className="border-t border-white/5">
                {columns.map((column) => (
                  <td key={`${rowIndex}-${column}`} className="px-3 py-2 text-slate-300">
                    {String(row[column] ?? "")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <section className="flex h-full flex-col rounded-[1.75rem] border border-white/10 bg-slate-950/80 p-4 shadow-glow">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <h3 className="font-display text-lg font-semibold text-white">{title}</h3>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
            {chartType} visualization
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={chartType}
            onChange={(event) => onChartTypeChange?.(widget.id, event.target.value)}
            className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-200 outline-none"
          >
            {supportedPlotOptions.map((option) => (
              <option key={option.value} value={option.value} className="bg-slate-950">
                {option.label}
              </option>
            ))}
          </select>
          {!expanded && chartType !== "table" && (
            <button
              type="button"
              onClick={() => onMaximize?.(widget)}
              className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-200 transition hover:bg-white/10"
            >
              <Expand size={14} />
              Maximize
            </button>
          )}
        </div>
      </div>
      <div className={expanded ? "min-h-[520px] flex-1" : "min-h-[260px] flex-1"}>
        {chartType === "table"
          ? renderTable()
          : chartType === "pie"
            ? renderPie()
            : renderCartesianChart()}
      </div>
    </section>
  );
}

export default ChartWidget;
