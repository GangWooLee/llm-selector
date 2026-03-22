import { describe, it, expect, beforeEach, vi } from "vitest";
import { streamAdvisor, type SSECallbacks } from "@/lib/sse-client";

function makeCallbacks(): SSECallbacks {
  return {
    onThinking: vi.fn(),
    onToolCall: vi.fn(),
    onToolResult: vi.fn(),
    onReport: vi.fn(),
    onDone: vi.fn(),
    onError: vi.fn(),
  };
}

function encodeChunks(chunks: string[]): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  let index = 0;
  return new ReadableStream({
    pull(controller) {
      if (index < chunks.length) {
        controller.enqueue(encoder.encode(chunks[index]));
        index++;
      } else {
        controller.close();
      }
    },
  });
}

function mockFetchSSE(chunks: string[], status = 200) {
  global.fetch = vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    body: encodeChunks(chunks),
    json: () => Promise.resolve({}),
  } as unknown as Response);
}

describe("streamAdvisor", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("parses thinking event", async () => {
    const cb = makeCallbacks();
    mockFetchSSE([
      'event: thinking\ndata: {"message":"Analyzing..."}\n\n',
    ]);

    await streamAdvisor("test input", "sk-key", "auto", cb);

    expect(cb.onThinking).toHaveBeenCalledWith("Analyzing...");
  });

  it("parses tool_call event", async () => {
    const cb = makeCallbacks();
    mockFetchSSE([
      'event: tool_call\ndata: {"tool":"search_models","reasoning":"Finding models","params":{"query":"test"}}\n\n',
    ]);

    await streamAdvisor("test", "sk-key", "auto", cb);

    expect(cb.onToolCall).toHaveBeenCalledWith(
      "search_models",
      "Finding models",
      { query: "test" },
    );
  });

  it("parses tool_result event", async () => {
    const cb = makeCallbacks();
    mockFetchSSE([
      'event: tool_result\ndata: {"tool":"search_models","summary":"Found 5 models"}\n\n',
    ]);

    await streamAdvisor("test", "sk-key", "auto", cb);

    expect(cb.onToolResult).toHaveBeenCalledWith(
      "search_models",
      "Found 5 models",
    );
  });

  it("parses report event", async () => {
    const cb = makeCallbacks();
    const report = {
      top_recommendation: { model_id: "m1", model_name: "GPT-4o", reason: "Best" },
      recommendations: [],
      summary: "Done",
      data_sources: [],
      agent_reasoning: [],
    };
    mockFetchSSE([
      `event: report\ndata: ${JSON.stringify(report)}\n\n`,
    ]);

    await streamAdvisor("test", "sk-key", "auto", cb);

    expect(cb.onReport).toHaveBeenCalledWith(report);
  });

  it("parses done event", async () => {
    const cb = makeCallbacks();
    mockFetchSSE([
      'event: done\ndata: {}\n\n',
    ]);

    await streamAdvisor("test", "sk-key", "auto", cb);

    expect(cb.onDone).toHaveBeenCalledOnce();
  });

  it("parses error event from SSE stream", async () => {
    const cb = makeCallbacks();
    mockFetchSSE([
      'event: error\ndata: {"message":"Agent timeout"}\n\n',
    ]);

    await streamAdvisor("test", "sk-key", "auto", cb);

    expect(cb.onError).toHaveBeenCalledWith("Agent timeout");
  });

  it("handles multiple events in a single chunk", async () => {
    const cb = makeCallbacks();
    mockFetchSSE([
      'event: thinking\ndata: {"message":"Step 1"}\n\nevent: thinking\ndata: {"message":"Step 2"}\n\n',
    ]);

    await streamAdvisor("test", "sk-key", "auto", cb);

    expect(cb.onThinking).toHaveBeenCalledTimes(2);
    expect(cb.onThinking).toHaveBeenNthCalledWith(1, "Step 1");
    expect(cb.onThinking).toHaveBeenNthCalledWith(2, "Step 2");
  });

  it("handles event split across chunk boundaries", async () => {
    const cb = makeCallbacks();
    mockFetchSSE([
      'event: thinking\ndata: {"mes',
      'sage":"Split event"}\n\n',
    ]);

    await streamAdvisor("test", "sk-key", "auto", cb);

    expect(cb.onThinking).toHaveBeenCalledWith("Split event");
  });

  it("handles event type and data in separate chunks", async () => {
    const cb = makeCallbacks();
    mockFetchSSE([
      'event: tool_result\n',
      'data: {"tool":"get_benchmarks","summary":"Scores loaded"}\n\n',
    ]);

    await streamAdvisor("test", "sk-key", "auto", cb);

    expect(cb.onToolResult).toHaveBeenCalledWith(
      "get_benchmarks",
      "Scores loaded",
    );
  });

  it("processes remaining buffer after stream ends", async () => {
    const cb = makeCallbacks();
    // No trailing \n\n — buffer has leftover data
    mockFetchSSE([
      'event: thinking\ndata: {"message":"Leftover"}',
    ]);

    await streamAdvisor("test", "sk-key", "auto", cb);

    expect(cb.onThinking).toHaveBeenCalledWith("Leftover");
  });

  it("calls onError for HTTP error response with detail", async () => {
    const cb = makeCallbacks();
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: () => Promise.resolve({ detail: "Invalid API key" }),
    } as unknown as Response);

    await streamAdvisor("test", "bad-key", "auto", cb);

    expect(cb.onError).toHaveBeenCalledWith("Invalid API key");
  });

  it("calls onError with status code when no detail in error response", async () => {
    const cb = makeCallbacks();
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: () => Promise.reject(new Error("not json")),
    } as unknown as Response);

    await streamAdvisor("test", "sk-key", "auto", cb);

    expect(cb.onError).toHaveBeenCalledWith("Request failed: 500");
  });

  it("calls onError when response body is null", async () => {
    const cb = makeCallbacks();
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      body: null,
    } as unknown as Response);

    await streamAdvisor("test", "sk-key", "auto", cb);

    expect(cb.onError).toHaveBeenCalledWith("Response body is empty");
  });

  it("silently returns on AbortSignal abort", async () => {
    const cb = makeCallbacks();
    const controller = new AbortController();

    const stream = new ReadableStream<Uint8Array>({
      pull() {
        controller.abort();
        return new Promise((_, reject) => {
          const error = new DOMException("Aborted", "AbortError");
          reject(error);
        });
      },
    });

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      body: stream,
    } as unknown as Response);

    await streamAdvisor("test", "sk-key", "auto", cb, controller.signal);

    expect(cb.onError).not.toHaveBeenCalled();
  });

  it("calls onError on non-abort stream error", async () => {
    const cb = makeCallbacks();

    const stream = new ReadableStream<Uint8Array>({
      pull() {
        return Promise.reject(new Error("Connection lost"));
      },
    });

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      body: stream,
    } as unknown as Response);

    await streamAdvisor("test", "sk-key", "auto", cb);

    expect(cb.onError).toHaveBeenCalledWith("Connection lost");
  });

  it("calls onError when SSE data contains invalid JSON", async () => {
    const cb = makeCallbacks();
    mockFetchSSE([
      'event: thinking\ndata: {invalid json}\n\n',
    ]);

    await streamAdvisor("test", "sk-key", "auto", cb);

    expect(cb.onError).toHaveBeenCalledWith(
      "Failed to parse SSE event: thinking",
    );
  });

  it("sends correct request body", async () => {
    const cb = makeCallbacks();
    mockFetchSSE(['event: done\ndata: {}\n\n']);

    await streamAdvisor("my use case", "sk-test-key", "google/gemini-3-flash-preview", cb);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/advise"),
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_input: "my use case",
          api_key: "sk-test-key",
          analysis_model: "google/gemini-3-flash-preview",
        }),
      }),
    );
  });

  it("passes AbortSignal to fetch", async () => {
    const cb = makeCallbacks();
    mockFetchSSE(['event: done\ndata: {}\n\n']);
    const controller = new AbortController();

    await streamAdvisor("test", "sk-key", "auto", cb, controller.signal);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({ signal: controller.signal }),
    );
  });
});
