import { Copy, MessageCircle } from 'lucide-react';

interface WhatsappMessageProps {
  message: string;
}

export function WhatsappMessage({ message }: WhatsappMessageProps) {
  return (
    <section className="rounded-2xl border border-sky-500/20 bg-[#050816]/90 p-6 shadow-soft">
      <div className="flex items-center gap-3">
        <div className="grid h-11 w-11 place-items-center rounded-2xl bg-emerald-500/15 text-emerald-300">
          <MessageCircle className="h-5 w-5" />
        </div>
        <div>
          <p className="text-lg font-semibold text-white">WhatsApp Message</p>
          <p className="text-sm text-sky-200/70">Styled recruiter message with quick-copy intent.</p>
        </div>
      </div>

      <div className="mt-5 rounded-2xl border border-sky-500/20 bg-black/80 p-4">
        <p className="whitespace-pre-wrap text-sm leading-7 text-slate-100">{message}</p>
      </div>

      <div className="mt-4 flex flex-wrap gap-3">
        <button className="inline-flex items-center gap-2 rounded-xl bg-sky-500/15 px-4 py-2 text-sm font-medium text-sky-100 transition hover:bg-sky-500/20">
          <Copy className="h-4 w-4" />
          Copy
        </button>
        <button className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 px-4 py-2 text-sm font-medium text-emerald-300 transition hover:bg-emerald-500/15">
          Open in WhatsApp
        </button>
      </div>
    </section>
  );
}