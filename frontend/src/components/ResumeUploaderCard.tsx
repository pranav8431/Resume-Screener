import { FileUp, UploadCloud } from 'lucide-react';

interface ResumeUploaderCardProps {
  disabled: boolean;
  files: File[];
  analyzing?: boolean;
  onFilesSelected: (files: File[]) => void;
  onAnalyze: () => void;
}

export function ResumeUploaderCard({ disabled, files, analyzing = false, onFilesSelected, onAnalyze }: ResumeUploaderCardProps) {
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selected = event.target.files ? Array.from(event.target.files) : [];
    onFilesSelected(selected);
  };

  return (
    <section className="rounded-3xl border border-dashed border-sky-400/40 bg-[#050816]/90 p-6 shadow-soft ring-1 ring-sky-400/10 transition hover:border-sky-300/60 hover:bg-[#07111f]">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
        <div className="max-w-xl">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-2xl bg-gradient-to-br from-sky-400 to-blue-600 text-white shadow-glow">
              <UploadCloud className="h-5 w-5" />
            </div>
            <div>
              <p className="text-lg font-semibold text-white">Resume Upload</p>
              <p className="text-sm text-sky-200/70">Drop multiple PDF, DOCX, or TXT resumes here.</p>
            </div>
          </div>
          <p className="mt-4 text-sm leading-6 text-sky-200/70">
            JD confirmation must be completed first. This uploader is styled like a modern drag-and-drop dropzone with clear call-to-action emphasis.
          </p>

          {files.length > 0 ? (
            <div className="mt-4 rounded-xl border border-sky-500/20 bg-black/70 p-3">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-sky-300/70">{files.length} file(s) selected</p>
              <ul className="mt-2 max-h-28 space-y-1 overflow-auto pr-1 text-sm text-slate-200">
                {files.map((file) => (
                  <li key={file.name} className="truncate">{file.name}</li>
                ))}
              </ul>
            </div>
          ) : (
            <p className="mt-4 text-sm text-sky-200/55">No resumes selected yet.</p>
          )}
        </div>

        <div className="flex flex-col gap-3">
          <label
            className={`group inline-flex items-center justify-center gap-3 rounded-xl px-5 py-3 text-sm font-semibold text-white shadow-glow transition ${
              disabled
                ? 'cursor-not-allowed bg-slate-800 text-slate-400 shadow-none'
                : 'cursor-pointer bg-gradient-to-r from-sky-500 to-blue-600 hover:scale-[1.01] hover:from-sky-400 hover:to-blue-500'
            }`}
          >
          <FileUp className="h-4 w-4" />
          <span>Upload Resumes</span>
          <input type="file" multiple accept=".pdf,.docx,.txt" className="hidden" onChange={handleFileChange} disabled={disabled} />
          </label>

          <button
            className={`rounded-xl px-5 py-3 text-sm font-semibold transition ${
              disabled || files.length === 0 || analyzing
                ? 'cursor-not-allowed border border-sky-500/15 bg-black/70 text-slate-500'
                : 'border border-sky-400/30 bg-sky-500/15 text-sky-200 hover:bg-sky-500/20'
            }`}
            onClick={onAnalyze}
            disabled={disabled || files.length === 0 || analyzing}
          >
            {analyzing ? 'Analyzing...' : 'Analyze All Resumes'}
          </button>
        </div>
      </div>
    </section>
  );
}