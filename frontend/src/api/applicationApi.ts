import { apiClient } from './client';
import { Application } from '../types/application';
import { PredictionRequest, PredictionResponse } from '../types/prediction';
import { PageResponse, PaginationParams } from '../types/common';

export interface ApplicationQueryParams extends PaginationParams {
  cycle?: number;
  finalStatus?: number;
}

export const applicationApi = {
  getApplications: async (params?: ApplicationQueryParams): Promise<PageResponse<Application>> => {
    const response = await apiClient.get<PageResponse<Application>>('/applications', {
      params,
    });
    return response.data;
  },

  getApplicationById: async (applicationId: string): Promise<Application> => {
    const response = await apiClient.get<Application>(`/applications/${applicationId}`);
    return response.data;
  },

  predictApplication: async (
    applicationId: string,
    request?: PredictionRequest
  ): Promise<PredictionResponse> => {
    const response = await apiClient.post<PredictionResponse>(
      `/applications/${applicationId}/predict`,
      request || {}
    );
    return response.data;
  },
};
