import { Suspense } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { ModelsPageContent } from "@/components/models/ModelsPageContent";
import { ModelCardSkeleton } from "@/components/models/ModelCardSkeleton";

function ModelsPageFallback() {
  return (
    <div className="mx-auto max-w-7xl px-4 md:px-6 lg:px-8 py-6">
      <div className="mb-6">
        <Skeleton className="h-8 w-32" />
        <Skeleton className="h-4 w-48 mt-2" />
      </div>
      <Skeleton className="h-11 w-full mb-6" />
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
        {Array.from({ length: 9 }, (_, i) => (
          <ModelCardSkeleton key={i} />
        ))}
      </div>
    </div>
  );
}

export default function ModelsPage() {
  return (
    <Suspense fallback={<ModelsPageFallback />}>
      <ModelsPageContent />
    </Suspense>
  );
}
