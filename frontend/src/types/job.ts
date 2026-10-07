export interface Job {
  jobId: string;
  jobTitle: string;
  jobDomain: string;
  minimumCgpa: number;
  experienceRequiredMonths: number;
  salaryLpa: number;
  requiredSkillCount: number;
  requiredSkills: string[];
}
