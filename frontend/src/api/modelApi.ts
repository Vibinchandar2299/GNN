import { apiClient } from './client';
import { ModelBenchmark, ModelMetadata } from '../types/model';

export const modelApi = {
  getBenchmarks: async (): Promise<ModelBenchmark[]> => {
    const response = await apiClient.get<ModelBenchmark[]>('/model/benchmarks');
    return response.data;
  },

  getMetadata: async (): Promise<ModelMetadata> => {
    const response = await apiClient.get<ModelMetadata>('/model/metadata');
    return response.data;
  },
};
