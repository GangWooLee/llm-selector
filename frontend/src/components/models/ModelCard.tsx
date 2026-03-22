import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import type { ModelSummary } from "@/types/model";

function formatPrice(price: number): string {
  if (price === 0) return "Free";
  if (price < 0.01) return `$${price.toFixed(4)}`;
  return `$${price.toFixed(2)}`;
}

function formatContextLength(tokens: number): string {
  if (tokens >= 1_000_000) return `${(tokens / 1_000_000).toFixed(1)}M`;
  return `${Math.round(tokens / 1000)}K`;
}

const CAPABILITY_LABELS: Record<string, string> = {
  vision: "Vision",
  tools: "Tools",
  json_mode: "JSON Mode",
  streaming: "Streaming",
};

interface ModelCardProps {
  model: ModelSummary;
}

export function ModelCard({ model }: ModelCardProps) {
  return (
    <Link
      href={`/models/${model.id}`}
      className="block rounded-xl border border-border p-5 ring-1 ring-foreground/10 hover:shadow-md hover:border-primary/30 transition-all duration-200 cursor-pointer focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 outline-none"
    >
      <p className="text-sm text-muted-foreground">{model.provider}</p>
      <h3 className="text-lg font-semibold truncate mt-0.5">{model.name}</h3>

      <div className="mt-3">
        <p className="text-xs text-muted-foreground">Price per 1M tokens</p>
        {model.is_free ? (
          <Badge
            variant="secondary"
            className="mt-1 bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300"
          >
            FREE
          </Badge>
        ) : (
          <p className="text-sm font-mono mt-0.5">
            {formatPrice(model.pricing_input)} / {formatPrice(model.pricing_output)}
          </p>
        )}
      </div>

      <p className="mt-2 text-sm text-muted-foreground">
        Context: {formatContextLength(model.context_length)} tokens
      </p>

      {model.supported_parameters.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {model.supported_parameters
            .filter((param) => param in CAPABILITY_LABELS)
            .slice(0, 4)
            .map((param) => (
              <Badge key={param} variant="outline" className="text-xs">
                {CAPABILITY_LABELS[param]}
              </Badge>
            ))}
        </div>
      )}
    </Link>
  );
}
