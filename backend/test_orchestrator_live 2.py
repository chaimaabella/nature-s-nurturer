from agent.orchestrator import handle_message

# Pose ta question réelle ici
question = "Ma monstera a des feuilles jaunes et brunes, que faire ?"

# Appel de l'orchestrator
response = handle_message(question, session_id="session_test")

print("\n=== ORCHESTRATOR LIVE TEST ===\n")
print("Question utilisateur :")
print(question)
print("\nReply (IA ou fallback) :")
print(response["reply"])
print("\nTools utilisés :")
print(response["tools_used"])
print("\nSources récupérées :")
for s in response["sources"]:
    print(f"- {s['title']} : {s['url']}")
