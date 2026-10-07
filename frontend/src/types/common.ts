export interface PageResponse<T> {
  content: T[];
  totalPages: number;
  totalElements: number;
  last: boolean;
  size: number;
  number: number;
  first: boolean;
  empty: boolean;
}

export interface ApiErrorResponse {
  timestamp?: string;
  status: number;
  error: string;
  message: string;
  path?: string;
}

export interface PaginationParams {
  page?: number;
  size?: number;
  sort?: string;
}
