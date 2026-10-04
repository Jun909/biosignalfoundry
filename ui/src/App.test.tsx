/**
 * Tests for App's submit/loading/result/error state machine.
 *
 * analyzeStock is mocked at the module boundary — these tests are about
 * App's own state transitions, not the SSE parsing (covered separately in
 * api/biosignalfoundry.test.ts).
 */

import { act, cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import { analyzeStock } from "./api/biosignalfoundry";
import type { AnalysisResult } from "./api/biosignalfoundry";

vi.mock("./api/biosignalfoundry", () => ({
  analyzeStock: vi.fn(),
}));

const mockedAnalyzeStock = vi.mocked(analyzeStock);

const SAMPLE_RESULT: AnalysisResult = {
  ticker: "nvda",
  decision: "Buy",
  confidence: 85,
  reasoning: "Strong pipeline",
};

const INPUT_PLACEHOLDER = /ask about any biotech stock/i;

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("App", () => {
  it("renders the query form and suggestions before anything is submitted", () => {
    render(<App />);

    expect(screen.getByPlaceholderText(INPUT_PLACEHOLDER)).toBeInTheDocument();
    expect(screen.getByText("Should I invest in Moderna?")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "ANALYZE" })).toBeDisabled();
  });

  it("submits the typed query and renders the returned result", async () => {
    mockedAnalyzeStock.mockResolvedValue(SAMPLE_RESULT);
    const user = userEvent.setup();
    render(<App />);

    // Typed lowercase so the "Query" label ("nvda") and the uppercased
    // ticker display ("NVDA") don't collide as the same text node.
    await user.type(screen.getByPlaceholderText(INPUT_PLACEHOLDER), "nvda");
    await user.click(screen.getByRole("button", { name: "ANALYZE" }));

    expect(mockedAnalyzeStock).toHaveBeenCalledWith("nvda", expect.any(Function));

    await waitFor(() => expect(screen.getByText("NVDA")).toBeInTheDocument());
    expect(screen.getByText("Buy")).toBeInTheDocument();
    expect(screen.getByText("85%")).toBeInTheDocument();
    expect(screen.getByText("Strong pipeline")).toBeInTheDocument();
  });

  it("shows a loading state while the request is in flight", async () => {
    let resolvePromise: (value: AnalysisResult) => void = () => {};
    mockedAnalyzeStock.mockReturnValue(
      new Promise((resolve) => {
        resolvePromise = resolve;
      }),
    );
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByPlaceholderText(INPUT_PLACEHOLDER), "nvda");
    await user.click(screen.getByRole("button", { name: "ANALYZE" }));

    expect(screen.getByText(/analyzing/i)).toBeInTheDocument();

    act(() => resolvePromise(SAMPLE_RESULT));
    await waitFor(() => expect(screen.getByText("NVDA")).toBeInTheDocument());
  });

  it("surfaces the latest progress message while loading", async () => {
    let onProgress: (message: string) => void = () => {};
    mockedAnalyzeStock.mockImplementation((_input, progressCallback) => {
      onProgress = progressCallback;
      return new Promise(() => {});
    });
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByPlaceholderText(INPUT_PLACEHOLDER), "NVDA");
    await user.click(screen.getByRole("button", { name: "ANALYZE" }));

    act(() => onProgress("Fetching financials..."));

    await waitFor(() =>
      expect(screen.getByText("Fetching financials...")).toBeInTheDocument(),
    );
  });

  it("shows the error message when analyzeStock rejects", async () => {
    mockedAnalyzeStock.mockRejectedValue(
      new Error("Too many requests, please slow down."),
    );
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByPlaceholderText(INPUT_PLACEHOLDER), "NVDA");
    await user.click(screen.getByRole("button", { name: "ANALYZE" }));

    await waitFor(() =>
      expect(screen.getByText("Too many requests, please slow down.")).toBeInTheDocument(),
    );
  });

  it("falls back to a generic error message for non-Error rejections", async () => {
    mockedAnalyzeStock.mockRejectedValue("network died");
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByPlaceholderText(INPUT_PLACEHOLDER), "NVDA");
    await user.click(screen.getByRole("button", { name: "ANALYZE" }));

    await waitFor(() =>
      expect(
        screen.getByText("Could not reach the server. Is the backend running?"),
      ).toBeInTheDocument(),
    );
  });

  it("clicking a suggestion submits it directly, without needing the form", async () => {
    mockedAnalyzeStock.mockResolvedValue({
      ticker: "mrna",
      decision: "Hold",
      confidence: 50,
      reasoning: "Mixed signals",
    });
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByText("Should I invest in Moderna?"));

    expect(mockedAnalyzeStock).toHaveBeenCalledWith(
      "Should I invest in Moderna?",
      expect.any(Function),
    );
    await waitFor(() => expect(screen.getByText("MRNA")).toBeInTheDocument());
  });

  it("returns to the query screen when 'New query' is clicked", async () => {
    mockedAnalyzeStock.mockResolvedValue(SAMPLE_RESULT);
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByPlaceholderText(INPUT_PLACEHOLDER), "nvda");
    await user.click(screen.getByRole("button", { name: "ANALYZE" }));
    await waitFor(() => expect(screen.getByText("NVDA")).toBeInTheDocument());

    await user.click(screen.getByRole("button", { name: /new query/i }));

    expect(screen.getByPlaceholderText(INPUT_PLACEHOLDER)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(INPUT_PLACEHOLDER)).toHaveValue("");
  });
});
