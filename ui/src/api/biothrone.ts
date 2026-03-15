const API_BASE_URL = import.meta.env.VITE_API_URL ?? "";

export async function analyzeStock(
    userInput: string,
    onToken: (token:string) => void,
    onDone: () => void
): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_input: userInput}),
    });

    if (!response.ok) throw new Error("Request failed");

    const reader = response.body!.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const lines = decoder.decode(value).split("\n");
        for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            const content = line.replace("data: ", "").trim();
            if (content === "[DONE]") { onDone(); return; }
            if (content) onToken(content);
        }

    }
}