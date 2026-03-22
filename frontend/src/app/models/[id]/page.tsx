"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { fetchModelDetail } from "@/lib/api";
import type { ModelDetail } from "@/types/model";
import { ModelProfileCard } from "@/components/models/ModelProfileCard";
import { PricingTable } from "@/components/models/PricingTable";
import { BenchmarkTable } from "@/components/models/BenchmarkTable";
import { CapabilitiesList } from "@/components/models/CapabilitiesList";

export default function ModelDetailPage() {
  const params = useParams<{ id: string }>();
  const [model, setModel] = useState<ModelDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!params.id) return;
    let cancelled = false;

    async function load() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await fetchModelDetail(params.id);
        if (!cancelled) setModel(data);
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Failed to load model"
          );
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [params.id]);

  if (isLoading) {
    return (
      <div className="mx-auto max-w-4xl px-4 md:px-6 lg:px-8 py-6 space-y-6">
        <Skeleton className="h-5 w-24" />
        <Skeleton className="h-8 w-[50%]" />
        <Skeleton className="h-4 w-[70%]" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (error || !model) {
    return (
      <div className="mx-auto max-w-4xl px-4 md:px-6 lg:px-8 py-6">
        <Link href="/models">
          <Button variant="ghost" size="sm" className="mb-4 min-h-[44px]">
            <ArrowLeft className="size-4 mr-1" />
            Back to models
          </Button>
        </Link>
        <p className="text-sm text-destructive">
          {error ?? "Model not found"}
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 md:px-6 lg:px-8 py-6">
      <Link href="/models">
        <Button variant="ghost" size="sm" className="mb-4 min-h-[44px]">
          <ArrowLeft className="size-4 mr-1" />
          Back to models
        </Button>
      </Link>

      <div className="space-y-8">
        <ModelProfileCard model={model} />

        <PricingTable
          pricingInput={model.pricing_input}
          pricingOutput={model.pricing_output}
          isFree={model.is_free}
        />

        <BenchmarkTable benchmarks={model.benchmarks} />

        <CapabilitiesList
          contextLength={model.context_length}
          maxCompletionTokens={model.max_completion_tokens}
          modalities={model.modalities}
          supportedParameters={model.supported_parameters}
          architecture={model.architecture}
        />

        <p className="text-xs text-muted-foreground">
          Last updated: {new Date(model.updated_at).toLocaleDateString()}
        </p>
      </div>
    </div>
  );
}
