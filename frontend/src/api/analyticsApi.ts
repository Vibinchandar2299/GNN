import { apiClient } from './client';
import { HiringTrend } from '../types/analytics';

export const analyticsApi = {
  getTrends: async (): Promise<HiringTrend[]> => {
    const response = await apiClient.get<HiringTrend[]>('/analytics/trends');
    return response.data;
  },
};
