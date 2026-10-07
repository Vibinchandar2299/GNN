import { apiClient } from './client';
import { Job } from '../types/job';
import { PageResponse, PaginationParams } from '../types/common';

export interface JobQueryParams extends PaginationParams {
  domain?: string;
}

export const jobApi = {
  getJobs: async (params?: JobQueryParams): Promise<PageResponse<Job>> => {
    const response = await apiClient.get<PageResponse<Job>>('/jobs', {
      params,
    });
    return response.data;
  },

  getJobById: async (jobId: string): Promise<Job> => {
    const response = await apiClient.get<Job>(`/jobs/${jobId}`);
    return response.data;
  },
};
