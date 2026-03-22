"use client";

import { Loader2, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const ANALYSIS_MODELS = [
  { value: "auto", label: "Auto (가성비 추천)" },
  { value: "google/gemini-3-flash-preview", label: "Gemini 3 Flash" },
  { value: "moonshotai/kimi-k2.5", label: "Kimi K2.5" },
  { value: "z-ai/glm-5-turbo", label: "GLM 5 Turbo" },
];

const MIN_INPUT_LENGTH = 10;
const MAX_INPUT_LENGTH = 2000;

interface AdvisorFormProps {
  userInput: string;
  onUserInputChange: (value: string) => void;
  selectedModel: string;
  onSelectedModelChange: (value: string) => void;
  onSubmit: () => void;
  isStreaming: boolean;
  hasApiKey: boolean;
}

export function AdvisorForm({
  userInput,
  onUserInputChange,
  selectedModel,
  onSelectedModelChange,
  onSubmit,
  isStreaming,
  hasApiKey,
}: AdvisorFormProps) {
  const canSubmit =
    hasApiKey &&
    userInput.trim().length >= MIN_INPUT_LENGTH &&
    !isStreaming;

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!canSubmit) return;
    onSubmit();
  }

  function getButtonTooltip(): string | undefined {
    if (!hasApiKey) return "Enter your API key first";
    if (userInput.trim().length < MIN_INPUT_LENGTH)
      return "Please describe your use case in more detail";
    return undefined;
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="mx-auto max-w-3xl px-4 py-8 md:py-12"
    >
      <h2 className="text-2xl font-semibold text-center md:text-3xl">
        What will you use an LLM for?
      </h2>
      <p className="mt-2 text-center text-sm text-muted-foreground">
        The more specific you are, the better recommendations you will get.
      </p>

      <label htmlFor="use-case-input" className="sr-only">
        Describe your use case
      </label>
      <Textarea
        id="use-case-input"
        placeholder='e.g., "I want to build a Korean customer support chatbot. It needs to handle about 1 million requests per month and fast responses are important."'
        value={userInput}
        onChange={(e) => onUserInputChange(e.target.value)}
        disabled={isStreaming}
        maxLength={MAX_INPUT_LENGTH}
        className="mt-6 min-h-32 resize-y text-base"
      />

      <div className="mt-4 flex flex-col items-stretch gap-3 sm:flex-row sm:items-center">
        <Select value={selectedModel} onValueChange={(v) => { if (v) onSelectedModelChange(v); }}>
          <SelectTrigger
            className="w-full sm:w-48 min-h-[44px]"
            aria-label="Select analysis model"
          >
            <SelectValue placeholder="Analysis model" />
          </SelectTrigger>
          <SelectContent>
            {ANALYSIS_MODELS.map((model) => (
              <SelectItem key={model.value} value={model.value}>
                {model.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Button
          type="submit"
          disabled={!canSubmit}
          className="w-full sm:w-auto min-h-[44px]"
          title={getButtonTooltip()}
        >
          {isStreaming ? (
            <>
              <Loader2 className="size-4 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              Start Analysis
              <ArrowRight className="size-4" />
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
