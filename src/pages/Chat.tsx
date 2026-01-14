import { useState, useEffect, useRef } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Send, ArrowLeft, Sparkles, RefreshCw } from "lucide-react";
import { markdownToHtml } from "@/lib/markdown";
import logoImage from "@/assets/logo-floria.svg";
import { useChatHistory, type ChatMessage } from "@/hooks/use-chat-history";
import { useChatSession } from "@/hooks/use-chat-session";
import { formatChatReply, sendChatMessage } from "@/lib/chat-api";

type Message = ChatMessage;

const suggestedQuestions = [
  "Pourquoi les feuilles de mon monstera jaunissent-elles ?",
  "Comment bouturer un pothos ?",
  "Ma plante a des taches brunes, que faire ?",
  "Quelle est la fréquence d'arrosage pour un cactus ?",
];

export default function Chat() {
  const [searchParams] = useSearchParams();
  const { messages, setMessages, addMessage, resetMessages } = useChatHistory();
  const { sessionId, resetSession } = useChatSession();
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const conversationIdRef = useRef(0);

  const handleReset = () => {
    resetMessages();
    resetSession();
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Check for initial question from URL
    const initialQuestion = searchParams.get("q");
    if (initialQuestion) {
      handleSend(initialQuestion);
    }
  }, []);

  const handleSend = async (messageText?: string) => {
  const text = messageText || input.trim();
  if (!text || isLoading) return;

  const userMessage: Message = {
    id: Date.now().toString(),
    role: "user",
    content: text,
  };

  setMessages((prev) => [...prev, userMessage]);
  setInput("");
  setIsLoading(true);

  try {
    // Appel au backend /chat
    const response = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        session_id: sessionId,
      }),
    });

    const data = await response.json();

    // On récupère la réponse envoyée par l'orchestrator
    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: data.reply || "Désolé, je n'ai pas pu générer de réponse.",
    };

    setMessages((prev) => [...prev, assistantMessage]);
  } catch (err) {
    console.error("Erreur backend:", err);

    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: "Désolé, le backend n'a pas répondu. Réessayez plus tard.",
    };

    setMessages((prev) => [...prev, assistantMessage]);
  } finally {
    setIsLoading(false);
  }
};

  return (
    <div className="min-h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur">
        <div className="container flex h-16 items-center gap-4">
          <Link to="/" className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors">
            <ArrowLeft className="h-5 w-5" />
            <span className="hidden sm:inline">Retour</span>
          </Link>
          
          <div className="flex-1 flex items-center justify-center gap-2">
            <img
              src={logoImage}
              alt="FlorIA"
              className="h-9 w-9 rounded-lg object-cover"
            />
            <span className="font-display text-xl font-semibold text-foreground">FlorIA</span>
          </div>

          <div className="flex w-20 justify-end">
            <Button
              type="button"
              variant="outline"
              size="icon"
              onClick={handleReset}
              disabled={messages.length === 0 && !isLoading}
              aria-label="Nouvelle conversation"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      {/* Chat Area */}
      <main className="flex-1 overflow-hidden">
        <div className="h-full max-w-3xl mx-auto flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center px-4">
                <div className="h-20 w-20 rounded-2xl bg-accent flex items-center justify-center mb-6">
                  <Sparkles className="h-10 w-10 text-primary" />
                </div>
                <h1 className="font-display text-2xl md:text-3xl font-bold text-foreground mb-3">
                  Bienvenue sur FlorIA
                </h1>
                <p className="text-muted-foreground max-w-md mb-8">
                  Posez-moi vos questions sur l'entretien de vos plantes. Je suis là pour vous aider !
                </p>
                
                <div className="grid sm:grid-cols-2 gap-3 w-full max-w-lg">
                  {suggestedQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => handleSend(question)}
                      className="p-4 text-left rounded-xl bg-card border border-border hover:border-primary/50 hover:shadow-nature transition-all text-sm text-foreground"
                    >
                      "{question}"
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <>
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[85%] md:max-w-[75%] rounded-2xl px-5 py-3 ${
                        message.role === "user"
                          ? "bg-primary text-primary-foreground rounded-br-md"
                          : "bg-card border border-border text-foreground rounded-bl-md"
                      }`}
                    >
                      {message.role === "assistant" ? (
                        <div
                          className="text-sm md:text-base leading-relaxed"
                          dangerouslySetInnerHTML={{ __html: markdownToHtml(message.content) }}
                        />
                      ) : (
                        <div className="text-sm md:text-base whitespace-pre-line">
                          {message.content}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-card border border-border rounded-2xl rounded-bl-md px-5 py-4">
                      <div className="flex gap-1.5">
                        <span className="h-2.5 w-2.5 rounded-full bg-primary/40 animate-pulse-soft" />
                        <span className="h-2.5 w-2.5 rounded-full bg-primary/40 animate-pulse-soft" style={{ animationDelay: "0.2s" }} />
                        <span className="h-2.5 w-2.5 rounded-full bg-primary/40 animate-pulse-soft" style={{ animationDelay: "0.4s" }} />
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* Input Area */}
          <div className="border-t border-border bg-background p-4 md:p-6">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="flex gap-3"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Posez une question sur vos plantes..."
                className="flex-1 px-5 py-3 rounded-xl bg-muted border-0 text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 text-base"
              />
              <Button
                type="submit"
                variant="nature"
                size="lg"
                disabled={!input.trim() || isLoading}
                className="px-6"
              >
                <Send className="h-5 w-5" />
                <span className="hidden sm:inline ml-2">Envoyer</span>
              </Button>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
