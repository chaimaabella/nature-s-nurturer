import { useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { MessageCircle, X, Send, RefreshCw } from "lucide-react";
import logoImage from "@/assets/logo-nature.png";
import { markdownToHtml } from "@/lib/markdown";
import { useChatHistory, type ChatMessage } from "@/hooks/use-chat-history";

type Message = ChatMessage;

const initialMessages: Message[] = [
  {
    id: "welcome",
    role: "assistant",
    content: "Bonjour ! 🌿 Je suis Floria, votre assistant botanique. Comment puis-je vous aider avec vos plantes aujourd'hui ?",
  },
];

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const { messages, addMessage, resetMessages } = useChatHistory();
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const conversationIdRef = useRef(0);
  const displayMessages = messages.length > 0 ? messages : initialMessages;

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
    };

    addMessage(userMessage);
    setInput("");
    setIsLoading(true);
    const conversationId = conversationIdRef.current;

    // Simulate AI response (will be replaced with actual API)
    setTimeout(() => {
      if (conversationIdRef.current !== conversationId) {
        return;
      }
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Je comprends votre question ! Pour une réponse complète et personnalisée, je vous invite à utiliser notre assistant complet. Cliquez sur le bouton ci-dessous pour accéder à toutes les fonctionnalités.",
      };
      addMessage(assistantMessage);
      setIsLoading(false);
    }, 1000);
  };

  const handleReset = () => {
    if (typeof window !== "undefined") {
      const shouldReset = window.confirm("Voulez-vous démarrer une nouvelle conversation ? Votre historique sera effacé.");
      if (!shouldReset) return;
    }
    conversationIdRef.current += 1;
    resetMessages();
    setInput("");
    setIsLoading(false);
  };

  return (
    <>
      {/* Chat Widget Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 h-14 w-14 rounded-full cta-gradient shadow-nature-elevated flex items-center justify-center transition-transform hover:scale-110 active:scale-95"
        aria-label={isOpen ? "Fermer le chat" : "Ouvrir le chat"}
      >
        {isOpen ? (
          <X className="h-6 w-6 text-primary-foreground" />
        ) : (
          <MessageCircle className="h-6 w-6 text-primary-foreground" />
        )}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-50 w-[calc(100vw-3rem)] max-w-sm bg-card rounded-2xl shadow-nature-elevated border border-border overflow-hidden animate-slide-up">
          {/* Header */}
          <div className="p-4 border-b border-border bg-primary/5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <img src={logoImage} alt="Floria" className="h-10 w-10 rounded-full object-cover" />
                <div>
                  <h3 className="font-display font-semibold text-foreground">Floria</h3>
                  <p className="text-xs text-muted-foreground">Assistant botanique</p>
                </div>
              </div>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={handleReset}
                aria-label="Nouvelle conversation"
                disabled={messages.length === 0 && !isLoading}
              >
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Messages */}
          <div className="h-72 overflow-y-auto p-4 space-y-4">
            {displayMessages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-2.5 ${
                    message.role === "user"
                      ? "bg-primary text-primary-foreground rounded-br-md"
                      : "bg-muted text-foreground rounded-bl-md"
                  }`}
                >
                  {message.role === "assistant" ? (
                    <div
                      className="text-sm leading-relaxed"
                      dangerouslySetInnerHTML={{ __html: markdownToHtml(message.content) }}
                    />
                  ) : (
                    <p className="text-sm whitespace-pre-line">{message.content}</p>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-muted rounded-2xl rounded-bl-md px-4 py-3">
                  <div className="flex gap-1">
                    <span className="h-2 w-2 rounded-full bg-muted-foreground animate-pulse-soft" />
                    <span className="h-2 w-2 rounded-full bg-muted-foreground animate-pulse-soft" style={{ animationDelay: "0.2s" }} />
                    <span className="h-2 w-2 rounded-full bg-muted-foreground animate-pulse-soft" style={{ animationDelay: "0.4s" }} />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="p-4 border-t border-border">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="flex gap-2"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Posez une question..."
                className="flex-1 px-4 py-2.5 rounded-xl bg-muted border-0 text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20"
              />
              <Button
                type="submit"
                variant="nature"
                size="icon"
                disabled={!input.trim() || isLoading}
              >
                <Send className="h-4 w-4" />
              </Button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
