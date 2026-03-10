import { Download } from "lucide-react";
import { WidthProvider, Responsive } from "react-grid-layout";
import ChartWidget from "./ChartWidget";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";

const ResponsiveGridLayout = WidthProvider(Responsive);

function Dashboard({ widgets, onLayoutsChange, onFilterChange, onMaximizeWidget, onChartTypeChange }) {
  const exportToPdf = async () => {
    const element = document.getElementById("dashboard-export");
    if (!element) {
      return;
    }

    const [{ default: html2canvas }, { default: jsPDF }] = await Promise.all([
      import("html2canvas"),
      import("jspdf")
    ]);

    const canvas = await html2canvas(element, { scale: 2, backgroundColor: "#020617" });
    const imageData = canvas.toDataURL("image/png");
    const pdf = new jsPDF("landscape", "px", [canvas.width, canvas.height]);
    pdf.addImage(imageData, "PNG", 0, 0, canvas.width, canvas.height);
    pdf.save("executive-dashboard.pdf");
  };

  return (
    <section className="rounded-[2rem] border border-white/10 bg-white/5 p-5 shadow-glow">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <h2 className="font-display text-xl font-semibold text-white">Dashboard Grid</h2>
          <p className="text-sm text-slate-400">
            Drag, resize, export, and collaborate in real time.
          </p>
        </div>
        <button
          type="button"
          onClick={exportToPdf}
          className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-4 py-2 text-sm font-medium text-slate-100 transition hover:bg-white/20"
        >
          <Download size={16} />
          Export Dashboard
        </button>
      </div>

      {widgets.length === 0 ? (
        <div className="rounded-[1.75rem] border border-dashed border-white/10 bg-slate-950/50 px-6 py-14 text-center">
          <p className="font-display text-xl text-white">No widgets yet</p>
          <p className="mx-auto mt-2 max-w-xl text-sm text-slate-400">
            Upload a CSV or ask a business question to generate your first chart or dataset answer.
          </p>
        </div>
      ) : (
        <div id="dashboard-export">
          <ResponsiveGridLayout
            className="grid-layout"
            rowHeight={40}
            layouts={{ lg: widgets.map((widget) => widget.layout) }}
            cols={{ lg: 12, md: 10, sm: 6, xs: 4 }}
            breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480 }}
            onLayoutChange={(layout) => onLayoutsChange?.(layout)}
            draggableHandle=".font-display"
          >
            {widgets.map((widget) => (
              <div key={widget.id}>
                <ChartWidget
                  widget={widget}
                  onFilterChange={onFilterChange}
                  onMaximize={onMaximizeWidget}
                  onChartTypeChange={onChartTypeChange}
                />
              </div>
            ))}
          </ResponsiveGridLayout>
        </div>
      )}
    </section>
  );
}

export default Dashboard;
