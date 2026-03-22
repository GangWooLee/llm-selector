import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import {
  ModelFilters,
  DEFAULT_FILTERS,
  type FilterState,
} from "@/components/models/ModelFilters";

function renderFilters(
  overrides: Partial<{ filters: FilterState; onFiltersChange: ReturnType<typeof vi.fn> }> = {},
) {
  const props = {
    filters: { ...DEFAULT_FILTERS },
    onFiltersChange: vi.fn(),
    ...overrides,
  };
  render(<ModelFilters {...props} />);
  return props;
}

describe("ModelFilters", () => {
  it("renders provider checkboxes", () => {
    renderFilters();

    expect(screen.getByText("OpenAI")).toBeInTheDocument();
    expect(screen.getByText("Anthropic")).toBeInTheDocument();
    expect(screen.getByText("Google")).toBeInTheDocument();
    expect(screen.getByText("Meta")).toBeInTheDocument();
    expect(screen.getByText("Mistral")).toBeInTheDocument();
  });

  it("calls onFiltersChange when a provider checkbox is clicked", async () => {
    const user = userEvent.setup();
    const props = renderFilters();

    await user.click(screen.getByText("OpenAI"));

    expect(props.onFiltersChange).toHaveBeenCalledWith(
      expect.objectContaining({ providers: ["OpenAI"] }),
    );
  });

  it("calls onFiltersChange to remove provider when already selected", async () => {
    const user = userEvent.setup();
    const props = renderFilters({
      filters: { ...DEFAULT_FILTERS, providers: ["Anthropic"] },
    });

    await user.click(screen.getByText("Anthropic"));

    expect(props.onFiltersChange).toHaveBeenCalledWith(
      expect.objectContaining({ providers: [] }),
    );
  });

  it("does not show Reset button when no filters are active", () => {
    renderFilters();

    expect(screen.queryByRole("button", { name: /reset/i })).not.toBeInTheDocument();
  });

  it("shows Reset button when filters are active", () => {
    renderFilters({
      filters: { ...DEFAULT_FILTERS, providers: ["OpenAI"] },
    });

    expect(screen.getByRole("button", { name: /reset/i })).toBeInTheDocument();
  });

  it("calls onFiltersChange with default filters when Reset is clicked", async () => {
    const user = userEvent.setup();
    const props = renderFilters({
      filters: {
        ...DEFAULT_FILTERS,
        providers: ["Google"],
        capabilities: ["vision"],
      },
    });

    await user.click(screen.getByRole("button", { name: /reset/i }));

    expect(props.onFiltersChange).toHaveBeenCalledWith(DEFAULT_FILTERS);
  });

  it("renders capability checkboxes", () => {
    renderFilters();

    expect(screen.getByText("Vision")).toBeInTheDocument();
    expect(screen.getByText("Function Calling")).toBeInTheDocument();
    expect(screen.getByText("JSON Mode")).toBeInTheDocument();
    expect(screen.getByText("Streaming")).toBeInTheDocument();
  });

  it("calls onFiltersChange when a capability is clicked", async () => {
    const user = userEvent.setup();
    const props = renderFilters();

    await user.click(screen.getByText("Vision"));

    expect(props.onFiltersChange).toHaveBeenCalledWith(
      expect.objectContaining({ capabilities: ["vision"] }),
    );
  });

  it("renders price range checkboxes", () => {
    renderFilters();

    expect(screen.getByText("Free")).toBeInTheDocument();
    expect(screen.getByText(/Low/)).toBeInTheDocument();
    expect(screen.getByText(/Medium/)).toBeInTheDocument();
    expect(screen.getByText(/High/)).toBeInTheDocument();
  });
});
