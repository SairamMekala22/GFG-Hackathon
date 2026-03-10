function LoadingSpinner({ label = "Analyzing your request..." }) {
  return (
    <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-200 shadow-glow">
      <div className="h-4 w-4 animate-spin rounded-full border-2 border-slate-500 border-t-signal" />
      <span>{label}</span>
    </div>
  );
}

export default LoadingSpinner;
