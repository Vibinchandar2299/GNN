import { apiClient } from './client';

export interface IngestionResult {
  message: string;
  applicationsCount: number;
  studentsCount: number;
  companiesCount: number;
  jobsCount: number;
  skillsCount: number;
  studentSkillsCount: number;
  jobSkillsCount: number;
  success: boolean;
}

export const adminApi = {
  triggerIngestion: async (forceReload: boolean = false): Promise<IngestionResult> => {
    const response = await apiClient.post<IngestionResult>('/admin/ingest', null, {
      params: { forceReload },
    });
    return response.data;
  },
};
