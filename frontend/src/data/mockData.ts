import type { Candidate, JDData } from '../types';

export const jdData: JDData = {
  jobTitle: { value: 'AI Engineering Intern', confidence: 'HIGH' },
  requiredSkills: {
    value: ['python', 'machine learning', 'nlp', 'langchain', 'llm', 'fastapi', 'flask', 'docker'],
    confidence: 'HIGH'
  },
  experienceMin: { value: 0, confidence: 'HIGH' },
  experienceMax: { value: 1, confidence: 'HIGH' },
  location: { value: null, confidence: 'NONE', optional: true },
  preferredSkills: { value: ['java'], confidence: 'LOW', optional: true },
  education: { value: 'B.Tech / B.E.', confidence: 'HIGH', optional: true },
  noticePeriod: { value: 'No preference', confidence: 'LOW', optional: true }
};

export const candidates: Candidate[] = [
  {
    id: '1',
    rank: 1,
    name: 'Pranav Kumar Dutta',
    score: 80.1,
    recommendation: 'Call First',
    matchedSkills: ['python', 'fastapi', 'flask', 'machine learning', 'llm', 'nlp', 'langchain', 'docker'],
    missingSkills: ['async programming'],
    experienceYears: 0.2,
    noticePeriod: 'Immediate',
    location: 'Nagpur',
    currentCompany: 'Athru Technology',
    currentCTC: '-',
    expectedCTC: '-',
    email: 'pranavkr1503@gmail.com',
    phone: '8684936832',
    explanation:
      'Pranav matched 8 of 8 required skills. Their 0.2 years of experience fits the intern requirement well. Location is not required for this role, so they get full marks there.',
    whatsappMessage:
      'Hi Pranav, I came across your profile and feel you would be a great fit for the AI Engineering Intern role. Your experience with Python, FastAPI, and machine learning stands out. Would you be available for a quick call this week?',
    scoreBreakdown: { skill: 32.5, experience: 25, semantic: 7.6, location: 10, education: 5 },
    education: ['B.Tech in Computer Science and Engineering (AI)'],
    skills: ['python', 'c++', 'javascript', 'typescript', 'sql', 'django', 'fastapi', 'flask', 'nodejs', 'rest api', 'machine learning', 'deep learning', 'llm', 'nlp', 'langchain', 'rag', 'faiss', 'transformers', 'postgresql', 'mongodb', 'mysql', 'aws', 'docker', 'git', 'linux', 'pytorch', 'tensorflow', 'pandas', 'numpy']
  },
  {
    id: '2',
    rank: 2,
    name: 'Aarav Sharma',
    score: 73.4,
    recommendation: 'Backup',
    matchedSkills: ['python', 'machine learning', 'docker', 'fastapi', 'nlp'],
    missingSkills: ['langchain', 'llm', 'flask'],
    experienceYears: 1.1,
    noticePeriod: '30 days',
    location: 'Bangalore',
    currentCompany: 'Nexus Labs',
    currentCTC: '8.5 LPA',
    expectedCTC: '12 LPA',
    email: 'aarav@example.com',
    phone: '9876543210',
    explanation: 'Aarav meets the core stack but has slightly more experience than the stated intern range.',
    whatsappMessage: 'Hi Aarav, we liked your profile for the AI Engineering Intern role. Could we connect this week?',
    scoreBreakdown: { skill: 28, experience: 19, semantic: 8.4, location: 8, education: 5 },
    education: ['B.Tech in Computer Science'],
    skills: ['python', 'fastapi', 'docker', 'machine learning', 'nlp', 'sql', 'aws']
  },
  {
    id: '3',
    rank: 3,
    name: 'Meera Iyer',
    score: 55.2,
    recommendation: 'Not Suitable',
    matchedSkills: ['python', 'flask'],
    missingSkills: ['machine learning', 'nlp', 'langchain', 'llm', 'fastapi', 'docker'],
    experienceYears: 3.2,
    noticePeriod: '60 days',
    location: 'Pune',
    currentCompany: 'SoftServe',
    currentCTC: '15 LPA',
    expectedCTC: '18 LPA',
    email: 'meera@example.com',
    phone: '9123456780',
    explanation: 'Meera has solid backend experience, but the AI/ML stack is not a close match for this role.',
    whatsappMessage: 'Hi Meera, thank you for applying. We are currently prioritizing profiles closer to the AI stack for this opening.',
    scoreBreakdown: { skill: 14, experience: 10, semantic: 9.2, location: 7, education: 5 },
    education: ['MCA'],
    skills: ['python', 'flask', 'django', 'sql', 'rest api']
  }
];

export const stepLabels = ['Upload JD', 'Review', 'Upload Resume', 'Results'] as const;

export const stats = [
  { label: 'Total', value: '3', tone: 'slate' },
  { label: 'Call First', value: '1', tone: 'emerald' },
  { label: 'Backup', value: '1', tone: 'amber' },
  { label: 'Not Suitable', value: '1', tone: 'rose' }
];