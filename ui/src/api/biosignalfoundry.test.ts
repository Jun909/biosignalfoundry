/**
 * Tests for analyzeStock's SSE parsing over a mocked fetch.
 *
 * global.fetch is stubbed with a fake Response whose body.getReader()
 * yields one pre-encoded "data: ...\n\n" chunk per call — this exercises
 * the same incremental buffer/split parsing analyzeStock actually runs,
 * without needing a real network connection or ReadableStream.
 */

import { afterEach, describe, expect, it, vi } from "vitest";
import { analyzeStock } from "./biosignalfoundry";

function fakeResponse(
  events: string[],
  opts: { ok?: boolean; status?: number; json?: () => Promise<unknown> } = {},
): Response {
  const chunks = events.map((e) => `data: ${e}\n\n`);
  const encoder = new TextEncoder();
  let i = 0;

  return {
    ok: opts.ok ?? true,
    status: opts.status ?? 200,
    json: opts.json ?? (async () => ({})),
    body: {
      getReader() {
        return {
          async read() {
            if (i < chunks.length) {
              const value = encoder.encode(chunks[i]);
              i += 1;
              return { done: false, value };
            }
            return { done: true, value: undefined };
          },
        };
      },
    },
  } as unknown as Response;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("analyzeStock", () => {
  it("reports progress events and resolves with the result event's data", async () => {
    const events = [
      JSON.stringify({ type: "progress", message: "Fetching financials..." }),
      JSON.stringify({ type: "progress", message: "Reasoning..." }),
      JSON.stringify({
        type: "result",
        data: { ticker: "NVDA", decision: "Buy", confidence: 85, reasoning: "Strong pipeline" },
      }),
    ];
    const fetchMock = vi.fn().mockResolvedValue(fakeResponse(events));
    vi.stubGlobal("fetch", fetchMock);

    const onProgress = vi.fn();
    const result = await analyzeStock("NVDA", onProgress);

    expect(onProgress).toHaveBeenNthCalledWith(1, "Fetching financials...");
    expect(onProgress).toHaveBeenNthCalledWith(2, "Reasoning...");
    expect(result).toEqual({
      ticker: "NVDA",
      decision: "Buy",
      confidence: 85,
      reasoning: "Strong pipeline",
    });
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/analyze"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ user_input: "NVDA" }),
      }),
    );
  });

  it("rejects with the message from an error event", async () => {
    const events = [JSON.stringify({ type: "error", message: "Agent invocation failed" })];
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(fakeResponse(events)));

    await expect(analyzeStock("NVDA", () => {})).rejects.toThrow("Agent invocation failed");
  });

  it("rejects if the stream ends without ever emitting a result", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(fakeResponse([])));

    await expect(analyzeStock("NVDA", () => {})).rejects.toThrow(
      "Stream ended without a result",
    );
  });

  it("rejects with the server's detail message on a non-ok response", async () => {
    const response = fakeResponse([], {
      ok: false,
      status: 429,
      json: async () => ({ detail: "Too many requests, please slow down." }),
    });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response));

    await expect(analyzeStock("NVDA", () => {})).rejects.toThrow(
      "Too many requests, please slow down.",
    );
  });

  it("falls back to a generic message when a non-ok response has no JSON body", async () => {
    const response = fakeResponse([], {
      ok: false,
      status: 500,
      json: async () => {
        throw new Error("not json");
      },
    });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response));

    await expect(analyzeStock("NVDA", () => {})).rejects.toThrow("Server error 500");
  });
});
