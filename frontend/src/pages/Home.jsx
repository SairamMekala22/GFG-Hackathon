import { useCallback, useEffect, useState } from "react";
import Dashboard from "../components/Dashboard";
import DatasetSummary from "../components/DatasetSummary";
import FileUpload from "../components/FileUpload";
import InsightPanel from "../components/InsightPanel";
import LoadingSpinner from "../components/LoadingSpinner";
import PromptInput from "../components/PromptInput";
import { followUp, generateDashboard, getDatasetProfile, uploadCsv } from "../services/api";
import { useSocket } from "../hooks/useSocket";

function normalizeWidget(response, index = 0) {
  const id = response.widget_id || `widget-${Date.now()}-${index}`;
  return {
    id,
    title: response.title || response.prompt || "Generated Chart",
    chartType: response.chartType || response.chart_type,
    data: response.data || [],
    metadata: response.metadata || response.chart_metadata || {},
    layout: response.layout || { i: id, x: (index * 6) % 12, y: Infinity, w: 6, h: 8 }
  };
}

function Home() {
  const [widgets, setWidgets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [insight, setInsight] = useState("");
  const [sql, setSql] = useState("");
  const [chartType, setChartType] = useState("");
  const [dataset, setDataset] = useState("sales_data");
  const [datasetProfile, setDatasetProfile] = useState(null);
  const [hasUploadedDataset, setHasUploadedDataset] = useState(false);
  const [summaryCards, setSummaryCards] = useState([]);
  const [error, setError] = useState("");
  const [sessionId] = useState(() => crypto.randomUUID());

  const handleDashboardEvent = useCallback((payload) => {
    if (payload?.widgets) {
      setWidgets(payload.widgets.map(normalizeWidget));
    }
    if (payload?.insight) {
      setInsight(payload.insight);
    }
    if (payload?.summary_cards) {
      setSummaryCards(payload.summary_cards);
    }
  }, []);

  const { socket, isConnected } = useSocket(sessionId, handleDashboardEvent);

  useEffect(() => {
    if (!socket) {
      return;
    }

    socket.emit("join_session", { session_id: sessionId });
  }, [sessionId, socket]);

  const submitPrompt = async (prompt, isFollowUp = false) => {
    setLoading(true);
    setError("");

    try {
      const payload = { prompt, session_id: sessionId };
      const response = isFollowUp
        ? await followUp(payload)
        : await generateDashboard(payload);

      const nextWidget = normalizeWidget({ ...response, prompt }, widgets.length);
      const nextWidgets = response.replace_dashboard ? [nextWidget] : [...widgets, nextWidget];

      setWidgets(nextWidgets);
      setInsight(response.insight);
      setSummaryCards(response.summary_cards || []);
      setSql(response.sql);
      setChartType(response.chart_type);
      setDataset(response.dataset || dataset);
      if (hasUploadedDataset && response.dataset && response.dataset !== dataset) {
        const profile = await getDatasetProfile(sessionId);
        setDatasetProfile(profile);
      }

      socket?.emit("dashboard_update", {
        session_id: sessionId,
        widgets: nextWidgets,
        insight: response.insight,
        summary_cards: response.summary_cards || []
      });
    } catch (requestError) {
      setError(
        requestError?.response?.data?.error ||
          "Sorry, the system could not answer this query using the available dataset."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (file) => {
    setUploading(true);
    setError("");
    try {
      const response = await uploadCsv(file, sessionId);
      setDataset(response.table_name);
      setDatasetProfile(response.profile || null);
      setHasUploadedDataset(true);
      setWidgets([]);
      setSql("");
      setChartType("");
      setSummaryCards([]);
      setInsight(
        `Dataset ${response.table_name} uploaded successfully with ${response.row_count} rows, ${response.columns.length} columns, and ${response.encoding} encoding. Ask a question about this data next.`
      );
    } catch (uploadError) {
      setDatasetProfile(null);
      setHasUploadedDataset(false);
      setError(uploadError?.response?.data?.error || "CSV upload failed.");
    } finally {
      setUploading(false);
    }
  };

  const handleLayoutsChange = (layout) => {
    setWidgets((current) =>
      current.map((widget) => ({
        ...widget,
        layout: layout.find((item) => item.i === widget.id) || widget.layout
      }))
    );
  };

  const handleFilterChange = (widgetId, range) => {
    socket?.emit("filter_change", { session_id: sessionId, widget_id: widgetId, range });
  };

  return (
    <main className="min-h-screen px-4 py-8 text-slate-100 md:px-8">
      <div className="mx-auto flex max-w-7xl flex-col gap-6">
        <header className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-signal">AI-native BI</p>
            <h1 className="font-display text-4xl font-semibold text-white">
              Natural Language Dashboard Studio
            </h1>
          </div>
          <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs text-slate-300">
            Session {isConnected ? "live" : "offline"} | Dataset: {dataset}
          </div>
        </header>

        <PromptInput onSubmit={(prompt) => submitPrompt(prompt, widgets.length > 0)} loading={loading} />
        <FileUpload onUpload={handleUpload} uploading={uploading} />
        {loading && <LoadingSpinner />}
        {hasUploadedDataset && <DatasetSummary profile={datasetProfile} />}
        <Dashboard
          widgets={widgets}
          onLayoutsChange={handleLayoutsChange}
          onFilterChange={handleFilterChange}
        />
        <InsightPanel
          insight={insight}
          sql={sql}
          chartType={chartType}
          dataset={dataset}
          error={error}
          summaryCards={summaryCards}
        />
      </div>
    </main>
  );
}

export default Home;
