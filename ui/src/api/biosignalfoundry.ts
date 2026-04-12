const API_BASE_URL = import.meta.env.VITE_API_URL ?? "";

export interface AnalysisResult {
    ticker: string;
    decision: string;
    confidence: number;
    reasoning: string;
}

export async function analyzeStock(
    userInput: string,
    onProgress: (message: string) => void,
): Promise<AnalysisResult> {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_input: userInput }),
    });

    if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body?.detail ?? `Server error ${response.status}`);
    }

    const reader = response.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop() ?? "";

        for (const part of parts) {
            if (!part.startsWith("data: ")) continue;
            const event = JSON.parse(part.slice(6));

            if (event.type === "progress") {
                onProgress(event.message);
            } else if (event.type === "result") {
                return event.data as AnalysisResult;
            } else if (event.type === "error") {
                throw new Error(event.message);
            }
        }
    }

    throw new Error("Stream ended without a result");
}
