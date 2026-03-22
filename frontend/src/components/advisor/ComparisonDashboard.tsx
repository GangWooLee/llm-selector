"use client";

import type { ComparisonReport } from "@/types/model";
import { TopPickCard } from "./TopPickCard";
import { ModelComparisonTable } from "./ModelComparisonTable";
import { ModelDetailCard } from "./ModelDetailCard";
import { AgentReasoningPanel } from "./AgentReasoningPanel";

interface ComparisonDashboardProps {
  report: ComparisonReport;
}

export function ComparisonDashboard({ report }: ComparisonDashboardProps) {
  const topRec = report.recommendations.find(
    (r) => r.model_id === report.top_recommendation.model_id
  );

  return (
    <div className="space-y-8 py-8">
      <AgentReasoningPanel steps={report.agent_reasoning} />

      <TopPickCard
        topPick={report.top_recommendation}
        recommendation={topRec}
      />

      <ModelComparisonTable recommendations={report.recommendations} />

      <div className="mx-auto max-w-7xl px-4">
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
          {report.recommendations.map((rec) => (
            <ModelDetailCard key={rec.model_id} recommendation={rec} />
          ))}
        </div>
      </div>

      <div className="mx-auto max-w-4xl px-4">
        <div className="rounded-lg bg-muted/30 p-6 space-y-4">
          <h3 className="text-lg font-semibold">Summary</h3>
          <p className="text-base leading-relaxed">{report.summary}</p>

          {report.data_sources.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
                Data Sources
              </h4>
              <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                {report.data_sources.map((source, i) => (
                  <li key={i}>{source}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
