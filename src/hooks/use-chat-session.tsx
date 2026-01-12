import { useCallback, useState } from "react";

const STORAGE_KEY = "flora_chat_session_id";

const createSessionId = () => {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

export function useChatSession() {
  const [sessionId, setSessionId] = useState(() => {
    if (typeof window === "undefined") return "";
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored) return stored;
    const generated = createSessionId();
    window.localStorage.setItem(STORAGE_KEY, generated);
    return generated;
  });

  const resetSession = useCallback(() => {
    const generated = createSessionId();
    if (typeof window !== "undefined") {
      window.localStorage.setItem(STORAGE_KEY, generated);
    }
    setSessionId(generated);
  }, []);

  return {
    sessionId,
    resetSession,
  };
}
