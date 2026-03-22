import type { ModelSummary } from "@/types/model";
import { ModelCard } from "@/components/models/ModelCard";
import { ModelCardSkeleton } from "@/components/models/ModelCardSkeleton";
import { EmptyState } from "@/components/models/EmptyState";

const SKELETON_COUNT = 9;

interface ModelGridProps {
  models: ModelSummary[];
  isLoading: boolean;
  onReset: () => void;
}

export function ModelGrid({ models, isLoading, onReset }: ModelGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
        {Array.from({ length: SKELETON_COUNT }, (_, i) => (
          <ModelCardSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (models.length === 0) {
    return <EmptyState onReset={onReset} />;
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
      {models.map((model) => (
        <ModelCard key={model.id} model={model} />
      ))}
    </div>
  );
}
