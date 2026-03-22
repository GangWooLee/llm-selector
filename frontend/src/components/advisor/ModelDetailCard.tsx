"use client";

import { CirclePlus, CircleMinus } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import type { ModelRecommendation } from "@/types/model";

interface ModelDetailCardProps {
  recommendation: ModelRecommendation;
}

export function ModelDetailCard({ recommendation }: ModelDetailCardProps) {
  const { monthly_cost_estimate } = recommendation;

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-5 space-y-4">
        <div>
          <h4 className="text-lg font-semibold">{recommendation.model_name}</h4>
          <p className="text-sm text-muted-foreground">
            {recommendation.provider}
          </p>
        </div>

        {recommendation.strengths.length > 0 && (
          <div className="space-y-1.5">
            <h5 className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
              Strengths
            </h5>
            <ul className="space-y-1">
              {recommendation.strengths.map((s, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <CirclePlus className="size-4 shrink-0 mt-0.5 text-green-600 dark:text-green-400" />
                  <span>{s}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {recommendation.weaknesses.length > 0 && (
          <div className="space-y-1.5">
            <h5 className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
              Weaknesses
            </h5>
            <ul className="space-y-1">
              {recommendation.weaknesses.map((w, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <CircleMinus className="size-4 shrink-0 mt-0.5 text-destructive" />
                  <span>{w}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="space-y-1.5">
          <h5 className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
            Monthly Cost Estimate
          </h5>
          <div className="grid grid-cols-3 gap-2">
            <div className="rounded-md bg-muted p-2 text-center">
              <div className="text-xs text-muted-foreground">Low</div>
              <div className="font-mono font-semibold text-sm">
                ${Math.round(monthly_cost_estimate.low)}
              </div>
            </div>
            <div className="rounded-md bg-muted p-2 text-center">
              <div className="text-xs text-muted-foreground">Medium</div>
              <div className="font-mono font-semibold text-sm">
                ${Math.round(monthly_cost_estimate.medium)}
              </div>
            </div>
            <div className="rounded-md bg-muted p-2 text-center">
              <div className="text-xs text-muted-foreground">High</div>
              <div className="font-mono font-semibold text-sm">
                ${Math.round(monthly_cost_estimate.high)}
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
