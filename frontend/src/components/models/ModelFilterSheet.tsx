"use client";

import { useState } from "react";
import { SlidersHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import {
  ModelFilters,
  getActiveFilterCount,
  type FilterState,
} from "@/components/models/ModelFilters";

interface ModelFilterSheetProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
}

export function ModelFilterSheet({
  filters,
  onFiltersChange,
}: ModelFilterSheetProps) {
  const [open, setOpen] = useState(false);
  const activeCount = getActiveFilterCount(filters);

  return (
    <>
      <Button
        variant="outline"
        className="w-full lg:hidden min-h-[44px]"
        onClick={() => setOpen(true)}
        aria-label="Open filters"
      >
        <SlidersHorizontal className="size-4 mr-2" />
        Filters
        {activeCount > 0 && (
          <Badge className="ml-2">{activeCount}</Badge>
        )}
      </Button>

      <Sheet open={open} onOpenChange={setOpen}>
        <SheetContent side="bottom" className="max-h-[80vh] overflow-y-auto p-6">
          <SheetHeader>
            <SheetTitle>Filters</SheetTitle>
            <SheetDescription>
              Filter models by provider, price, and capabilities
            </SheetDescription>
          </SheetHeader>
          <div className="mt-4">
            <ModelFilters filters={filters} onFiltersChange={onFiltersChange} />
          </div>
        </SheetContent>
      </Sheet>
    </>
  );
}
