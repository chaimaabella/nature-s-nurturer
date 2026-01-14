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

const CHAT_ENDPOINT = "http://localhost:8000/chat";

export const formatChatReply = (payload: ChatApiResponse) => {
  let content = payload.reply;

  if (payload.sources?.length) {
    const sources = payload.sources
      .map((source) => `- [${source.title}](${source.url})`)
      .join("\n");
    content = `${content}\n\n**Sources :**\n${sources}`;
  }

  return content;
};

export const sendChatMessage = async ({ message, sessionId }: ChatRequest) => {
  const response = await fetch(CHAT_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    throw new Error("chat_request_failed");
  }

  return (await response.json()) as ChatApiResponse;
};
