import { apiClient } from './client';
import { Skill, SkillDemand } from '../types/skill';

export const skillApi = {
  getAllSkills: async (): Promise<Skill[]> => {
    const response = await apiClient.get<Skill[]>('/skills');
    return response.data;
  },

  getSkillDemand: async (): Promise<SkillDemand[]> => {
    const response = await apiClient.get<SkillDemand[]>('/skills/demand');
    return response.data;
  },
};
