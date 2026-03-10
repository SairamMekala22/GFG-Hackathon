import { SendHorizontal } from "lucide-react";
import VoiceInput from "./VoiceInput";

const EXAMPLES = [
  "Show monthly revenue trends for 2024 and highlight the best performing region",
  "Compare sales across product categories",
  "Which region had the highest growth this quarter?"
];

function PromptInput({ onSubmit, loading, prompt, onPromptChange, suggestedPrompts = [] }) {
  const prompts = suggestedPrompts.length ? suggestedPrompts : EXAMPLES;

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!prompt.trim()) {
      return;
    }
    await onSubmit(prompt);
  };

  return (
    <div className="rounded-[2rem] border border-white/10 bg-white/5 p-5 shadow-glow backdrop-blur">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="font-display text-2xl font-semibold text-white">
            Executive Prompt Console
          </p>
          <p className="mt-1 max-w-2xl text-sm text-slate-300">
            Ask in plain English. The app will generate SQL, select visuals, and
            produce an AI summary.
          </p>
        </div>
        <VoiceInput onTranscript={onPromptChange} />
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          value={prompt}
          onChange={(event) => onPromptChange(event.target.value)}
          rows={4}
          placeholder="Show revenue by region and flag top growth areas."
          className="w-full rounded-3xl border border-white/10 bg-slate-950/70 px-4 py-4 text-sm text-slate-100 outline-none ring-0 placeholder:text-slate-500 focus:border-signal"
        />
        <div className="flex flex-wrap gap-2">
          {prompts.map((example) => (
            <button
              key={example}
              type="button"
              onClick={() => onPromptChange(example)}
              className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-slate-300 transition hover:border-signal/60 hover:text-white"
            >
              {example}
            </button>
          ))}
        </div>
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-full bg-accent px-5 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <SendHorizontal size={16} />
            {loading ? "Generating..." : "Generate Dashboard"}
          </button>
        </div>
      </form>
    </div>
  );
}

export default PromptInput;
