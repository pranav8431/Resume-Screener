import { ArrowUpDown, BadgeCheck, Search } from 'lucide-react';
import type { Candidate } from '../types';

interface RankingTableProps {
  candidates: Candidate[];
}

const recTone: Record<Candidate['recommendation'], string> = {
  'Call First': 'bg-emerald-500/15 text-emerald-300 border-emerald-500/20',
  Backup: 'bg-amber-500/15 text-amber-300 border-amber-500/20',
  'Not Suitable': 'bg-rose-500/15 text-rose-300 border-rose-500/20'
};

export function RankingTable({ candidates }: RankingTableProps) {
  return (
    <section className="rounded-3xl border border-sky-500/20 bg-[#050816]/90 p-6 shadow-soft ring-1 ring-sky-400/10">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-lg font-semibold text-white">Rankings & Scores</p>
          <p className="mt-1 text-sm text-sky-200/70">Sorted by overall fit with hover-friendly row styling and chip-based metadata.</p>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row">
          <label className="flex items-center gap-2 rounded-xl border border-sky-500/20 bg-black/70 px-4 py-2 text-sm text-sky-200/70">
            <Search className="h-4 w-4" />
            <input placeholder="Search candidates" className="w-40 bg-transparent outline-none placeholder:text-slate-500" />
          </label>
          <button className="inline-flex items-center justify-center gap-2 rounded-xl border border-sky-500/20 bg-black/70 px-4 py-2 text-sm font-medium text-sky-100 transition hover:border-sky-400/40 hover:bg-sky-500/10">
            <ArrowUpDown className="h-4 w-4" />
            Sort
          </button>
        </div>
      </div>

      <div className="mt-6 overflow-hidden rounded-2xl border border-sky-500/20 bg-black/70">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-sky-500/10 text-left text-sm">
            <thead className="bg-black/90 text-sky-200/70">
              <tr>
                {['Rank', 'Name', 'Score', 'Recommendation', 'Matched Skills', 'Missing Skills'].map((heading) => (
                  <th key={heading} className="whitespace-nowrap px-5 py-4 font-medium tracking-wide">
                    {heading}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-sky-500/10 text-slate-100">
              {candidates.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-5 py-10 text-center text-sm text-sky-200/70">
                    No analyzed candidates yet. Upload resumes and run analysis to view rankings.
                  </td>
                </tr>
              ) : (
                candidates.map((candidate) => (
                  <tr key={candidate.id} className="group transition hover:bg-sky-500/5">
                    <td className="whitespace-nowrap px-5 py-5 font-semibold text-white">{candidate.rank}</td>
                    <td className="whitespace-nowrap px-5 py-5">
                      <div className="font-medium text-white">{candidate.name}</div>
                      <div className="mt-1 text-xs text-sky-200/55">{candidate.location} · {candidate.experienceYears} yrs</div>
                    </td>
                    <td className="px-5 py-5">
                      <div className="flex items-center gap-3">
                        <div className="h-2.5 w-32 overflow-hidden rounded-full bg-sky-950/80">
                          <div className="h-full rounded-full bg-gradient-to-r from-sky-400 to-blue-600" style={{ width: `${candidate.score}%` }} />
                        </div>
                        <span className="text-sm font-semibold text-white">{candidate.score.toFixed(1)}</span>
                      </div>
                    </td>
                    <td className="whitespace-nowrap px-5 py-5">
                      <span className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold ${recTone[candidate.recommendation]}`}>
                        <BadgeCheck className="h-3.5 w-3.5" />
                        {candidate.recommendation}
                      </span>
                    </td>
                    <td className="px-5 py-5 align-top">
                      <div className="flex flex-wrap gap-2">
                        {candidate.matchedSkills.map((skill) => (
                          <span key={skill} className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-1 text-xs text-emerald-300">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-5 py-5 align-top">
                      <div className="flex flex-wrap gap-2">
                        {candidate.missingSkills.map((skill) => (
                          <span key={skill} className="rounded-full border border-rose-500/20 bg-rose-500/10 px-2.5 py-1 text-xs text-rose-300">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}