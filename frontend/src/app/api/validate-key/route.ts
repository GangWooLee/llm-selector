import { NextResponse } from "next/server";
import type { ApiKeyValidation } from "@/types/api";

interface ValidateKeyBody {
  api_key?: string;
}

export async function POST(request: Request) {
  const body = (await request.json()) as ValidateKeyBody;
  const apiKey = body.api_key;

  if (!apiKey || typeof apiKey !== "string") {
    return NextResponse.json(
      { valid: false, error: "API key is required" } satisfies ApiKeyValidation,
      { status: 400 },
    );
  }

  try {
    const response = await fetch("https://openrouter.ai/api/v1/key", {
      headers: { Authorization: `Bearer ${apiKey}` },
      signal: AbortSignal.timeout(15000),
    });

    if (!response.ok) {
      return NextResponse.json(
        { valid: false, error: "Invalid API key" } satisfies ApiKeyValidation,
        { status: 401 },
      );
    }

    const data = (await response.json()) as {
      data?: {
        limit?: number | null;
        usage?: number;
        limit_remaining?: number | null;
      };
    };

    const keyData = data.data;
    const creditsRemaining = keyData?.limit_remaining ?? null;
    const usage = keyData?.usage ?? 0;

    const result: ApiKeyValidation = {
      valid: true,
      credits_remaining: creditsRemaining ?? undefined,
      usage: {
        daily: usage,
        weekly: usage,
        monthly: usage,
      },
    };

    return NextResponse.json(result);
  } catch {
    return NextResponse.json(
      { valid: false, error: "Failed to reach OpenRouter" } satisfies ApiKeyValidation,
      { status: 502 },
    );
  }
}
