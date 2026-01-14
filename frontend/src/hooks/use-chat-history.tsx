import { useCallback, useEffect, useState, type SetStateAction } from "react";

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  ts?: number;
};

type ChatHistoryPayload = {
  version: number;
  messages: ChatMessage[];
};

const STORAGE_KEY = "flora_chat_history_v1";
const STORAGE_VERSION = 1;
const MAX_MESSAGES = 50;

const trimMessages = (messages: ChatMessage[]) => messages.slice(-MAX_MESSAGES);

const isValidMessage = (message: unknown): message is ChatMessage => {
  if (!message || typeof message !== "object") return false;
  const candidate = message as ChatMessage;
  return (
    typeof candidate.id === "string" &&
    (candidate.role === "user" || candidate.role === "assistant") &&
    typeof candidate.content === "string"
  );
};

export function useChatHistory() {
  const [messages, setMessagesState] = useState<ChatMessage[]>([]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (!stored) return;

    try {
      const parsed = JSON.parse(stored) as ChatHistoryPayload;
      if (parsed?.version !== STORAGE_VERSION || !Array.isArray(parsed.messages)) {
        return;
      }

      const sanitized = trimMessages(parsed.messages.filter(isValidMessage));
      setMessagesState(sanitized);
    } catch {
      setMessagesState([]);
    }
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;

    if (messages.length === 0) {
      window.localStorage.removeItem(STORAGE_KEY);
      return;
    }

    const payload: ChatHistoryPayload = {
      version: STORAGE_VERSION,
      messages: trimMessages(messages),
    };

    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    } catch {
      // Ignore write errors (e.g. storage quota)
    }
  }, [messages]);

  const setMessages = useCallback(
    (value: SetStateAction<ChatMessage[]>) => {
      setMessagesState((prev) => {
        const next = typeof value === "function" ? value(prev) : value;
        return trimMessages(next);
      });
    },
    [],
  );

  const addMessage = useCallback(
    (message: ChatMessage) => {
      const enriched = {
        ...message,
        ts: message.ts ?? Date.now(),
      };
      setMessages((prev) => [...prev, enriched]);
    },
    [setMessages],
  );

  const resetMessages = useCallback(() => {
    setMessagesState([]);
    if (typeof window !== "undefined") {
      window.localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  return {
    messages,
    setMessages,
    addMessage,
    resetMessages,
  };
}
