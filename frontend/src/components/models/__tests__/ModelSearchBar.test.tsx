import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { ModelSearchBar } from "@/components/models/ModelSearchBar";

function renderSearchBar(
  overrides: Partial<Parameters<typeof ModelSearchBar>[0]> = {},
) {
  const props = {
    query: "",
    sort: "name_asc",
    onQueryChange: vi.fn(),
    onSortChange: vi.fn(),
    ...overrides,
  };
  render(<ModelSearchBar {...props} />);
  return props;
}

describe("ModelSearchBar", () => {
  it("renders the search input", () => {
    renderSearchBar();

    expect(screen.getByLabelText("Search models")).toBeInTheDocument();
  });

  it("renders the search input with the provided query value", () => {
    renderSearchBar({ query: "gpt" });

    expect(screen.getByLabelText("Search models")).toHaveValue("gpt");
  });

  it("calls onQueryChange after debounce when typing", async () => {
    const user = userEvent.setup();
    const props = renderSearchBar();

    await user.type(screen.getByLabelText("Search models"), "claude");

    await waitFor(() => {
      expect(props.onQueryChange).toHaveBeenCalled();
    });

    const lastCall = props.onQueryChange.mock.calls.at(-1);
    expect(lastCall?.[0]).toBe("claude");
  });

  it("renders the sort selector with accessible label", () => {
    renderSearchBar();

    expect(screen.getByLabelText("Sort models")).toBeInTheDocument();
  });
});
