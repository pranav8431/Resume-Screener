interface StatCardProps {
  label: string;
  value: string;
  tone: 'slate' | 'emerald' | 'amber' | 'rose';
}

const toneMap = {
  slate: 'from-slate-800/90 to-slate-900 border-slate-700 text-slate-100',
  emerald: 'from-emerald-500/15 to-slate-900 border-emerald-500/25 text-emerald-300',
  amber: 'from-amber-500/15 to-slate-900 border-amber-500/25 text-amber-300',
  rose: 'from-rose-500/15 to-slate-900 border-rose-500/25 text-rose-300'
};

function StatCard({ label, value, tone }: StatCardProps) {
  return (
    <div className={`rounded-3xl border bg-gradient-to-br p-5 shadow-soft ring-1 ring-white/5 ${toneMap[tone]}`}>
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-3 text-3xl font-semibold tracking-tight text-white">{value}</p>
    </div>
  );
}

interface StatCardsProps {
  stats: StatCardProps[];
}

export function StatCards({ stats }: StatCardsProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {stats.map((stat) => (
        <StatCard key={stat.label} {...stat} />
      ))}
    </div>
  );
}