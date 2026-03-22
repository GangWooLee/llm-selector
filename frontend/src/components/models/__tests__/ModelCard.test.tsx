import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ModelCard } from "@/components/models/ModelCard";
import type { ModelSummary } from "@/types/model";

function createModel(overrides: Partial<ModelSummary> = {}): ModelSummary {
  return {
    id: "test-model-1",
    openrouter_id: "provider/test-model-1",
    name: "Test Model",
    provider: "TestProvider",
    context_length: 128000,
    pricing_input: 3.0,
    pricing_output: 15.0,
    is_free: false,
    modalities: ["text"],
    supported_parameters: [],
    ...overrides,
  };
}

describe("ModelCard", () => {
  it("renders the model name and provider", () => {
    render(<ModelCard model={createModel()} />);

    expect(screen.getByText("Test Model")).toBeInTheDocument();
    expect(screen.getByText("TestProvider")).toBeInTheDocument();
  });

  it("displays input and output pricing", () => {
    render(
      <ModelCard model={createModel({ pricing_input: 3.0, pricing_output: 15.0 })} />,
    );

    expect(screen.getByText("$3.00 / $15.00")).toBeInTheDocument();
  });

  it("displays FREE badge when is_free is true", () => {
    render(<ModelCard model={createModel({ is_free: true })} />);

    expect(screen.getByText("FREE")).toBeInTheDocument();
  });

  it("does not display FREE badge when is_free is false", () => {
    render(<ModelCard model={createModel({ is_free: false })} />);

    expect(screen.queryByText("FREE")).not.toBeInTheDocument();
  });

  it("displays context length formatted as K or M", () => {
    render(<ModelCard model={createModel({ context_length: 128000 })} />);

    expect(screen.getByText(/128K tokens/)).toBeInTheDocument();
  });

  it("displays context length in M for million-level tokens", () => {
    render(<ModelCard model={createModel({ context_length: 1_000_000 })} />);

    expect(screen.getByText(/1\.0M tokens/)).toBeInTheDocument();
  });

  it("renders a link to the model detail page", () => {
    render(<ModelCard model={createModel({ id: "my-model-42" })} />);

    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "/models/my-model-42");
  });

  it("renders capability badges for known parameters", () => {
    render(
      <ModelCard
        model={createModel({
          supported_parameters: ["vision", "tools", "json_mode", "streaming"],
        })}
      />,
    );

    expect(screen.getByText("Vision")).toBeInTheDocument();
    expect(screen.getByText("Tools")).toBeInTheDocument();
    expect(screen.getByText("JSON Mode")).toBeInTheDocument();
    expect(screen.getByText("Streaming")).toBeInTheDocument();
  });

  it("does not render badges for unknown parameters", () => {
    render(
      <ModelCard
        model={createModel({ supported_parameters: ["unknown_param"] })}
      />,
    );

    expect(screen.queryByText("unknown_param")).not.toBeInTheDocument();
  });

  it("formats very small prices with four decimal places", () => {
    render(
      <ModelCard
        model={createModel({ pricing_input: 0.005, pricing_output: 0.008 })}
      />,
    );

    expect(screen.getByText("$0.0050 / $0.0080")).toBeInTheDocument();
  });
});
