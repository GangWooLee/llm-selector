"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Slider } from "@/components/ui/slider";

const PROVIDERS = [
  "OpenAI",
  "Anthropic",
  "Google",
  "Meta",
  "Mistral",
  "Cohere",
] as const;

const INITIAL_VISIBLE_PROVIDERS = 5;

const PRICE_RANGES = [
  { value: "free", label: "Free" },
  { value: "low", label: "Low (< $1/M)" },
  { value: "medium", label: "Medium ($1-10/M)" },
  { value: "high", label: "High (> $10/M)" },
] as const;

const CAPABILITIES = [
  { value: "vision", label: "Vision" },
  { value: "tools", label: "Function Calling" },
  { value: "json_mode", label: "JSON Mode" },
  { value: "streaming", label: "Streaming" },
] as const;

const CONTEXT_MIN = 4000;
const CONTEXT_MAX = 200000;
const CONTEXT_STEP = 4000;

export interface FilterState {
  providers: string[];
  priceRanges: string[];
  contextMin: number;
  capabilities: string[];
  modelType: "all" | "free" | "paid";
}

export const DEFAULT_FILTERS: FilterState = {
  providers: [],
  priceRanges: [],
  contextMin: CONTEXT_MIN,
  capabilities: [],
  modelType: "all",
};

interface ModelFiltersProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
}

export function ModelFilters({ filters, onFiltersChange }: ModelFiltersProps) {
  const [showAllProviders, setShowAllProviders] = useState(false);

  const visibleProviders = showAllProviders
    ? PROVIDERS
    : PROVIDERS.slice(0, INITIAL_VISIBLE_PROVIDERS);

  function toggleArrayItem(array: string[], item: string): string[] {
    return array.includes(item)
      ? array.filter((v) => v !== item)
      : [...array, item];
  }

  function handleReset() {
    onFiltersChange(DEFAULT_FILTERS);
    setShowAllProviders(false);
  }

  const activeCount =
    filters.providers.length +
    filters.priceRanges.length +
    filters.capabilities.length +
    (filters.contextMin > CONTEXT_MIN ? 1 : 0) +
    (filters.modelType !== "all" ? 1 : 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-medium">Filters</h2>
        {activeCount > 0 && (
          <Button
            variant="ghost"
            size="xs"
            onClick={handleReset}
            className="min-h-[44px]"
          >
            Reset
          </Button>
        )}
      </div>

      {/* Provider */}
      <div>
        <p className="text-sm font-medium text-muted-foreground uppercase tracking-wide mb-3">
          Provider
        </p>
        <div className="space-y-2">
          {visibleProviders.map((provider) => (
            <label
              key={provider}
              className="flex items-center gap-2 text-sm cursor-pointer"
            >
              <Checkbox
                checked={filters.providers.includes(provider)}
                onCheckedChange={() =>
                  onFiltersChange({
                    ...filters,
                    providers: toggleArrayItem(filters.providers, provider),
                  })
                }
              />
              {provider}
            </label>
          ))}
          {PROVIDERS.length > INITIAL_VISIBLE_PROVIDERS && (
            <Button
              variant="link"
              size="xs"
              onClick={() => setShowAllProviders(!showAllProviders)}
              className="px-0 min-h-[44px]"
            >
              {showAllProviders ? "Show less" : `Show all (${PROVIDERS.length})`}
            </Button>
          )}
        </div>
      </div>

      {/* Price Range */}
      <div>
        <p className="text-sm font-medium text-muted-foreground uppercase tracking-wide mb-3">
          Price Range
        </p>
        <div className="space-y-2">
          {PRICE_RANGES.map((range) => (
            <label
              key={range.value}
              className="flex items-center gap-2 text-sm cursor-pointer"
            >
              <Checkbox
                checked={filters.priceRanges.includes(range.value)}
                onCheckedChange={() =>
                  onFiltersChange({
                    ...filters,
                    priceRanges: toggleArrayItem(
                      filters.priceRanges,
                      range.value
                    ),
                  })
                }
              />
              {range.label}
            </label>
          ))}
        </div>
      </div>

      {/* Context Length */}
      <div>
        <p className="text-sm font-medium text-muted-foreground uppercase tracking-wide mb-3">
          Min Context Length
        </p>
        <Slider
          min={CONTEXT_MIN}
          max={CONTEXT_MAX}
          step={CONTEXT_STEP}
          value={[filters.contextMin]}
          onValueChange={(val) => {
            const values = Array.isArray(val) ? val : [val];
            onFiltersChange({ ...filters, contextMin: values[0] });
          }}
        />
        <p className="text-xs text-muted-foreground mt-2">
          {filters.contextMin >= 1000
            ? `${Math.round(filters.contextMin / 1000)}K`
            : filters.contextMin}{" "}
          tokens
        </p>
      </div>

      {/* Capabilities */}
      <div>
        <p className="text-sm font-medium text-muted-foreground uppercase tracking-wide mb-3">
          Capabilities
        </p>
        <div className="space-y-2">
          {CAPABILITIES.map((cap) => (
            <label
              key={cap.value}
              className="flex items-center gap-2 text-sm cursor-pointer"
            >
              <Checkbox
                checked={filters.capabilities.includes(cap.value)}
                onCheckedChange={() =>
                  onFiltersChange({
                    ...filters,
                    capabilities: toggleArrayItem(
                      filters.capabilities,
                      cap.value
                    ),
                  })
                }
              />
              {cap.label}
            </label>
          ))}
        </div>
      </div>

      {/* Type */}
      <div>
        <p className="text-sm font-medium text-muted-foreground uppercase tracking-wide mb-3">
          Type
        </p>
        <RadioGroup
          value={filters.modelType}
          onValueChange={(val) =>
            onFiltersChange({
              ...filters,
              modelType: val as FilterState["modelType"],
            })
          }
        >
          {(["all", "free", "paid"] as const).map((type) => (
            <label
              key={type}
              className="flex items-center gap-2 text-sm cursor-pointer"
            >
              <RadioGroupItem value={type} />
              {type === "all" ? "All" : type === "free" ? "Free only" : "Paid only"}
            </label>
          ))}
        </RadioGroup>
      </div>
    </div>
  );
}

export function getActiveFilterCount(filters: FilterState): number {
  return (
    filters.providers.length +
    filters.priceRanges.length +
    filters.capabilities.length +
    (filters.contextMin > CONTEXT_MIN ? 1 : 0) +
    (filters.modelType !== "all" ? 1 : 0)
  );
}
