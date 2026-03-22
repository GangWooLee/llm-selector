"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { AlertCircle, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { AdvisorForm } from "@/components/advisor/AdvisorForm";
import { StreamingView } from "@/components/advisor/StreamingView";
import type { StreamingStep } from "@/components/advisor/StreamingView";
import { ComparisonDashboard } from "@/components/advisor/ComparisonDashboard";
import { streamAdvisor } from "@/lib/sse-client";
import { API_KEY_STORAGE_KEY } from "@/lib/constants";
import type { ComparisonReport } from "@/types/model";

type PageStatus = "idle" | "streaming" | "complete" | "error";

export default function AdvisorPage() {
  const [status, setStatus] = useState<PageStatus>("idle");
  const [userInput, setUserInput] = useState("");
  const [selectedModel, setSelectedModel] = useState("auto");
  const [thinkingMessage, setThinkingMessage] = useState<string | null>(null);
  const [streamingSteps, setStreamingSteps] = useState<StreamingStep[]>([]);
  const [report, setReport] = useState<ComparisonReport | null>(null);
  const [errorMessage, setErrorMessage] = useState("");
  const abortRef = useRef<AbortController | null>(null);
  const [hasApiKey, setHasApiKey] = useState(false);

  useEffect(() => {
    setHasApiKey(!!sessionStorage.getItem(API_KEY_STORAGE_KEY));
  }, []);

  const handleSubmit = useCallback(async () => {
    const apiKey = sessionStorage.getItem(API_KEY_STORAGE_KEY);
    if (!apiKey || !userInput.trim()) return;

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setStatus("streaming");
    setStreamingSteps([]);
    setReport(null);
    setErrorMessage("");
    setThinkingMessage("Agent is analyzing your requirements...");

    const model = selectedModel === "auto" ? "google/gemini-3-flash-preview" : selectedModel;

    await streamAdvisor(userInput, apiKey, model, {
      onThinking: (msg) => setThinkingMessage(msg),
      onToolCall: (tool, reasoning) => {
        setStreamingSteps((prev) => [...prev, { tool, reasoning, status: "running" }]);
      },
      onToolResult: (tool, summary) => {
        setStreamingSteps((prev) => {
          const updated = [...prev];
          const idx = updated.findLastIndex((s) => s.tool === tool);
          if (idx >= 0) updated[idx] = { ...updated[idx], summary, status: "done" };
          return updated;
        });
      },
      onReport: (r) => setReport(r),
      onDone: () => setStatus("complete"),
      onError: (msg) => { setErrorMessage(msg); setStatus("error"); },
    }, controller.signal);
  }, [userInput, selectedModel]);

  const handleRetry = () => {
    abortRef.current?.abort();
    setStatus("idle");
    setErrorMessage("");
    setStreamingSteps([]);
    setReport(null);
  };

  return (
    <div className="pb-12">
      <AdvisorForm
        userInput={userInput}
        onUserInputChange={setUserInput}
        selectedModel={selectedModel}
        onSelectedModelChange={setSelectedModel}
        onSubmit={handleSubmit}
        isStreaming={status === "streaming"}
        hasApiKey={hasApiKey}
      />

      {status === "streaming" && (
        <StreamingView thinkingMessage={thinkingMessage} steps={streamingSteps} />
      )}

      {status === "complete" && report && (
        <ComparisonDashboard report={report} />
      )}

      {status === "error" && (
        <div className="mx-auto max-w-3xl px-4 py-6">
          <Card className="border-destructive">
            <CardContent className="flex items-start gap-3 p-4">
              <AlertCircle className="size-5 shrink-0 text-destructive mt-0.5" />
              <div className="flex-1 space-y-2">
                <p className="text-sm font-medium">Analysis failed</p>
                <p className="text-sm text-muted-foreground">{errorMessage}</p>
                <Button variant="outline" size="sm" onClick={handleRetry} className="min-h-[44px]">
                  <RotateCcw className="size-4" />
                  Try Again
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
