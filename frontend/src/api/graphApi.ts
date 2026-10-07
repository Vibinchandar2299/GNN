import { apiClient } from './client';
import { GraphOverview, SubgraphResponse } from '../types/graph';

export const graphApi = {
  getOverview: async (): Promise<GraphOverview> => {
    const response = await apiClient.get<GraphOverview>('/graph/overview');
    return response.data;
  },

  getSubgraph: async (type: string, id: string, maxNeighbors: number = 30): Promise<SubgraphResponse> => {
    const response = await apiClient.get<SubgraphResponse>(`/graph/subgraph/${type}/${id}`, {
      params: { maxNeighbors },
    });
    return response.data;
  },
};
