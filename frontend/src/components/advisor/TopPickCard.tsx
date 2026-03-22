"use client";

import { Crown } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import type { TopPick, ModelRecommendation } from "@/types/model";

interface TopPickCardProps {
  topPick: TopPick;
  recommendation: ModelRecommendation | undefined;
}

function ScoreBar({ score }: { score: number }) {
  return (
    <div className="mt-4 space-y-1">
      <div className="flex items-center justify-between text-sm">
        <span className="text-muted-foreground">Overall Score</span>
        <span className="font-semibold">{score}/100</span>
      </div>
      <div className="h-2 w-full rounded-full bg-muted">
        <div
          className="h-2 rounded-full bg-primary transition-all duration-500"
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
}

export function TopPickCard({ topPick, recommendation }: TopPickCardProps) {
  return (
    <div className="mx-auto max-w-4xl px-4">
      <Card className="border-2 border-primary bg-primary/5 shadow-lg">
        <CardContent className="p-6">
          <div className="flex items-center gap-2 text-sm font-medium uppercase tracking-wide text-primary">
            <Crown className="size-4" />
            <span>Top Pick</span>
          </div>
          <h3 className="mt-3 text-2xl font-semibold">{topPick.model_name}</h3>
          {recommendation && (
            <p className="text-sm text-muted-foreground">
              {recommendation.provider}
            </p>
          )}
          {recommendation && <ScoreBar score={recommendation.overall_score} />}
          <p className="mt-4 text-base leading-relaxed text-foreground">
            {topPick.reason}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
