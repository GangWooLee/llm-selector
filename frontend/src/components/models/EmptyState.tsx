import { SearchX } from "lucide-react";
import { Button } from "@/components/ui/button";

interface EmptyStateProps {
  onReset: () => void;
}

export function EmptyState({ onReset }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <SearchX className="size-12 text-muted-foreground/50 mb-4" />
      <h3 className="text-lg font-medium">No results found</h3>
      <p className="text-sm text-muted-foreground mt-1">
        Try adjusting your search or filters
      </p>
      <Button
        variant="outline"
        className="mt-4 min-h-[44px]"
        onClick={onReset}
      >
        Reset filters
      </Button>
    </div>
  );
}
