import { render, screen } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import { Header } from "@/components/layout/Header";

describe("Header", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    sessionStorage.clear();
  });

  it("renders the app title", () => {
    render(<Header />);

    expect(
      screen.getByRole("link", { name: "LLM Selector" }),
    ).toBeInTheDocument();
  });

  it("renders the ApiKeyInput component", () => {
    render(<Header />);

    expect(screen.getByLabelText("OpenRouter API Key")).toBeInTheDocument();
  });
});
