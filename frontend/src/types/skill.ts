export interface Skill {
  skillId: string;
  skillName: string;
  studentCount: number;
  jobCount: number;
}

export interface SkillDemand {
  skillId: string;
  skillName: string;
  demandCount: number;
  supplyCount: number;
  demandRatio: number;
}
