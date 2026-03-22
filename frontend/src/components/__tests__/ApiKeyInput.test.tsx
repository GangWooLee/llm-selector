import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, beforeEach, vi } from "vitest";
import { ApiKeyInput } from "@/components/ApiKeyInput";

function mockFetchSuccess(credits: number) {
  return vi.fn().mockResolvedValue({
    ok: true,
    json: () =>
      Promise.resolve({ valid: true, credits_remaining: credits }),
  });
}

function mockFetchInvalid(error: string) {
  return vi.fn().mockResolvedValue({
    ok: true,
    json: () => Promise.resolve({ valid: false, error }),
  });
}

function mockFetchNetworkError() {
  return vi.fn().mockRejectedValue(new Error("Network error"));
}

describe("ApiKeyInput", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    sessionStorage.clear();
  });

  describe("empty state", () => {
    it("renders the input field when no key is stored", () => {
      render(<ApiKeyInput />);

      expect(screen.getByLabelText("OpenRouter API Key")).toBeInTheDocument();
    });

    it("renders the verify button", () => {
      render(<ApiKeyInput />);

      expect(
        screen.getByRole("button", { name: /verify/i }),
      ).toBeInTheDocument();
    });

    it("disables the verify button when input is empty", () => {
      render(<ApiKeyInput />);

      expect(screen.getByRole("button", { name: /verify/i })).toBeDisabled();
    });
  });

  describe("validating state", () => {
    it("shows validating text while key is being verified", async () => {
      // fetch that never resolves to keep the validating state
      global.fetch = vi.fn(
        () => new Promise<Response>(() => {}),
      );
      const user = userEvent.setup();

      render(<ApiKeyInput />);

      await user.type(screen.getByLabelText("OpenRouter API Key"), "sk-or-test");
      await user.click(screen.getByRole("button", { name: /verify/i }));

      expect(
        screen.getByRole("button", { name: /validating/i }),
      ).toBeInTheDocument();
    });

    it("disables the input while validating", async () => {
      global.fetch = vi.fn(
        () => new Promise<Response>(() => {}),
      );
      const user = userEvent.setup();

      render(<ApiKeyInput />);

      await user.type(screen.getByLabelText("OpenRouter API Key"), "sk-or-test");
      await user.click(screen.getByRole("button", { name: /verify/i }));

      expect(screen.getByLabelText("OpenRouter API Key")).toBeDisabled();
    });
  });

  describe("valid state", () => {
    it("displays the masked key on successful validation", async () => {
      global.fetch = mockFetchSuccess(12.5);
      const user = userEvent.setup();

      render(<ApiKeyInput />);

      await user.type(
        screen.getByLabelText("OpenRouter API Key"),
        "sk-or-v1-abcdefghijklmnop",
      );
      await user.click(screen.getByRole("button", { name: /verify/i }));

      await waitFor(() => {
        expect(screen.getByText("Valid")).toBeInTheDocument();
      });
    });

    it("shows remaining credits after validation", async () => {
      global.fetch = mockFetchSuccess(12.5);
      const user = userEvent.setup();

      render(<ApiKeyInput />);

      await user.type(
        screen.getByLabelText("OpenRouter API Key"),
        "sk-or-v1-abcdefghijklmnop",
      );
      await user.click(screen.getByRole("button", { name: /verify/i }));

      await waitFor(() => {
        expect(screen.getByText(/\$12\.50/)).toBeInTheDocument();
      });
    });

    it("shows change and remove buttons in valid state", async () => {
      global.fetch = mockFetchSuccess(5.0);
      const user = userEvent.setup();

      render(<ApiKeyInput />);

      await user.type(
        screen.getByLabelText("OpenRouter API Key"),
        "sk-or-v1-abcdefghijklmnop",
      );
      await user.click(screen.getByRole("button", { name: /verify/i }));

      await waitFor(() => {
        expect(
          screen.getByRole("button", { name: /change/i }),
        ).toBeInTheDocument();
        expect(
          screen.getByRole("button", { name: /remove/i }),
        ).toBeInTheDocument();
      });
    });
  });

  describe("invalid state", () => {
    it("displays error message for invalid key", async () => {
      global.fetch = mockFetchInvalid("Invalid API key");
      const user = userEvent.setup();

      render(<ApiKeyInput />);

      await user.type(
        screen.getByLabelText("OpenRouter API Key"),
        "bad-key",
      );
      await user.click(screen.getByRole("button", { name: /verify/i }));

      await waitFor(() => {
        expect(screen.getByText("Invalid API key")).toBeInTheDocument();
      });
    });

    it("displays fallback error on network failure", async () => {
      global.fetch = mockFetchNetworkError();
      const user = userEvent.setup();

      render(<ApiKeyInput />);

      await user.type(
        screen.getByLabelText("OpenRouter API Key"),
        "sk-or-test",
      );
      await user.click(screen.getByRole("button", { name: /verify/i }));

      await waitFor(() => {
        expect(
          screen.getByText("Failed to validate key. Please try again."),
        ).toBeInTheDocument();
      });
    });
  });

  describe("sessionStorage persistence", () => {
    it("stores the key in sessionStorage on successful validation", async () => {
      global.fetch = mockFetchSuccess(10.0);
      const user = userEvent.setup();

      render(<ApiKeyInput />);

      await user.type(
        screen.getByLabelText("OpenRouter API Key"),
        "sk-or-v1-mykey123",
      );
      await user.click(screen.getByRole("button", { name: /verify/i }));

      await waitFor(() => {
        expect(sessionStorage.getItem("openrouter_api_key")).toBe(
          "sk-or-v1-mykey123",
        );
      });
    });

    it("restores saved key from sessionStorage on mount", async () => {
      sessionStorage.setItem("openrouter_api_key", "sk-or-v1-savedkey99");
      global.fetch = mockFetchSuccess(7.25);

      render(<ApiKeyInput />);

      await waitFor(() => {
        expect(screen.getByText("Valid")).toBeInTheDocument();
      });
    });

    it("removes key from sessionStorage when remove button is clicked", async () => {
      global.fetch = mockFetchSuccess(3.0);
      const user = userEvent.setup();

      render(<ApiKeyInput />);

      await user.type(
        screen.getByLabelText("OpenRouter API Key"),
        "sk-or-v1-toremove",
      );
      await user.click(screen.getByRole("button", { name: /verify/i }));

      await waitFor(() => {
        expect(screen.getByText("Valid")).toBeInTheDocument();
      });

      await user.click(screen.getByRole("button", { name: /remove/i }));

      expect(sessionStorage.getItem("openrouter_api_key")).toBeNull();
    });
  });

  describe("change flow", () => {
    it("returns to empty state when change button is clicked", async () => {
      global.fetch = mockFetchSuccess(5.0);
      const user = userEvent.setup();

      render(<ApiKeyInput />);

      await user.type(
        screen.getByLabelText("OpenRouter API Key"),
        "sk-or-v1-abcdefghijklmnop",
      );
      await user.click(screen.getByRole("button", { name: /verify/i }));

      await waitFor(() => {
        expect(screen.getByText("Valid")).toBeInTheDocument();
      });

      await user.click(screen.getByRole("button", { name: /change/i }));

      expect(screen.getByLabelText("OpenRouter API Key")).toBeInTheDocument();
    });
  });

  describe("form submission", () => {
    it("does not submit when input is whitespace only", async () => {
      global.fetch = vi.fn();
      const user = userEvent.setup();

      render(<ApiKeyInput />);

      const input = screen.getByLabelText("OpenRouter API Key");
      await user.type(input, "   ");
      // Button should still be disabled since trimmed value is empty
      expect(screen.getByRole("button", { name: /verify/i })).toBeDisabled();
      expect(global.fetch).not.toHaveBeenCalled();
    });

    it("sends POST to /api/validate-key with correct body", async () => {
      global.fetch = mockFetchSuccess(1.0);
      const user = userEvent.setup();

      render(<ApiKeyInput />);

      await user.type(
        screen.getByLabelText("OpenRouter API Key"),
        "sk-or-v1-testkey",
      );
      await user.click(screen.getByRole("button", { name: /verify/i }));

      expect(global.fetch).toHaveBeenCalledWith("/api/validate-key", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: "sk-or-v1-testkey" }),
      });
    });
  });
});
