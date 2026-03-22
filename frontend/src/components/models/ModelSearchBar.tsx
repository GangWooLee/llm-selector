"use client";

import { useEffect, useRef, useState } from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const DEBOUNCE_MS = 300;

const SORT_OPTIONS = [
  { value: "name_asc", label: "Name (A-Z)" },
  { value: "price_asc", label: "Price (low to high)" },
  { value: "price_desc", label: "Price (high to low)" },
  { value: "context_desc", label: "Context (longest)" },
] as const;

interface ModelSearchBarProps {
  query: string;
  sort: string;
  onQueryChange: (query: string) => void;
  onSortChange: (sort: string) => void;
}

export function ModelSearchBar({
  query,
  sort,
  onQueryChange,
  onSortChange,
}: ModelSearchBarProps) {
  const [localQuery, setLocalQuery] = useState(query);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    setLocalQuery(query);
  }, [query]);

  function handleInputChange(value: string) {
    setLocalQuery(value);
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      onQueryChange(value);
    }, DEBOUNCE_MS);
  }

  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  return (
    <div className="flex flex-col sm:flex-row gap-3 mb-6">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
        <Input
          placeholder="Search by model name, provider, or description..."
          value={localQuery}
          onChange={(e) => handleInputChange(e.target.value)}
          className="pl-10 w-full h-11"
          aria-label="Search models"
        />
      </div>
      <Select value={sort} onValueChange={(val) => { if (val) onSortChange(val); }}>
        <SelectTrigger className="w-full sm:w-48 h-11" aria-label="Sort models">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {SORT_OPTIONS.map((option) => (
            <SelectItem key={option.value} value={option.value}>
              {option.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
