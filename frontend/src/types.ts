export type Recommendation = 'Call First' | 'Backup' | 'Not Suitable';

export type JdConfidence = 'HIGH' | 'LOW' | 'NONE';

export interface JdField {
  value: string | string[] | number | null;
  confidence: JdConfidence;
  optional?: boolean;
}

export interface JDData {
  jobTitle: JdField;
  requiredSkills: JdField;
  experienceMin: JdField;
  experienceMax: JdField;
  location: JdField;
  preferredSkills: JdField;
  education?: JdField;
  noticePeriod?: JdField;
}

export interface Candidate {
  id: string;
  rank: number;
  name: string;
  score: number;
  recommendation: Recommendation;
  matchedSkills: string[];
  missingSkills: string[];
  experienceYears: number;
  noticePeriod: string;
  location: string;
  currentCompany: string;
  currentCTC: string;
  expectedCTC: string;
  email: string;
  phone: string;
  explanation: string;
  whatsappMessage: string;
  scoreBreakdown: {
    skill: number;
    experience: number;
    semantic: number;
    location: number;
    education: number;
  };
  education: string[];
  skills: string[];
  isDuplicate?: boolean;
}