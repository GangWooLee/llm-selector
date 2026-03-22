import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { AdvisorForm } from "@/components/advisor/AdvisorForm";

function renderForm(overrides: Partial<Parameters<typeof AdvisorForm>[0]> = {}) {
  const props = {
    userInput: "",
    onUserInputChange: vi.fn(),
    selectedModel: "auto",
    onSelectedModelChange: vi.fn(),
    onSubmit: vi.fn(),
    isStreaming: false,
    hasApiKey: true,
    ...overrides,
  };
  render(<AdvisorForm {...props} />);
  return props;
}

describe("AdvisorForm", () => {
  describe("rendering", () => {
    it("renders the textarea", () => {
      renderForm();

      expect(
        screen.getByLabelText("Describe your use case"),
      ).toBeInTheDocument();
    });

    it("renders the analysis model selector", () => {
      renderForm();

      expect(
        screen.getByRole("combobox", { name: /select analysis model/i }),
      ).toBeInTheDocument();
    });

    it("renders the submit button with Start Analysis text", () => {
      renderForm();

      expect(
        screen.getByRole("button", { name: /start analysis/i }),
      ).toBeInTheDocument();
    });

    it("shows Analyzing text when streaming", () => {
      renderForm({ isStreaming: true, userInput: "a valid input text" });

      expect(
        screen.getByRole("button", { name: /analyzing/i }),
      ).toBeInTheDocument();
    });
  });

  describe("validation", () => {
    it("disables submit when input is empty", () => {
      renderForm({ userInput: "" });

      expect(
        screen.getByRole("button", { name: /start analysis/i }),
      ).toBeDisabled();
    });

    it("disables submit when input is too short", () => {
      renderForm({ userInput: "short" });

      expect(
        screen.getByRole("button", { name: /start analysis/i }),
      ).toBeDisabled();
    });

    it("enables submit when input meets minimum length", () => {
      renderForm({ userInput: "I need a model for customer support chatbot" });

      expect(
        screen.getByRole("button", { name: /start analysis/i }),
      ).toBeEnabled();
    });

    it("disables submit when API key is missing", () => {
      renderForm({
        userInput: "I need a model for customer support chatbot",
        hasApiKey: false,
      });

      expect(
        screen.getByRole("button", { name: /start analysis/i }),
      ).toBeDisabled();
    });

    it("shows tooltip when API key is missing", () => {
      renderForm({
        userInput: "I need a model for customer support chatbot",
        hasApiKey: false,
      });

      expect(
        screen.getByTitle("Enter your API key first"),
      ).toBeInTheDocument();
    });

    it("shows tooltip when input is too short", () => {
      renderForm({ userInput: "short" });

      expect(
        screen.getByTitle("Please describe your use case in more detail"),
      ).toBeInTheDocument();
    });

    it("disables submit while streaming", () => {
      renderForm({
        userInput: "I need a model for customer support chatbot",
        isStreaming: true,
      });

      expect(
        screen.getByRole("button", { name: /analyzing/i }),
      ).toBeDisabled();
    });
  });

  describe("submission", () => {
    it("calls onSubmit when form is submitted with valid input", async () => {
      const user = userEvent.setup();
      const props = renderForm({
        userInput: "I need a model for customer support chatbot",
      });

      await user.click(
        screen.getByRole("button", { name: /start analysis/i }),
      );

      expect(props.onSubmit).toHaveBeenCalledOnce();
    });

    it("does not call onSubmit when input is too short", async () => {
      const user = userEvent.setup();
      const props = renderForm({ userInput: "short" });

      // Button is disabled, so click should not trigger submit
      await user.click(
        screen.getByRole("button", { name: /start analysis/i }),
      );

      expect(props.onSubmit).not.toHaveBeenCalled();
    });
  });

  describe("input handling", () => {
    it("calls onUserInputChange when typing", async () => {
      const user = userEvent.setup();
      const props = renderForm();

      const textarea = screen.getByLabelText("Describe your use case");
      await user.type(textarea, "a");

      expect(props.onUserInputChange).toHaveBeenCalled();
    });

    it("disables textarea while streaming", () => {
      renderForm({ isStreaming: true });

      expect(screen.getByLabelText("Describe your use case")).toBeDisabled();
    });
  });
});
