const API_BASE_URL = import.meta.env.VITE_API_URL ?? "";

export interface AnalysisResult {
    ticker: string;
    decision: string;
    confidence: number;
    reasoning: string;
}

export async function analyzeStock(userInput: string): Promise<AnalysisResult> {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_input: userInput }),
    });

    if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body?.detail ?? `Server error ${response.status}`);
    }

    return response.json();
}