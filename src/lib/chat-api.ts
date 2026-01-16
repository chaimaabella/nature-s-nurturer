// src/lib/chatApi.ts

export type ChatSource = {
  title: string;
  url: string;
};

export type ChatApiResponse = {
  reply: string;
  tools_used?: string[];
  sources?: ChatSource[];
};

type ChatRequest = {
  message: string;
  sessionId: string;
};

/**
 * URL du backend
 * - Priorité à la variable d'environnement Vite
 * - Fallback en local si non définie
 */
const API_BASE_URL = (
  (import.meta.env.VITE_API_URL as string | undefined) ??
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://127.0.0.1:8000"
).trim().replace(/\/+$/, ""); // supprime les / finaux

const CHAT_ENDPOINT = `${API_BASE_URL}/chat`;

/**
 * Formate la réponse du backend (texte + sources)
 */
export const formatChatReply = (payload: ChatApiResponse): string => {
  const base = payload?.reply ?? "";
  const sources = payload?.sources?.length
    ? payload.sources
        .filter((s) => s?.title && s?.url)
        .map((s) => `• [${s.title}](${s.url})`)
        .join("\n")
    : "";

  return sources ? `${base}\n\n**Sources :**\n${sources}` : base;
};

/**
 * Envoie un message au backend FastAPI
 */
export const sendChatMessage = async ({
  message,
  sessionId,
}: ChatRequest): Promise<ChatApiResponse> => {
  const response = await fetch(CHAT_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      session_id: sessionId, // snake_case attendu par le backend
    }),
  });

  if (!response.ok) {
    const errorText = await response.text().catch(() => "");
    console.error("Chat API error:", response.status, errorText);
    throw new Error(`chat_request_failed:${response.status}`);
  }

  const data = (await response.json()) as ChatApiResponse;

  // Sécurise un minimum le format attendu
  return {
    reply: data?.reply ?? "",
    tools_used: data?.tools_used ?? [],
    sources: data?.sources ?? [],
  };
};