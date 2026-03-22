"use client";

import { useState, useEffect, useCallback } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import type { ApiKeyValidation } from "@/types/api";
import { API_KEY_STORAGE_KEY } from "@/lib/constants";

type KeyState = "empty" | "validating" | "valid" | "invalid" | "change";
const MASK_VISIBLE_CHARS = 8;

function maskKey(key: string): string {
  if (key.length <= MASK_VISIBLE_CHARS) return key;
  return key.slice(0, MASK_VISIBLE_CHARS) + "..." + key.slice(-4);
}

export function ApiKeyInput() {
  const [keyState, setKeyState] = useState<KeyState>("empty");
  const [inputValue, setInputValue] = useState("");
  const [storedKey, setStoredKey] = useState("");
  const [credits, setCredits] = useState<number | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const saved = sessionStorage.getItem(API_KEY_STORAGE_KEY);
    if (saved) {
      setStoredKey(saved);
      setKeyState("change");
      validateKey(saved);
    }
  // Only run on mount
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const validateKey = useCallback(async (key: string) => {
    setKeyState("validating");
    setErrorMessage("");

    try {
      const response = await fetch("/api/validate-key", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: key }),
      });

      const data: ApiKeyValidation = await response.json();

      if (data.valid) {
        sessionStorage.setItem(API_KEY_STORAGE_KEY, key);
        setStoredKey(key);
        setCredits(data.credits_remaining ?? null);
        setKeyState("valid");
      } else {
        setErrorMessage(data.error ?? "Invalid API key");
        setKeyState("invalid");
      }
    } catch {
      setErrorMessage("Failed to validate key. Please try again.");
      setKeyState("invalid");
    }
  }, []);

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const trimmed = inputValue.trim();
    if (!trimmed) return;
    validateKey(trimmed);
  }

  function handleChange() {
    setKeyState("empty");
    setInputValue("");
    setCredits(null);
  }

  function handleRemove() {
    sessionStorage.removeItem(API_KEY_STORAGE_KEY);
    setStoredKey("");
    setKeyState("empty");
    setInputValue("");
    setCredits(null);
  }

  if (keyState === "valid" || keyState === "change") {
    return (
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-sm">
          <span className="text-green-600 dark:text-green-400 font-medium">
            Valid
          </span>
          <span className="text-muted-foreground">
            {maskKey(storedKey)}
          </span>
          {credits !== null && (
            <span className="text-muted-foreground">
              | Remaining: ${credits.toFixed(2)}
            </span>
          )}
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleChange}
          className="min-h-[44px] min-w-[44px]"
        >
          Change
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleRemove}
          className="min-h-[44px] min-w-[44px] text-muted-foreground"
          aria-label="Remove API key"
        >
          Remove
        </Button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-2">
      <label htmlFor="api-key-input" className="sr-only">
        OpenRouter API Key
      </label>
      <Input
        id="api-key-input"
        type="password"
        placeholder="Enter OpenRouter API key (sk-or-...)"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        disabled={keyState === "validating"}
        className="w-64 min-h-[44px]"
        autoComplete="off"
      />
      <Button
        type="submit"
        size="sm"
        disabled={keyState === "validating" || !inputValue.trim()}
        className="min-h-[44px] min-w-[44px]"
      >
        {keyState === "validating" ? "Validating..." : "Verify"}
      </Button>
      {keyState === "invalid" && (
        <span className="text-sm text-destructive">{errorMessage}</span>
      )}
    </form>
  );
}
