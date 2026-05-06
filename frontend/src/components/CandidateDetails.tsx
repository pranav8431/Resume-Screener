import { Building2, Clock3, Mail, MapPin, Phone, ScrollText, Sparkles } from 'lucide-react';
import type { Candidate } from '../types';

interface CandidateDetailsProps {
  candidate: Candidate;
}

function DetailRow({ icon: Icon, label, value }: { icon: typeof Building2; label: string; value: string }) {
  return (
    <div className="flex items-start gap-3 rounded-2xl border border-sky-500/15 bg-black/70 p-3 shadow-soft">
      <Icon className="mt-0.5 h-4 w-4 text-sky-300" />
      <div>
        <p className="text-[11px] uppercase tracking-[0.22em] text-sky-200/60">{label}</p>
        <p className="mt-1 break-words text-sm text-slate-100">{value}</p>
      </div>
    </div>
  );
}

export function CandidateDetails({ candidate }: CandidateDetailsProps) {
  return (
    <section className="grid gap-6 xl:grid-cols-1">
      <div className="rounded-3xl border border-sky-500/20 bg-[#050816]/90 p-6 shadow-soft ring-1 ring-sky-400/10">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-2xl font-semibold tracking-tight text-white">{candidate.name}</p>
            <p className="mt-1 text-sm text-sky-200/70">Rank #{candidate.rank} · {candidate.recommendation}</p>
          </div>
          <div className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-300">
            {candidate.score.toFixed(1)} / 100
          </div>
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-2">
          <DetailRow icon={Mail} label="Email" value={candidate.email} />
          <DetailRow icon={Phone} label="Phone" value={candidate.phone} />
          <DetailRow icon={MapPin} label="Location" value={candidate.location} />
          <DetailRow icon={Building2} label="Company" value={candidate.currentCompany} />
          <DetailRow icon={Clock3} label="Notice Period" value={candidate.noticePeriod} />
          <DetailRow icon={ScrollText} label="Experience" value={`${candidate.experienceYears} years`} />
        </div>

        <div className="mt-6 rounded-2xl border border-sky-500/20 bg-black/70 p-4">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-sky-300/70">Education</p>
          <ul className="mt-3 space-y-2 text-sm text-slate-100">
            {candidate.education.map((item) => (
              <li key={item} className="rounded-xl border border-sky-500/15 bg-sky-500/5 px-3 py-2">
                {item}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="grid gap-6">
        <div className="rounded-3xl border border-sky-500/20 bg-[#050816]/90 p-6 shadow-soft ring-1 ring-sky-400/10">
          <p className="text-lg font-semibold text-white">Explanation</p>
          <p className="mt-3 text-sm leading-7 text-sky-100/85">{candidate.explanation}</p>
          <div className="mt-5 flex flex-wrap gap-2">
            {candidate.skills.slice(0, 12).map((skill) => (
              <span key={skill} className="rounded-full border border-sky-500/20 bg-sky-500/10 px-3 py-1 text-xs text-sky-100">
                {skill}
              </span>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}