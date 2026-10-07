import { apiClient } from './client';
import { Company } from '../types/company';
import { PageResponse, PaginationParams } from '../types/common';

export interface CompanyQueryParams extends PaginationParams {
  industry?: string;
}

export const companyApi = {
  getCompanies: async (params?: CompanyQueryParams): Promise<PageResponse<Company>> => {
    const response = await apiClient.get<PageResponse<Company>>('/companies', {
      params,
    });
    return response.data;
  },

  getCompanyById: async (companyId: string): Promise<Company> => {
    const response = await apiClient.get<Company>(`/companies/${companyId}`);
    return response.data;
  },
};
