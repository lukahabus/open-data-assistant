import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from "axios";
import {
  API_BASE_URL,
  DEFAULT_CONFIG,
  ApiError,
  handleApiError,
} from "../config/api";
import { ApiErrorResponse } from "../types/api";

// Create Axios instance with default configuration
const http: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: DEFAULT_CONFIG.timeout,
  headers: DEFAULT_CONFIG.headers,
});

// Request interceptor
http.interceptors.request.use(
  (config) => {
    // You can add authentication headers here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
http.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorResponse>) => {
    const apiError: ApiError = {
      status: error.response?.status || 500,
      message: error.response?.data?.message || error.message,
      details: error.response?.data?.details,
    };
    return Promise.reject(apiError);
  }
);

// Generic request method with type safety
async function request<T>(config: AxiosRequestConfig): Promise<T> {
  try {
    const response = await http.request<T>(config);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.data) {
      throw {
        status: error.response.status,
        message: error.response.data.message,
        details: error.response.data.details,
      } as ApiError;
    }
    throw error;
  }
}

// HTTP methods with type safety
export const httpClient = {
  get: <T>(url: string, config?: AxiosRequestConfig) =>
    request<T>({ ...config, method: "GET", url }),

  post: <T>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    request<T>({ ...config, method: "POST", url, data }),

  put: <T>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    request<T>({ ...config, method: "PUT", url, data }),

  patch: <T>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    request<T>({ ...config, method: "PATCH", url, data }),

  delete: <T>(url: string, config?: AxiosRequestConfig) =>
    request<T>({ ...config, method: "DELETE", url }),
};

// Request cancellation
export const createCancelToken = () => {
  const source = axios.CancelToken.source();
  return {
    token: source.token,
    cancel: source.cancel,
  };
};

// Retry configuration
export interface RetryConfig {
  retries: number;
  retryDelay: number;
  retryCondition?: (error: AxiosError) => boolean;
}

// Retry request utility
export async function retryRequest<T>(
  requestFn: () => Promise<T>,
  config: RetryConfig
): Promise<T> {
  const { retries, retryDelay, retryCondition } = config;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      return await requestFn();
    } catch (error) {
      const isAxiosError = axios.isAxiosError(error);
      const shouldRetry =
        attempt < retries &&
        (!retryCondition || (isAxiosError && retryCondition(error)));

      if (!shouldRetry) {
        throw error;
      }

      await new Promise((resolve) => setTimeout(resolve, retryDelay));
    }
  }

  throw new Error("Max retries reached");
}

// Export default instance
export default http;

// Export types
export type { AxiosInstance, AxiosError, AxiosRequestConfig };
