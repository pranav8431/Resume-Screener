import { BarChart3, ClipboardList, FileUp, Layers3 } from 'lucide-react';

const items = [
  { label: 'Upload & Analyze', icon: FileUp, active: true },
  { label: 'Rankings & Scores', icon: BarChart3, active: false },
  { label: 'Candidate Details', icon: ClipboardList, active: false },
  { label: 'Export', icon: Layers3, active: false }
];

export function Sidebar() {
  return (
    <aside className="sticky top-0 hidden h-screen shrink-0 xl:flex xl:w-[290px] xl:flex-col xl:gap-6 xl:border-r xl:border-slate-800/80 xl:bg-slate-950/70 xl:px-5 xl:py-5 xl:backdrop-blur">
      <nav className="rounded-3xl border border-slate-800/80 bg-slate-900/70 p-3 shadow-soft ring-1 ring-white/5">
        <p className="px-3 py-2 text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Navigation</p>
        <div className="space-y-1">
          {items.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.label}
                className={`flex w-full items-center gap-3 rounded-2xl px-3 py-3 text-left text-sm font-medium transition-all duration-200 ${
                  item.active
                    ? 'bg-slate-800/80 text-white shadow-glow ring-1 ring-blue-500/30'
                    : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-100'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </nav>

      <div className="rounded-3xl border border-slate-800 bg-gradient-to-br from-blue-500/10 to-indigo-500/10 p-5 shadow-soft ring-1 ring-white/5">
        <p className="text-sm font-medium text-slate-200">Workflow status</p>
        <p className="mt-2 text-sm leading-6 text-slate-400">
          JD confirmation is required before resumes can be analyzed. This keeps the scoring pipeline deterministic.
        </p>
        <div className="mt-4 flex items-center gap-2 text-xs text-slate-300">
          <span className="h-2 w-2 rounded-full bg-emerald-400" /> Ready for review
        </div>
      </div>
    </aside>
  );
}