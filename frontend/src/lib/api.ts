import type { PaginatedResponse, SyncResult } from "@/types/api";
import type { ModelSummary, ModelDetail } from "@/types/model";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface FetchModelsParams {
  page?: number;
  per_page?: number;
  provider?: string;
  min_context?: number;
  max_price_input?: number;
  has_tools?: boolean;
  has_vision?: boolean;
  is_free?: boolean;
  search?: string;
  sort_by?: string;
}

export async function fetchModels(
  params: FetchModelsParams = {},
): Promise<PaginatedResponse<ModelSummary>> {
  const searchParams = new URLSearchParams();

  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null) {
      searchParams.set(key, String(value));
    }
  }

  const response = await fetch(
    `${API_URL}/api/v1/models?${searchParams.toString()}`,
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch models: ${response.status}`);
  }

  return response.json() as Promise<PaginatedResponse<ModelSummary>>;
}

export async function fetchModelDetail(id: string): Promise<ModelDetail> {
  const response = await fetch(`${API_URL}/api/v1/models/${id}`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Model not found");
    }
    throw new Error(`Failed to fetch model: ${response.status}`);
  }

  return response.json() as Promise<ModelDetail>;
}

export async function triggerSync(): Promise<SyncResult> {
  const response = await fetch(`${API_URL}/api/v1/sync`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error(`Sync failed: ${response.status}`);
  }

  return response.json() as Promise<SyncResult>;
}
