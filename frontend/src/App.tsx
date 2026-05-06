import { CheckCircle2, FileText, Stars } from 'lucide-react';
import { useMemo, useState } from 'react';
import * as pdfjsLib from 'pdfjs-dist';
import pdfWorkerUrl from 'pdfjs-dist/build/pdf.worker.mjs?url';
import { JDReviewPanel } from './components/JDReviewPanel';
import { ResumeUploaderCard } from './components/ResumeUploaderCard';
import { RankingTable } from './components/RankingTable';
import { CandidateDetails } from './components/CandidateDetails';
import { WhatsappMessage } from './components/WhatsappMessage';
import type { JDData } from './types';
import { candidates, jdData, stats, stepLabels } from './data/mockData';

pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorkerUrl;

type MatchResult = {
  matched: string[];
  missing: string[];
};

type ResumeProfile = {
  name: string;
  email: string;
  phone: string;
  location: string;
  currentCompany: string;
  noticePeriod: string;
  experienceYears: number;
  education: string[];
};

const skillAliasMap: Record<string, string[]> = {
  python: ['python', 'py'],
  'machine learning': ['machine learning', 'ml', 'model training', 'supervised learning', 'unsupervised learning'],
  nlp: ['nlp', 'natural language processing', 'spacy', 'nltk'],
  langchain: ['langchain', 'lang chain'],
  llm: ['llm', 'llms', 'large language model', 'generative ai', 'gen ai', 'gpt', 'chatgpt'],
  fastapi: ['fastapi', 'fast api'],
  flask: ['flask'],
  docker: ['docker', 'containerization', 'dockerfile'],
  java: ['java', 'core java']
};

const normalizeText = (text: string) => text.toLowerCase().replace(/[^a-z0-9+\s]/g, ' ');

const firstMeaningfulLine = (text: string) =>
  text
    .split(/\r?\n/)
    .map((line) => line.replace(/\s+/g, ' ').trim())
    .find((line) => line.length > 2 && /[a-zA-Z]/.test(line));

const extractEmail = (text: string) => text.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i)?.[0] ?? 'Not found';

const extractPhone = (text: string) => {
  const match = text.match(/(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3,5}\)?[\s-]?)?\d{3,5}[\s-]?\d{4}/);
  return match?.[0].replace(/\s+/g, ' ').trim() ?? 'Not found';
};

const formatDisplayName = (value: string) =>
  value
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/\b\w/g, (character) => character.toUpperCase());

const extractResumeProfile = (file: File, resumeText: string): ResumeProfile => {
  const nameFromText = firstMeaningfulLine(resumeText);
  const fileName = file.name.replace(/\.[^/.]+$/, '');
  const inferredName = nameFromText && nameFromText.length <= 45 ? nameFromText : fileName;
  const educationLine = resumeText
    .split(/\r?\n/)
    .map((line) => line.trim())
    .find((line) => /b\.?(tech|e|sc|com|ca)|mca|msc|bachelor|master/i.test(line));

  return {
    name: formatDisplayName(inferredName),
    email: extractEmail(resumeText),
    phone: extractPhone(resumeText),
    location: 'Not found',
    currentCompany: 'Not found',
    noticePeriod: 'Not found',
    experienceYears: 0,
    education: educationLine ? [educationLine] : ['Not found']
  };
};

const initialJdText = `Truviq is building a dedicated AI practice from the ground up. As an intern, you'll ship production-ready AI systems.

Technology Focus
- LangChain: RAG pipelines, memory management
- Ollama: Local LLM deployment

Skills Required
- Python, ML, NLP, FastAPI/Flask, Docker
- Good to have: Java

Eligibility
- B.Tech / BE (CSE / IT)
- Minimum 70% aggregate`;

const emptyJdData: JDData = {
  jobTitle: { value: '', confidence: 'NONE' },
  requiredSkills: { value: [], confidence: 'NONE' },
  experienceMin: { value: null, confidence: 'NONE' },
  experienceMax: { value: null, confidence: 'NONE' },
  location: { value: '', confidence: 'NONE', optional: true },
  preferredSkills: { value: [], confidence: 'NONE', optional: true },
  education: { value: '', confidence: 'NONE', optional: true },
  noticePeriod: { value: '', confidence: 'NONE', optional: true }
};

const extractTextFromPdf = async (file: File): Promise<string> => {
  const buffer = await file.arrayBuffer();
  const data = new Uint8Array(buffer);
  const doc = await pdfjsLib.getDocument({ data }).promise;
  const pages: string[] = [];

  for (let pageNum = 1; pageNum <= doc.numPages; pageNum += 1) {
    const page = await doc.getPage(pageNum);
    const content = await page.getTextContent();
    const pageText = content.items
      .map((item) => ('str' in item ? item.str : ''))
      .join(' ');
    pages.push(pageText);
  }

  return pages.join(' ');
};

const extractTextFromFile = async (file: File): Promise<string> => {
  const name = file.name.toLowerCase();
  if (name.endsWith('.txt')) {
    return file.text();
  }
  if (name.endsWith('.pdf')) {
    return extractTextFromPdf(file);
  }
  return '';
};

