# backend/test_orchestrator.py

from agent.orchestrator import handle_message, _build_prompt

# -------------------------
# 1️⃣ Question de test
# -------------------------
message = "Ma monstera a des feuilles jaunes et brunes"
session_id = "session_test"

# -------------------------
# 2️⃣ Appel de l'orchestrator
# -------------------------
result = handle_message(message, session_id)

# -------------------------
# 3️⃣ Affichage des résultats
# -------------------------
print("=== ORCHESTRATOR TEST ===\n")
print("Question utilisateur :")
print(message, "\n")

print("Reply (IA ou fallback) :")
print(result["reply"], "\n")

print("Tools utilisés :")
print(result["tools_used"], "\n")

print("Sources récupérées :")
for s in result["sources"]:
    print(f"- {s['title']} : {s['url']}")
print("\n")

# -------------------------
# 4️⃣ (Optionnel) Voir le prompt envoyé à Ollama
# -------------------------
if result["tools_used"]:
    # On peut reconstruire le prompt pour debug
    intent = "diagnostic"  # ou utiliser _detect_intent(message)
    tool_context = None
    for s in result["sources"]:
        tool_context = (tool_context or "") + f"{s['title']} : {s['url']}\n"

    prompt = _build_prompt(message, intent, tool_context)
    print("=== PROMPT ENVOYÉ À OLLAMA ===")
    print(prompt)
