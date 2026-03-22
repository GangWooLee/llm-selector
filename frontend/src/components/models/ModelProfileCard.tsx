import { Badge } from "@/components/ui/badge";
import type { ModelDetail } from "@/types/model";

interface ModelProfileCardProps {
  model: ModelDetail;
}

export function ModelProfileCard({ model }: ModelProfileCardProps) {
  return (
    <div>
      <p className="text-sm text-muted-foreground">{model.provider}</p>
      <h1 className="text-2xl font-bold tracking-tight mt-1">{model.name}</h1>
      {model.description && (
        <p className="text-sm text-muted-foreground mt-3 leading-relaxed">
          {model.description}
        </p>
      )}
      {model.is_free && (
        <Badge
          variant="secondary"
          className="mt-3 bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300"
        >
          FREE
        </Badge>
      )}
      {model.tags.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-1.5">
          {model.tags.map((tag) => (
            <Badge key={tag.category} variant="outline" className="text-xs">
              {tag.category}
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
}
