import axios, { AxiosError } from 'axios';
import { ApiErrorResponse } from '../types/common';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorResponse>) => {
    let friendlyMessage = 'An unexpected error occurred while communicating with the backend.';

    if (!error.response) {
      friendlyMessage = 'Unable to connect to the HireGraph backend. Please ensure the Spring Boot service is running on port 8080.';
    } else if (error.response.data && error.response.data.message) {
      friendlyMessage = error.response.data.message;
    } else if (error.response.status === 404) {
      friendlyMessage = 'The requested resource was not found in the database.';
    } else if (error.response.status === 502) {
      friendlyMessage = 'The Python AI Inference Service (FastAPI) is currently unavailable or returning an error.';
    } else if (error.response.status >= 500) {
      friendlyMessage = 'Internal server error encountered in backend processing.';
    }

    return Promise.reject(new Error(friendlyMessage));
  }
);
