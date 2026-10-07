import { PredictionResponse } from './prediction';

export interface Application {
  applicationId: string;
  studentId: string;
  companyId: string;
  jobId: string;
  cycle: number;
  relevantExperienceMonths: number;
  totalSkillCount: number;
  averageSkillProficiency: number;
  roleShiftScore: number;
  skillMatchRatio: number;
  requiredSkillLevelGap: number;
  roleExperienceMatch: number;
  expectedHiringCount: number;
  finalStatus: number;
  finalStatusLabel: string;
  latestPrediction?: PredictionResponse | null;
}

export interface ApplicationFilters {
  cycle?: number;
  finalStatus?: number;
}
