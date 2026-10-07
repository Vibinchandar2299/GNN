import { apiClient } from './client';
import { Candidate } from '../types/candidate';
import { PageResponse, PaginationParams } from '../types/common';

export interface CandidateQueryParams extends PaginationParams {
  department?: string;
}

export const candidateApi = {
  getCandidates: async (params?: CandidateQueryParams): Promise<PageResponse<Candidate>> => {
    const response = await apiClient.get<PageResponse<Candidate>>('/candidates', {
      params,
    });
    return response.data;
  },

  getCandidateById: async (studentId: string): Promise<Candidate> => {
    const response = await apiClient.get<Candidate>(`/candidates/${studentId}`);
    return response.data;
  },
};
