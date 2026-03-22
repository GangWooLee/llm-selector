import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ComparisonDashboard } from "@/components/advisor/ComparisonDashboard";
import type { ComparisonReport, ModelRecommendation } from "@/types/model";

function makeRecommendation(
  overrides: Partial<ModelRecommendation> = {},
): ModelRecommendation {
  return {
    model_id: "model-1",
    model_name: "GPT-4o",
    provider: "OpenAI",
    overall_score: 85,
    price_score: 70,
    performance_score: 90,
    fit_score: 88,
    strengths: ["Fast responses", "Great reasoning"],
    weaknesses: ["Higher cost"],
    monthly_cost_estimate: { low: 50, medium: 150, high: 300 },
    best_for: "Complex reasoning tasks",
    ...overrides,
  };
}

function makeReport(
  overrides: Partial<ComparisonReport> = {},
): ComparisonReport {
  const rec = makeRecommendation();
  return {
    top_recommendation: {
      model_id: "model-1",
      model_name: "GPT-4o",
      reason: "Best overall performance for your use case",
    },
    recommendations: [rec],
    summary: "GPT-4o is the best choice for complex reasoning tasks.",
    data_sources: ["OpenRouter API", "Chatbot Arena"],
    agent_reasoning: [
      {
        step_number: 1,
        action: "search_models",
        reasoning: "Finding suitable models",
        result_summary: "Found 5 candidates",
      },
    ],
    ...overrides,
  };
}

describe("ComparisonDashboard", () => {
  describe("TopPickCard", () => {
    it("renders the top pick model name", () => {
      render(<ComparisonDashboard report={makeReport()} />);

      // Model name appears in TopPickCard, table, and detail card
      const elements = screen.getAllByText("GPT-4o");
      expect(elements.length).toBeGreaterThanOrEqual(1);
    });

    it("renders the top pick reason", () => {
      render(<ComparisonDashboard report={makeReport()} />);

      expect(
        screen.getByText("Best overall performance for your use case"),
      ).toBeInTheDocument();
    });

    it("shows Top Pick label", () => {
      render(<ComparisonDashboard report={makeReport()} />);

      expect(screen.getByText("Top Pick")).toBeInTheDocument();
    });

    it("shows the provider name from recommendation", () => {
      render(<ComparisonDashboard report={makeReport()} />);

      // Provider appears in both table and detail card
      const elements = screen.getAllByText("OpenAI");
      expect(elements.length).toBeGreaterThanOrEqual(1);
    });

    it("shows the overall score", () => {
      render(<ComparisonDashboard report={makeReport()} />);

      expect(screen.getByText("85/100")).toBeInTheDocument();
    });
  });

  describe("comparison table", () => {
    it("renders model names in the table", () => {
      const report = makeReport({
        recommendations: [
          makeRecommendation({ model_id: "m1", model_name: "GPT-4o" }),
          makeRecommendation({
            model_id: "m2",
            model_name: "Claude 3.5 Sonnet",
            provider: "Anthropic",
          }),
        ],
      });

      render(<ComparisonDashboard report={report} />);

      // Name appears in both table and detail card
      const elements = screen.getAllByText("Claude 3.5 Sonnet");
      expect(elements.length).toBeGreaterThanOrEqual(1);
    });

    it("renders table column headers", () => {
      render(<ComparisonDashboard report={makeReport()} />);

      expect(screen.getByText("Model")).toBeInTheDocument();
      expect(screen.getByText("Overall")).toBeInTheDocument();
      expect(screen.getByText("Price")).toBeInTheDocument();
      expect(screen.getByText("Performance")).toBeInTheDocument();
      expect(screen.getByText("Fit")).toBeInTheDocument();
      expect(screen.getByText("Monthly Cost")).toBeInTheDocument();
      expect(screen.getByText("Best For")).toBeInTheDocument();
    });

    it("renders best_for text in table", () => {
      render(<ComparisonDashboard report={makeReport()} />);

      expect(
        screen.getByText("Complex reasoning tasks"),
      ).toBeInTheDocument();
    });

    it("renders monthly cost range", () => {
      render(<ComparisonDashboard report={makeReport()} />);

      expect(screen.getByText("$50 - $300")).toBeInTheDocument();
    });
  });

  describe("summary section", () => {
    it("renders the summary text", () => {
      render(<ComparisonDashboard report={makeReport()} />);

      expect(
        screen.getByText(
          "GPT-4o is the best choice for complex reasoning tasks.",
        ),
      ).toBeInTheDocument();
    });

    it("renders data sources", () => {
      render(<ComparisonDashboard report={makeReport()} />);

      expect(screen.getByText("OpenRouter API")).toBeInTheDocument();
      expect(screen.getByText("Chatbot Arena")).toBeInTheDocument();
    });

    it("hides data sources section when empty", () => {
      const report = makeReport({ data_sources: [] });

      render(<ComparisonDashboard report={report} />);

      expect(screen.queryByText("Data Sources")).not.toBeInTheDocument();
    });
  });

  describe("model detail cards", () => {
    it("renders strengths", () => {
      render(<ComparisonDashboard report={makeReport()} />);

      expect(screen.getByText("Fast responses")).toBeInTheDocument();
      expect(screen.getByText("Great reasoning")).toBeInTheDocument();
    });

    it("renders weaknesses", () => {
      render(<ComparisonDashboard report={makeReport()} />);

      expect(screen.getByText("Higher cost")).toBeInTheDocument();
    });

    it("renders monthly cost estimates in detail card", () => {
      render(<ComparisonDashboard report={makeReport()} />);

      expect(screen.getByText("$50")).toBeInTheDocument();
      expect(screen.getByText("$150")).toBeInTheDocument();
      expect(screen.getByText("$300")).toBeInTheDocument();
    });
  });

  describe("multiple recommendations", () => {
    it("renders all recommendation cards", () => {
      const report = makeReport({
        recommendations: [
          makeRecommendation({ model_id: "m1", model_name: "GPT-4o" }),
          makeRecommendation({
            model_id: "m2",
            model_name: "Claude 3.5 Sonnet",
            provider: "Anthropic",
            overall_score: 82,
          }),
          makeRecommendation({
            model_id: "m3",
            model_name: "Gemini Pro",
            provider: "Google",
            overall_score: 78,
          }),
        ],
      });

      render(<ComparisonDashboard report={report} />);

      // Names appear in both table and detail card
      const geminiElements = screen.getAllByText("Gemini Pro");
      expect(geminiElements.length).toBeGreaterThanOrEqual(1);
      const googleElements = screen.getAllByText("Google");
      expect(googleElements.length).toBeGreaterThanOrEqual(1);
    });
  });
});
