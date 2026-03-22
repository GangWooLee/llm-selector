"use client";

import { Loader2, Info } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { TOOL_ICON_COMPONENTS as TOOL_ICONS, TOOL_DISPLAY_LABELS as TOOL_LABELS } from "@/lib/tool-metadata";

export interface StreamingStep {
  tool: string;
  reasoning: string;
  summary?: string;
  status: "running" | "done";
}

interface StreamingViewProps {
  thinkingMessage: string | null;
  steps: StreamingStep[];
}

export function StreamingView({ thinkingMessage, steps }: StreamingViewProps) {
  return (
    <div className="mx-auto max-w-3xl px-4 py-6">
      <div className="flex items-center gap-2 mb-4">
        <Loader2 className="size-4 animate-spin text-primary" />
        <span className="text-sm font-medium">
          {thinkingMessage ?? "Agent is analyzing..."}
        </span>
      </div>

      <div className="space-y-3" aria-live="polite" aria-atomic="false">
        {steps.map((step, index) => (
          <div
            key={index}
            className="rounded-lg border border-border p-4 space-y-2"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {TOOL_ICONS[step.tool] ?? (
                  <Info className="size-4 text-muted-foreground" />
                )}
                <span className="text-sm font-medium">
                  Step {index + 1}:{" "}
                  {TOOL_LABELS[step.tool] ?? step.tool}
                </span>
              </div>
              {step.status === "done" ? (
                <Badge variant="outline" className="text-green-600 border-green-600 dark:text-green-400 dark:border-green-400">
                  Done
                </Badge>
              ) : (
                <div className="flex items-center gap-1.5">
                  <Loader2 className="size-3 animate-spin" />
                  <Badge variant="outline">Running</Badge>
                </div>
              )}
            </div>
            <p className="text-sm text-muted-foreground">{step.reasoning}</p>
            {step.summary && <p className="text-sm">{step.summary}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
