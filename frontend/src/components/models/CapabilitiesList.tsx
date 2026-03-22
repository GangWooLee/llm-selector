import { Badge } from "@/components/ui/badge";

interface CapabilitiesListProps {
  contextLength: number;
  maxCompletionTokens: number | null;
  modalities: string[];
  supportedParameters: string[];
  architecture: Record<string, string> | null;
}

function formatTokens(tokens: number): string {
  if (tokens >= 1_000_000) return `${(tokens / 1_000_000).toFixed(1)}M`;
  return `${Math.round(tokens / 1000)}K`;
}

export function CapabilitiesList({
  contextLength,
  maxCompletionTokens,
  modalities,
  supportedParameters,
  architecture,
}: CapabilitiesListProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-base font-semibold">Capabilities</h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-muted-foreground">Context Length</p>
          <p className="font-medium">{formatTokens(contextLength)} tokens</p>
        </div>
        {maxCompletionTokens && (
          <div>
            <p className="text-muted-foreground">Max Completion</p>
            <p className="font-medium">
              {formatTokens(maxCompletionTokens)} tokens
            </p>
          </div>
        )}
      </div>

      {modalities.length > 0 && (
        <div>
          <p className="text-sm text-muted-foreground mb-2">Modalities</p>
          <div className="flex flex-wrap gap-1.5">
            {modalities.map((modality) => (
              <Badge key={modality} variant="secondary" className="text-xs">
                {modality}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {supportedParameters.length > 0 && (
        <div>
          <p className="text-sm text-muted-foreground mb-2">
            Supported Parameters
          </p>
          <div className="flex flex-wrap gap-1.5">
            {supportedParameters.map((param) => (
              <Badge key={param} variant="outline" className="text-xs">
                {param}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {architecture && Object.keys(architecture).length > 0 && (
        <div>
          <p className="text-sm text-muted-foreground mb-2">Architecture</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
            {Object.entries(architecture).map(([key, value]) => (
              <div key={key}>
                <p className="text-muted-foreground capitalize">
                  {key.replace(/_/g, " ")}
                </p>
                <p className="font-medium">{value}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