const computeSkillMatch = (resumeText: string, requiredSkills: string[]): MatchResult => {
  const normalizedResume = normalizeText(resumeText);
  const normalizedRequired = requiredSkills.map((s) => s.toLowerCase());
  const matched = normalizedRequired.filter((skill) => {
    const aliases = skillAliasMap[skill] ?? [skill];
    return aliases.some((alias) => normalizedResume.includes(alias.toLowerCase()));
  });

  return {
    matched,
    missing: normalizedRequired.filter((skill) => !matched.includes(skill))
  };
};

export default function App() {
  const [jdExtracted, setJdExtracted] = useState(false);
  const [jdConfirmed, setJdConfirmed] = useState(false);
  const [jdInput, setJdInput] = useState(initialJdText);
  const [reviewJd, setReviewJd] = useState<JDData>(emptyJdData);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analyzedCandidates, setAnalyzedCandidates] = useState<typeof candidates>([]);
  const [resetKey, setResetKey] = useState(0);

  const activeStep = useMemo(() => {
    if (analysisComplete) return 3;
    if (uploadedFiles.length > 0) return 2;
    if (jdExtracted) return 1;
    return 0;
  }, [analysisComplete, jdExtracted, uploadedFiles.length]);

  const selected = analysisComplete ? analyzedCandidates[0] ?? null : null;
  const visibleCandidates = analysisComplete ? analyzedCandidates : [];
  const jdRequiredSkills = (reviewJd.requiredSkills.value as string[]) ?? [];

  const fileBaseName = (filename: string) => filename.replace(/\.[^/.]+$/, '');

  const handleExtractJD = () => {
    setJdExtracted(true);
    setJdConfirmed(false);
    setUploadedFiles([]);
    setAnalysisComplete(false);
    setReviewJd(jdData);
    setAnalyzedCandidates([]);
  };

  const handleReset = () => {
    setJdExtracted(false);
    setJdConfirmed(false);
    setJdInput('');
    setReviewJd(emptyJdData);
    setUploadedFiles([]);
    setAnalysisComplete(false);
    setIsAnalyzing(false);
    setAnalyzedCandidates([]);
    setResetKey((value) => value + 1);
  };

  const handleConfirmJD = () => {
    setJdConfirmed(true);
  };

  const handleAnalyzeResumes = async () => {
    if (jdConfirmed && uploadedFiles.length > 0) {
      setIsAnalyzing(true);
      try {
        const mapped = await Promise.all(
          uploadedFiles.map(async (file, index) => {
            const resumeText = await extractTextFromFile(file);
            const { matched, missing } = computeSkillMatch(resumeText, jdRequiredSkills);
            const coverage = jdRequiredSkills.length > 0 ? matched.length / jdRequiredSkills.length : 0;
            const score = Math.max(30, Math.min(92, Math.round((coverage * 70 + 20) * 10) / 10));

            const recommendation = score >= 80 ? 'Call First' : score >= 60 ? 'Backup' : 'Not Suitable';
            const profile = extractResumeProfile(file, resumeText);

            const explanation = resumeText
              ? `${file.name}: matched ${matched.length} of ${jdRequiredSkills.length} required skills from uploaded resume content.`
              : `${file.name}: could not extract text from this file type in browser preview mode. Use PDF/TXT or connect backend parsing for full accuracy.`;

            return {
              id: `uploaded-${index}`,
              rank: index + 1,
              name: profile.name,
              score,
              recommendation,
              matchedSkills: matched,
              missingSkills: missing,
              explanation,
              experienceYears: profile.experienceYears,
              noticePeriod: profile.noticePeriod,
              location: profile.location,
              currentCompany: profile.currentCompany,
              currentCTC: 'Not found',
              expectedCTC: 'Not found',
              email: profile.email,
              phone: profile.phone,
              scoreBreakdown: {
                skill: Math.round(coverage * 40 * 10) / 10,
                experience: 0,
                semantic: Math.round(coverage * 20 * 10) / 10,
                location: 0,
                education: 0
              },
              education: profile.education,
              skills: matched.length > 0 ? matched : jdRequiredSkills,
              whatsappMessage:
                `Hi ${profile.name}, I came across your profile and feel you would be a great fit for the AI Engineering Intern role. Would you be available for a quick call this week?`
            };
          })
        );

        const ranked = [...mapped].sort((a, b) => b.score - a.score).map((c, idx) => ({ ...c, rank: idx + 1 }));
        setAnalyzedCandidates(ranked);
        setAnalysisComplete(true);
      } finally {
        setIsAnalyzing(false);
      }
    }
  };

  return (
    <div className="min-h-screen bg-black text-slate-100">
      <div className="flex min-h-screen">
        <main className="min-w-0 flex-1 overflow-hidden">
          <div className="flex w-full flex-col gap-6 px-4 py-5 sm:px-6 lg:px-8">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <h1 className="text-4xl font-bold tracking-tight text-sky-300 drop-shadow-[0_0_18px_rgba(56,189,248,0.18)]">Resume Screener</h1>
              <button
                className="inline-flex items-center gap-2 rounded-xl border border-red-500/40 bg-red-500 px-4 py-2.5 text-sm font-semibold text-white shadow-md transition hover:border-red-400 hover:bg-red-400"
                onClick={handleReset}
              >
                Reset All
              </button>
            </div>

            <section className="grid gap-6 xl:grid-cols-[minmax(0,1.25fr)_minmax(360px,0.75fr)]">
              <div className="space-y-6 min-w-0">
                <section className="grid gap-6 rounded-2xl border border-sky-500/20 bg-[#050816]/95 p-6 shadow-soft">
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <div className="grid h-11 w-11 place-items-center rounded-2xl bg-gradient-to-br from-sky-400 to-blue-600 text-white shadow-glow">
                        <FileText className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="text-lg font-semibold text-white">Job Description</p>
                        <p className="text-sm text-sky-200/70">Paste or upload the JD to extract key hiring criteria.</p>
                      </div>
                    </div>

                    <div className="rounded-2xl border border-sky-500/15 bg-black/70 p-4">
                      <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.22em] text-sky-300/70">JD Input</label>
                      <textarea
                        value={jdInput}
                        onChange={(event) => setJdInput(event.target.value)}
                        className="h-56 w-full rounded-xl border border-sky-500/20 bg-black px-4 py-4 text-sm leading-7 text-white outline-none transition placeholder:text-slate-500 focus:border-sky-400/70 focus:ring-2 focus:ring-sky-400/20"
                        placeholder="Paste a job description here..."
                      />
                    </div>

                    <div className="flex flex-wrap gap-3">
                      <button
                        className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 px-4 py-3 text-sm font-semibold text-white shadow-glow transition hover:from-sky-400 hover:to-blue-500"
                        onClick={handleExtractJD}
                      >
                        <Stars className="h-4 w-4" />
                        Extract JD Details
                      </button>
                      <button className="inline-flex items-center gap-2 rounded-xl border border-sky-500/20 bg-black/70 px-4 py-3 text-sm font-medium text-sky-100 transition hover:border-sky-400/40 hover:bg-sky-500/10">
                        Save Draft
                      </button>
                    </div>
                  </div>
                </section>

                <JDReviewPanel key={`jd-${resetKey}`} jd={reviewJd} />

                <div className="rounded-2xl border border-sky-500/20 bg-[#050816]/85 p-4 shadow-soft ring-1 ring-sky-400/10">
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <p className="text-sm font-semibold text-white">JD Confirmation Gate</p>
                      <p className="mt-1 text-sm text-sky-200/70">
                        Confirm the JD to unlock resume upload and analysis.
                      </p>
                    </div>
                    <button
                      className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition ${
                        jdConfirmed
                          ? 'cursor-default border border-emerald-500/30 bg-emerald-500/15 text-emerald-300'
                            : 'border border-sky-500/30 bg-sky-500/15 text-sky-200 hover:bg-sky-500/20'
                      }`}
                      onClick={handleConfirmJD}
                      disabled={jdConfirmed || !jdExtracted}
                    >
                      <CheckCircle2 className="h-4 w-4" />
                      {jdConfirmed ? 'JD Confirmed' : 'Confirm JD & Unlock Upload'}
                    </button>
                  </div>
                </div>

                <ResumeUploaderCard
                  key={`upload-${resetKey}`}
                  disabled={!jdConfirmed}
                  files={uploadedFiles}
                  analyzing={isAnalyzing}
                  onFilesSelected={(files) => {
                    setUploadedFiles(files);
                    setAnalysisComplete(false);
                    setAnalyzedCandidates(candidates.slice(0, 1));
                  }}
                  onAnalyze={() => {
                    void handleAnalyzeResumes();
                  }}
                />

                {analysisComplete ? (
                  <div className="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-300">
                    {uploadedFiles.length} resume(s) analyzed successfully. Rankings updated.
                  </div>
                ) : (
                  <div className="rounded-2xl border border-sky-500/20 bg-[#050816]/85 p-4 text-sm text-sky-200/70">
                    Upload resumes and click Analyze All Resumes to populate rankings.
                  </div>
                )}

                <RankingTable key={`ranking-${resetKey}`} candidates={visibleCandidates} />
              </div>

              <div className="space-y-6 xl:sticky xl:top-6 xl:self-start">
                {selected ? (
                  <>
                    <CandidateDetails key={`candidate-${resetKey}`} candidate={selected} />
                    <WhatsappMessage key={`whatsapp-${resetKey}`} message={selected.whatsappMessage} />
                  </>
                ) : (
                  <div className="rounded-3xl border border-sky-500/20 bg-[#050816]/90 p-6 shadow-soft ring-1 ring-sky-400/10">
                    <p className="text-lg font-semibold text-white">No suggestions yet</p>
                    <p className="mt-2 text-sm leading-6 text-sky-200/70">
                      Extract the JD, confirm it, and analyze resumes to populate candidate suggestions here.
                    </p>
                  </div>
                )}
              </div>
            </section>
          </div>
        </main>
      </div>
    </div>
  );
}