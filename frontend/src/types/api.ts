export interface Pagination {
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: Pagination;
}

export interface ApiKeyValidation {
  valid: boolean;
  credits_remaining?: number;
  usage?: {
    daily: number;
    weekly: number;
    monthly: number;
  };
  error?: string;
}

export interface SyncResult {
  status: string;
  models_added: number;
  models_updated: number;
  models_deactivated: number;
  total_active: number;
  synced_at: string;
}
