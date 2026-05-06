import { AlertCircle, CheckCircle2, Edit3, FileText, Sparkles } from 'lucide-react';
import type { JDData, JdConfidence } from '../types';

interface JDReviewPanelProps {
  jd: JDData;
}

const confidenceClass: Record<JdConfidence, string> = {
  HIGH: 'text-emerald-300 bg-emerald-500/10 border-emerald-500/20',
  LOW: 'text-amber-300 bg-amber-500/10 border-amber-500/20',
  NONE: 'text-rose-300 bg-rose-500/10 border-rose-500/20'
};

const confidenceIcon: Record<JdConfidence, React.ReactNode> = {
  HIGH: <CheckCircle2 className="h-4 w-4" />,
  LOW: <AlertCircle className="h-4 w-4" />,
  NONE: <Edit3 className="h-4 w-4" />
};

function SkillChips({ items }: { items: string[] }) {
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((skill) => (
        <span key={skill} className="rounded-full border border-sky-500/20 bg-sky-500/10 px-3 py-1 text-xs font-medium text-sky-100">
          {skill}
        </span>
      ))}
    </div>
  );
}

function FieldCard({
  label,
  value,
  confidence,
  optional
}: {
  label: string;
  value: string | string[] | number | null;
  confidence: JdConfidence;
  optional?: boolean;
}) {
  const empty = value === null || value === '' || (Array.isArray(value) && value.length === 0);
  const display = Array.isArray(value) ? value : empty ? 'Not found' : value;

  return (
    <div className={`rounded-2xl border p-4 shadow-soft ${confidenceClass[confidence]}`}>
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-white">
          {confidenceIcon[confidence]}
          <span>{label}</span>
        </div>
        {optional ? <span className="rounded-full border border-sky-500/20 px-2 py-0.5 text-[11px] uppercase tracking-[0.18em] text-sky-200/60">Optional</span> : null}
      </div>
      <div className="mt-3">
        {Array.isArray(display) ? (
          <SkillChips items={display} />
        ) : (
          <p className="text-sm leading-6 text-slate-100">{display}</p>
        )}
      </div>
    </div>
  );
}

function EditableField({ label, value, placeholder }: { label: string; value: string; placeholder: string }) {
  return (
    <label className="block">
      <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.22em] text-sky-200/70">{label}</span>
      <input
        defaultValue={value}
        placeholder={placeholder}
        className="w-full rounded-xl border border-sky-500/20 bg-black/70 px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-sky-400/70 focus:ring-2 focus:ring-sky-400/20"
      />
    </label>
  );
}

function EditableChipField({ label, items, placeholder }: { label: string; items: string[]; placeholder: string }) {
  return (
    <label className="block">
      <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.22em] text-sky-200/70">{label}</span>
      <textarea
        defaultValue={items.join(', ')}
        placeholder={placeholder}
        rows={3}
        className="w-full rounded-xl border border-sky-500/20 bg-black/70 px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-sky-400/70 focus:ring-2 focus:ring-sky-400/20"
      />
    </label>
  );
}

export function JDReviewPanel({ jd }: JDReviewPanelProps) {
  return (
    <section className="grid gap-6 xl:grid-cols-[minmax(0,1.05fr)_minmax(0,0.95fr)]">
      <div className="rounded-3xl border border-sky-500/20 bg-[#050816]/90 p-6 shadow-soft ring-1 ring-sky-400/10">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-500 text-white shadow-glow">
            <FileText className="h-5 w-5" />
          </div>
          <div>
            <p className="text-lg font-semibold text-white">JD Review & Confirmation</p>
            <p className="text-sm text-sky-200/70">Validate extracted fields before screening resumes.</p>
          </div>
        </div>

        <div className="mt-6 grid gap-4">
          <FieldCard label="Job Title" value={jd.jobTitle.value} confidence={jd.jobTitle.confidence} />
          <FieldCard label="Required Skills" value={(jd.requiredSkills.value as string[]) || []} confidence={jd.requiredSkills.confidence} />
          <div className="grid gap-4 md:grid-cols-2">
            <FieldCard label="Experience Min" value={String(jd.experienceMin.value ?? 'Not found')} confidence={jd.experienceMin.confidence} />
            <FieldCard label="Experience Max" value={String(jd.experienceMax.value ?? 'Not found')} confidence={jd.experienceMax.confidence} />
          </div>
          <FieldCard label="Location" value={jd.location.value} confidence={jd.location.confidence} optional />
          <FieldCard label="Preferred Skills" value={(jd.preferredSkills.value as string[]) || []} confidence={jd.preferredSkills.confidence} optional />
        </div>
      </div>

      <div className="rounded-3xl border border-sky-500/20 bg-[#050816]/90 p-6 shadow-soft ring-1 ring-sky-400/10">
        <div className="flex items-center gap-2 text-white">
          <Sparkles className="h-4 w-4 text-blue-400" />
          <p className="text-lg font-semibold">Confirm & Correct</p>
        </div>
        <p className="mt-2 text-sm leading-6 text-sky-200/70">Every field is editable. Missing fields must be filled before resume analysis unlocks.</p>

        <div className="mt-6 grid gap-4">
          <EditableField label="Job Title *" value={String(jd.jobTitle.value ?? '')} placeholder="e.g. AI Engineering Intern" />
          <EditableChipField label="Required Skills *" items={(jd.requiredSkills.value as string[]) || []} placeholder="Python, FastAPI, Docker" />
          <div className="grid gap-4 md:grid-cols-2">
            <EditableField label="Min Years *" value={String(jd.experienceMin.value ?? 0)} placeholder="0" />
            <EditableField label="Max Years *" value={String(jd.experienceMax.value ?? 0)} placeholder="1" />
          </div>
          <EditableField label="Location" value={String(jd.location.value ?? '')} placeholder="Not specified / Remote / City" />
          <EditableChipField label="Preferred Skills" items={(jd.preferredSkills.value as string[]) || []} placeholder="Java, AWS, Kubernetes" />
          <EditableField label="Education Requirement" value={String(jd.education?.value ?? 'Not specified')} placeholder="B.Tech / B.E." />
          <EditableField label="Notice Period" value={String(jd.noticePeriod?.value ?? 'No preference')} placeholder="No preference" />
        </div>

        <div className="mt-6 rounded-2xl border border-sky-500/20 bg-black/70 p-4">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-sky-300/70">JD ready for scoring</p>
          <p className="mt-2 text-sm leading-6 text-slate-200">
            Once confirmed, the dashboard unlocks resume upload and preserves this JD as the scoring source of truth.
          </p>
        </div>
      </div>
    </section>
  );
}