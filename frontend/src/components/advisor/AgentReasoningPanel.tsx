"use client";

import { useState } from "react";
import { Info } from "lucide-react";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { TOOL_ICON_COMPONENTS as TOOL_ICONS, TOOL_DISPLAY_LABELS as TOOL_LABELS } from "@/lib/tool-metadata";
import type { AgentStep } from "@/types/model";

interface AgentReasoningPanelProps {
  steps: AgentStep[];
}

export function AgentReasoningPanel({ steps }: AgentReasoningPanelProps) {
  const [open, setOpen] = useState(false);

  if (steps.length === 0) return null;

  return (
    <div className="mx-auto max-w-4xl px-4">
      <div className="flex items-center justify-end gap-2 mb-4">
        <label
          htmlFor="reasoning-toggle"
          className="text-sm text-muted-foreground cursor-pointer"
        >
          Show reasoning
        </label>
        <Switch
          id="reasoning-toggle"
          checked={open}
          onCheckedChange={setOpen}
          aria-label="Toggle agent reasoning panel"
        />
      </div>

      {open && (
        <div className="space-y-3">
          {steps.map((step) => (
            <div
              key={step.step_number}
              className="rounded-lg border border-border p-4 space-y-2"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {TOOL_ICONS[step.action] ?? (
                    <Info className="size-4 text-muted-foreground" />
                  )}
                  <span className="text-sm font-medium">
                    Step {step.step_number}:{" "}
                    {TOOL_LABELS[step.action] ?? step.action}
                  </span>
                </div>
                <Badge variant="outline">Done</Badge>
              </div>
              <p className="text-sm text-muted-foreground">{step.reasoning}</p>
              <p className="text-sm">{step.result_summary}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
