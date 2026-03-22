import type { ComparisonReport } from "@/types/model";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface SSECallbacks {
  onThinking: (message: string) => void;
  onToolCall: (
    tool: string,
    reasoning: string,
    params: Record<string, unknown>,
  ) => void;
  onToolResult: (tool: string, summary: string) => void;
  onReport: (report: ComparisonReport) => void;
  onDone: () => void;
  onError: (message: string) => void;
}

/**
 * POST /api/v1/advise 로 SSE 스트리밍을 수행한다.
 * fetch + ReadableStream 기반 — EventSource는 POST를 지원하지 않으므로 사용하지 않는다.
 */
export async function streamAdvisor(
  userInput: string,
  apiKey: string,
  analysisModel: string,
  callbacks: SSECallbacks,
  signal?: AbortSignal,
): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}/api/v1/advise`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_input: userInput,
        api_key: apiKey,
        analysis_model: analysisModel,
      }),
      signal,
    });
  } catch (error: unknown) {
    if (error instanceof DOMException && error.name === "AbortError") return;
    callbacks.onError(
      "서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.",
    );
    return;
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    const message =
      (errorBody as { detail?: string } | null)?.detail ??
      `Request failed: ${response.status}`;
    callbacks.onError(message);
    return;
  }

  if (!response.body) {
    callbacks.onError("Response body is empty");
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  const MAX_BUFFER_SIZE = 1024 * 1024; // 1MB

  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      if (buffer.length > MAX_BUFFER_SIZE) {
        callbacks.onError("Buffer overflow: response too large");
        reader.cancel();
        return;
      }
      const events = parseSSEBuffer(buffer);
      buffer = events.remaining;

      for (const evt of events.parsed) {
        dispatchEvent(evt, callbacks);
      }
    }

    // 남은 버퍼 처리
    if (buffer.trim()) {
      const events = parseSSEBuffer(buffer + "\n\n");
      for (const evt of events.parsed) {
        dispatchEvent(evt, callbacks);
      }
    }
  } catch (error: unknown) {
    if (error instanceof DOMException && error.name === "AbortError") {
      return;
    }
    const message = error instanceof Error ? error.message : "Stream failed";
    callbacks.onError(message);
  }
}

interface ParsedSSEEvent {
  event: string;
  data: string;
}

interface ParseResult {
  parsed: ParsedSSEEvent[];
  remaining: string;
}

/**
 * SSE 버퍼를 파싱하여 완성된 이벤트와 남은 버퍼를 반환한다.
 * 청크 경계에서 이벤트가 나뉠 수 있으므로 빈 줄(\n\n)로 이벤트를 구분한다.
 */
function parseSSEBuffer(buffer: string): ParseResult {
  const parsed: ParsedSSEEvent[] = [];
  const blocks = buffer.split("\n\n");

  // 마지막 블록은 아직 완성되지 않았을 수 있음
  const remaining = blocks.pop() ?? "";

  for (const block of blocks) {
    const trimmed = block.trim();
    if (!trimmed) continue;

    let event = "";
    let data = "";

    for (const line of trimmed.split("\n")) {
      if (line.startsWith("event: ")) {
        event = line.slice(7);
      } else if (line.startsWith("data: ")) {
        data = line.slice(6);
      }
    }

    if (event && data) {
      parsed.push({ event, data });
    }
  }

  return { parsed, remaining };
}

function dispatchEvent(evt: ParsedSSEEvent, callbacks: SSECallbacks): void {
  try {
    const payload = JSON.parse(evt.data) as Record<string, unknown>;

    switch (evt.event) {
      case "thinking":
        callbacks.onThinking((payload.message as string) ?? "");
        break;
      case "tool_call":
        callbacks.onToolCall(
          (payload.tool as string) ?? "",
          (payload.reasoning as string) ?? "",
          (payload.params as Record<string, unknown>) ?? {},
        );
        break;
      case "tool_result":
        callbacks.onToolResult(
          (payload.tool as string) ?? "",
          (payload.summary as string) ?? "",
        );
        break;
      case "report":
        callbacks.onReport(payload as unknown as ComparisonReport);
        break;
      case "done":
        callbacks.onDone();
        break;
      case "error":
        callbacks.onError((payload.message as string) ?? "Unknown error");
        break;
    }
  } catch {
    callbacks.onError(`Failed to parse SSE event: ${evt.event}`);
  }
}
