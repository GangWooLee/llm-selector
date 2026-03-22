"use client";

import { useCallback, useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { fetchModels } from "@/lib/api";
import type { ModelSummary } from "@/types/model";
import type { Pagination as PaginationType } from "@/types/api";
import { ModelSearchBar } from "@/components/models/ModelSearchBar";
import { ModelFilters, DEFAULT_FILTERS, type FilterState } from "@/components/models/ModelFilters";
import { ModelFilterSheet } from "@/components/models/ModelFilterSheet";
import { ModelGrid } from "@/components/models/ModelGrid";
import { ModelPagination } from "@/components/models/ModelPagination";

const PER_PAGE = 24;

function parseFiltersFromParams(params: URLSearchParams): FilterState {
  const providers = params.get("provider")?.split(",").filter(Boolean) ?? [];
  const priceRanges = params.get("price")?.split(",").filter(Boolean) ?? [];
  const capabilities = params.get("cap")?.split(",").filter(Boolean) ?? [];
  const contextMin = parseInt(params.get("ctx_min") ?? "4000", 10);
  const typeParam = params.get("type");
  const modelType: FilterState["modelType"] =
    typeParam === "free" || typeParam === "paid" ? typeParam : "all";

  return { providers, priceRanges, contextMin, capabilities, modelType };
}

function filtersToApiParams(
  filters: FilterState,
  query: string,
  sort: string,
  page: number
): Record<string, string | number | boolean | undefined> {
  const params: Record<string, string | number | boolean | undefined> = {
    page,
    per_page: PER_PAGE,
  };

  if (query) params.search = query;
  if (sort) params.sort_by = sort;
  if (filters.providers.length === 1) params.provider = filters.providers[0];
  if (filters.contextMin > 4000) params.min_context = filters.contextMin;

  if (filters.modelType === "free") params.is_free = true;
  if (filters.modelType === "paid") params.is_free = false;

  if (filters.capabilities.includes("vision")) params.has_vision = true;
  if (filters.capabilities.includes("tools")) params.has_tools = true;

  return params;
}

export function ModelsPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const query = searchParams.get("q") ?? "";
  const sort = searchParams.get("sort") ?? "name_asc";
  const page = parseInt(searchParams.get("page") ?? "1", 10);
  const filters = parseFiltersFromParams(searchParams);

  const [models, setModels] = useState<ModelSummary[]>([]);
  const [pagination, setPagination] = useState<PaginationType | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const providerKey = filters.providers.join(",");
  const priceKey = filters.priceRanges.join(",");
  const capKey = filters.capabilities.join(",");

  const updateParams = useCallback(
    (updates: Record<string, string | undefined>) => {
      const params = new URLSearchParams(searchParams.toString());
      for (const [key, value] of Object.entries(updates)) {
        if (value) {
          params.set(key, value);
        } else {
          params.delete(key);
        }
      }
      router.push(`/models?${params.toString()}`);
    },
    [searchParams, router]
  );

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setIsLoading(true);
      try {
        const apiParams = filtersToApiParams(filters, query, sort, page);
        const result = await fetchModels(apiParams);
        if (!cancelled) {
          setModels(result.data);
          setPagination(result.pagination);
        }
      } catch {
        if (!cancelled) {
          setModels([]);
          setPagination(null);
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps -- filter keys are stable string representations
  }, [query, sort, page, providerKey, priceKey, filters.contextMin, capKey, filters.modelType]);

  function handleQueryChange(newQuery: string) {
    updateParams({ q: newQuery || undefined, page: undefined });
  }

  function handleSortChange(newSort: string) {
    updateParams({ sort: newSort, page: undefined });
  }

  function handlePageChange(newPage: number) {
    updateParams({ page: String(newPage) });
  }

  function handleFiltersChange(newFilters: FilterState) {
    updateParams({
      provider: newFilters.providers.length > 0
        ? newFilters.providers.join(",")
        : undefined,
      price: newFilters.priceRanges.length > 0
        ? newFilters.priceRanges.join(",")
        : undefined,
      ctx_min: newFilters.contextMin > 4000
        ? String(newFilters.contextMin)
        : undefined,
      cap: newFilters.capabilities.length > 0
        ? newFilters.capabilities.join(",")
        : undefined,
      type: newFilters.modelType !== "all" ? newFilters.modelType : undefined,
      page: undefined,
    });
  }

  function handleReset() {
    handleFiltersChange(DEFAULT_FILTERS);
    updateParams({ q: undefined, sort: undefined, page: undefined });
  }

  return (
    <div className="mx-auto max-w-7xl px-4 md:px-6 lg:px-8 py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">Models</h1>
        {pagination && (
          <p className="text-sm text-muted-foreground mt-1">
            {pagination.total} models available
          </p>
        )}
      </div>

      <ModelSearchBar
        query={query}
        sort={sort}
        onQueryChange={handleQueryChange}
        onSortChange={handleSortChange}
      />

      <ModelFilterSheet
        filters={filters}
        onFiltersChange={handleFiltersChange}
      />

      <div className="flex gap-8 mt-6 lg:mt-0">
        <aside className="hidden lg:block w-64 shrink-0 sticky top-20 self-start">
          <ModelFilters
            filters={filters}
            onFiltersChange={handleFiltersChange}
          />
        </aside>

        <div className="flex-1 min-w-0">
          <ModelGrid
            models={models}
            isLoading={isLoading}
            onReset={handleReset}
          />

          {pagination && (
            <ModelPagination
              currentPage={pagination.page}
              totalPages={pagination.total_pages}
              total={pagination.total}
              perPage={pagination.per_page}
              onPageChange={handlePageChange}
            />
          )}
        </div>
      </div>
    </div>
  );
}
