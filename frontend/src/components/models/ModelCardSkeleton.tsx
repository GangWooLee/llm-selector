import { Skeleton } from "@/components/ui/skeleton";

export function ModelCardSkeleton() {
  return (
    <div className="rounded-xl border border-border p-5 space-y-3 ring-1 ring-foreground/10">
      <Skeleton className="h-5 w-10" />
      <Skeleton className="h-5 w-[60%]" />
      <Skeleton className="h-4 w-[40%]" />
      <Skeleton className="h-4 w-[50%]" />
      <Skeleton className="h-4 w-[35%]" />
      <div className="flex gap-1.5 pt-1">
        <Skeleton className="h-5 w-16 rounded-full" />
        <Skeleton className="h-5 w-16 rounded-full" />
        <Skeleton className="h-5 w-16 rounded-full" />
      </div>
    </div>
  );
}
