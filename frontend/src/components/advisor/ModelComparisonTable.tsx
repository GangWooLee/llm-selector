"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { ModelRecommendation } from "@/types/model";

function scoreColor(score: number): string {
  if (score >= 80) return "bg-green-500 dark:bg-green-400";
  if (score >= 60) return "bg-yellow-500 dark:bg-yellow-400";
  return "bg-red-500 dark:bg-red-400";
}

function ScoreCell({ score }: { score: number }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-sm font-semibold">{score}</span>
      <div className="h-1.5 w-16 rounded-full bg-muted">
        <div
          className={`h-1.5 rounded-full transition-all duration-500 ${scoreColor(score)}`}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
}

function formatCostRange(low: number, high: number): string {
  return `$${Math.round(low)} - $${Math.round(high)}`;
}

interface ModelComparisonTableProps {
  recommendations: ModelRecommendation[];
}

export function ModelComparisonTable({
  recommendations,
}: ModelComparisonTableProps) {
  return (
    <div className="mx-auto max-w-5xl px-4">
      <div className="overflow-x-auto rounded-lg border border-border" role="region" aria-label="Model comparison table" tabIndex={0}>
        <Table>
          <TableHeader className="bg-muted/50">
            <TableRow>
              <TableHead className="text-xs font-medium uppercase text-muted-foreground">
                Model
              </TableHead>
              <TableHead className="text-xs font-medium uppercase text-muted-foreground">
                Overall
              </TableHead>
              <TableHead className="text-xs font-medium uppercase text-muted-foreground">
                Price
              </TableHead>
              <TableHead className="text-xs font-medium uppercase text-muted-foreground">
                Performance
              </TableHead>
              <TableHead className="text-xs font-medium uppercase text-muted-foreground">
                Fit
              </TableHead>
              <TableHead className="text-xs font-medium uppercase text-muted-foreground">
                Monthly Cost
              </TableHead>
              <TableHead className="text-xs font-medium uppercase text-muted-foreground">
                Best For
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {recommendations.map((rec) => (
              <TableRow key={rec.model_id}>
                <TableCell className="py-3 px-4">
                  <div>
                    <div className="font-medium">{rec.model_name}</div>
                    <div className="text-xs text-muted-foreground">
                      {rec.provider}
                    </div>
                  </div>
                </TableCell>
                <TableCell className="py-3 px-4">
                  <ScoreCell score={rec.overall_score} />
                </TableCell>
                <TableCell className="py-3 px-4">
                  <ScoreCell score={rec.price_score} />
                </TableCell>
                <TableCell className="py-3 px-4">
                  <ScoreCell score={rec.performance_score} />
                </TableCell>
                <TableCell className="py-3 px-4">
                  <ScoreCell score={rec.fit_score} />
                </TableCell>
                <TableCell className="py-3 px-4 text-sm font-mono">
                  {formatCostRange(
                    rec.monthly_cost_estimate.low,
                    rec.monthly_cost_estimate.high
                  )}
                </TableCell>
                <TableCell className="py-3 px-4 text-sm">
                  {rec.best_for}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
