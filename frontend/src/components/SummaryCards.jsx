import { Sparkles } from "lucide-react";

function SummaryCards({ cards }) {
  if (!cards?.length) {
    return null;
  }

  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {cards.map((card, index) => (
        <article
          key={`${card.title}-${index}`}
          className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-5 shadow-glow"
        >
          <div className="mb-4 flex items-center gap-2 text-indigo-400">
            <Sparkles size={16} />
            <p className="text-xs font-semibold uppercase tracking-[0.14em]">
              {card.title}
            </p>
          </div>
          <p className="mb-6 font-display text-3xl font-semibold leading-tight text-white">
            {card.value}
          </p>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm leading-6 text-slate-300">
            {card.summary}
          </div>
        </article>
      ))}
    </section>
  );
}

export default SummaryCards;
