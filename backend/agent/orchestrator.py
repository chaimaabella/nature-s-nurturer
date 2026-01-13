# backend/agent/orchestrator.py

import os
import re
import requests
from typing import Optional, Dict, Any, List

# Mémoire simple en RAM (MVP)
CHAT_MEMORY: Dict[str, List[Dict[str, str]]] = {}

"""
But
---
Orchestrator = "chef d'orchestre" entre :

1) Backend principal (/chat)
   → reçoit la question utilisateur

2) MCP Server (/execute)
   → exécute des tools contrôlés (scraping, etc.)

3) Ollama (LLM local)
   → génère la réponse finale


Contrat de sortie (utilisé par backend/main.py)
----------------------------------------------
handle_message(...) retourne toujours :

{
  "reply": str,
  "tools_used": [str],
  "sources": [{"title": "...", "url": "..."}]
}
"""

# ============================================================================
# CONFIGURATION (ENV VARS)
# ============================================================================

# MCP
MCP_URL = os.getenv("MCP_URL", "http://localhost:8000")  # Serveur déjà lancé
MCP_EXECUTE_ENDPOINT = os.getenv("MCP_EXECUTE_ENDPOINT", "/execute")
MCP_TIMEOUT = int(os.getenv("MCP_TIMEOUT", "60"))  # Augmenté à 60 secondes

# OLLAMA
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))  # Augmenté à 120 secondes


# ============================================================================
# MCP CALL
# ============================================================================

def _mcp_execute(tool: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Appel MCP via HTTP POST /execute
    """
    url = f"{MCP_URL}{MCP_EXECUTE_ENDPOINT}"
    payload = {"tool": tool, "arguments": arguments}

    resp = requests.post(url, json=payload, timeout=MCP_TIMEOUT)

    if resp.status_code != 200:
        raise RuntimeError(f"MCP error {resp.status_code}: {resp.text}")

    return resp.json()


# ============================================================================
# OLLAMA CALL (LLM)
# ============================================================================

def _call_ollama(messages: List[Dict[str, str]], model: str = OLLAMA_MODEL) -> str:
    """
    Appel Ollama local avec historique de conversation.
    """
    payload = {
        "model": model,
        "messages": messages,
        "stream": False
    }

    r = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
    r.raise_for_status()

    data = r.json()
    return (data.get("message", {}).get("content") or "").strip()


def _fallback_reply(message: str, tool_context: Optional[str] = None) -> str:
    """
    Réponse fallback (MVP) si Ollama n'est pas prêt ou en erreur.
    """
    base = (
        "Je suis Floria (mode MVP sans modèle).\n\n"
        "Pour t'aider au mieux, peux-tu préciser :\n"
        "1) Quelle plante exactement ?\n"
        "2) Exposition (lumière directe / indirecte) ?\n"
        "3) Fréquence d'arrosage ?\n"
        "4) Symptômes visibles (jaunissement, taches, feuilles molles) ?\n\n"
        f"Tu as demandé : {message}\n"
    )

    if tool_context:
        base += f"\nContexte (extraits de sources) : {tool_context}\n"

    return base


# ============================================================================
# INTENT + ENTITY EXTRACTION (MVP)
# ============================================================================

def _detect_intent(message: str) -> str:
    """
    Détecte une intention simple :
    - diagnostic : si symptômes détectés
    - entretien  : sinon
    """
    msg = message.lower()

    symptom_words = [
        "jaunit", "jaunissent", "tache", "taches",
        "molle", "pourrit", "brune", "brunes",
        "tombe", "chute", "sec", "sèche", "seche",
        "feuilles molles", "racines", "moisi", "champignon"
    ]

    return "diagnostic" if any(w in msg for w in symptom_words) else "entretien"


def _extract_plant(message: str) -> Optional[str]:
    """
    Extraction simple du nom de plante depuis le message utilisateur.
    """
    msg = message.lower()

    known = [
        "monstera", "pothos", "cactus", "ficus",
        "orchidée", "orchidee", "succulente",
        "aloe", "aloé", "calathea", "philodendron",
        "sansevieria", "zamioculcas", "yucca", "dracaena",
        "tournesol", "tournesols", "basilic", "tomate", "tomates",
        "rose", "roses", "lavande", "fougère", "fougere"
    ]

    for k in known:
        if k in msg:
            return k

    m = re.search(r"\b(mon|ma|mes)\s+([a-zàâçéèêëîïôûùüÿñæœ-]{3,})\b", msg)
    if m:
        candidate = m.group(2)
        if candidate not in ["plante", "feuille", "feuilles", "pot", "terreau"]:
            return candidate

    return None


# ============================================================================
# MAIN ENTRYPOINT (appelé par /chat)
# ============================================================================

def handle_message(message: str, session_id: str) -> Dict[str, Any]:
    """
    Point d'entrée principal de l'orchestrator avec gestion de l'historique.
    """
    intent = _detect_intent(message)
    plant = _extract_plant(message)

    tools_used: List[str] = []
    sources: List[Dict[str, str]] = []
    tool_context: Optional[str] = None

    # ------------------------------------------------------------------------
    # 1) Appel MCP si plante détectée
    # ------------------------------------------------------------------------
    if plant:
        print(f"🌿 Plante détectée : {plant}")
        try:
            print(f"📞 Appel MCP avec query={plant}")
            mcp_res = _mcp_execute(
                "fetch_plant_sources",
                {"query": plant, "limit": 2}
            )
            print(f"✅ Réponse MCP : {mcp_res}")

            if mcp_res.get("status") == "success":
                tools_used.append(mcp_res.get("tool", "fetch_plant_sources"))

                # Le MCP retourne result.result (double imbrication)
                result = mcp_res.get("result") or {}
                
                # Si double imbrication, extraire le vrai result
                if "result" in result:
                    result = result.get("result") or {}
                
                tool_context = result.get("summary")
                print(f"📝 Contexte récupéré : {tool_context[:200] if tool_context else 'VIDE'}...")

                for s in result.get("sources", []):
                    if s.get("url"):
                        sources.append({
                            "title": s.get("source_name") or s.get("title") or plant,
                            "url": s["url"]
                        })
                print(f"🔗 Sources trouvées : {len(sources)}")
            else:
                print(f"❌ MCP a échoué")
                tools_used.append("fetch_plant_sources_failed")

        except Exception as e:
            print(f"💥 Erreur MCP : {e}")
            tools_used.append("fetch_plant_sources_failed")
    else:
        print(f"⚠️ Aucune plante détectée dans : {message}")

    # ------------------------------------------------------------------------
    # 2) Gestion de l'historique de conversation
    # ------------------------------------------------------------------------
    
    # Initialisation mémoire session si première fois
    if session_id not in CHAT_MEMORY:
        CHAT_MEMORY[session_id] = [
            {
                "role": "system",
                "content": (
                    "# Contexte\n"
                    "Tu es **FlorIA**, un assistant IA spécialisé dans l'entretien des plantes d'intérieur et d'extérieur. "
                    "Tu donnes des conseils pratiques, clairs et actionnables, en t'appuyant PRIORITAIREMENT sur des informations issues de 2 sources :\n"
                    "1) https://www.conservation-nature.fr/plantes/\n"
                    "2) http://nature.jardin.free.fr\n\n"
                    "Tu peux utiliser des outils de recherche/scraping fournis par l'orchestrator pour récupérer des extraits pertinents de ces sites. "
                    "Tu n'inventes jamais de faits botaniques : si l'info n'est pas trouvée dans les sources, tu le dis.\n\n"
                    
                    "# Détection d'intention (OBLIGATOIRE)\n"
                    "Avant de répondre, identifie l'intention principale de l'utilisateur :\n\n"
                    "1) **Diagnostic** → il décrit un problème :\n"
                    "   - feuilles jaunes / brunes\n"
                    "   - feuilles molles\n"
                    "   - taches\n"
                    "   - parasites\n"
                    "   - plante qui meurt\n"
                    "   - odeur bizarre\n"
                    "   - chute de feuilles\n"
                    "   - etc.\n\n"
                    "2) **Conseil / Entretien** → il veut apprendre ou anticiper :\n"
                    "   - comment arroser\n"
                    "   - où placer la plante\n"
                    "   - quand rempoter\n"
                    "   - quelle lumière\n"
                    "   - comment bien l'entretenir\n"
                    "   - conseils généraux\n\n"
                    "3) **Identification** → il ne sait pas quelle est sa plante\n\n"
                    "Adapte ton format de réponse en fonction de cette intention.\n\n"
                    
                    "# Objectif\n"
                    "Aider l'utilisateur à :\n"
                    "- Identifier la plante (si besoin)\n"
                    "- Comprendre un symptôme (diagnostic)\n"
                    "- Proposer un plan d'action concret\n"
                    "- Donner des recommandations d'entretien claires\n\n"
                    
                    "# Style de réponse\n"
                    "- Réponses en français, ton simple, bienveillant, 'mode coach plantes'\n"
                    "- Format structuré et court : listes, étapes, check-list\n"
                    "- Priorité à l'action : 'Fais A, puis B, puis C'\n"
                    "- Si plusieurs causes possibles : donne les 2-3 hypothèses les plus probables et comment trancher rapidement\n"
                    "- Évite le blabla et les généralités\n\n"
                    
                    "# Formats selon l'intention\n\n"
                    "## Si intention = DIAGNOSTIC\n"
                    "Toujours produire :\n"
                    "1) Diagnostic probable (2-3 hypothèses max)\n"
                    "2) Causes possibles\n"
                    "3) Actions immédiates (aujourd'hui)\n"
                    "4) Plan 7 jours\n"
                    "5) Erreurs à éviter\n"
                    "6) Questions finales (max 2-3)\n\n"
                    
                    "## Si intention = CONSEIL / ENTRETIEN\n"
                    "Toujours produire :\n"
                    "1) Bonnes pratiques essentielles\n"
                    "2) Fréquence (arrosage, lumière, etc.)\n"
                    "3) Signes que tout va bien / mal\n"
                    "4) Astuces simples\n"
                    "5) Erreurs courantes\n\n"
                    
                    "## Si intention = IDENTIFICATION\n"
                    "Toujours produire :\n"
                    "1) Hypothèses possibles (si texte seul)\n"
                    "2) Demande de photo si nécessaire\n"
                    "3) Indices pour reconnaître la plante\n"
                    "4) Famille botanique probable\n"
                    "5) Conseils de base temporaires (safe)\n\n"
                    
                    "# Données à collecter (si manquantes)\n"
                    "Si infos insuffisantes, pose au maximum 3 questions ciblées :\n"
                    "1) Plante (nom ou photo si possible) + depuis quand\n"
                    "2) Exposition + fréquence d'arrosage\n"
                    "3) Symptômes visibles\n\n"
                    "Ne repose pas ces questions si tu as déjà les infos.\n\n"
                    
                    "# Règles de sourcing\n"
                    "- Utilise les outils (scraping/recherche) pour obtenir des extraits des 2 sites.\n"
                    "- Cite clairement la source.\n"
                    "- Si non trouvé : le dire + proposer une solution prudente.\n\n"
                    
                    "# Logique de diagnostic (priorités)\n"
                    "1) Arrosage / drainage\n"
                    "2) Lumière\n"
                    "3) Substrat / racines\n"
                    "4) Humidité / température\n"
                    "5) Nutrition\n"
                    "6) Parasites / maladies\n\n"
                    
                    "# Sécurité / limites\n"
                    "- Pas de conseils dangereux\n"
                    "- Prévenir si plante toxique\n"
                    "- Proposer bouturage si plante condamnée\n\n"
                    
                    "# Latence / concision\n"
                    "Réponds en moins de 1200 caractères quand c'est possible. "
                    "Ne fais pas de longs paragraphes. Va droit au but."
                )
            }
        ]

    # Ajout du message utilisateur (avec contexte MCP intégré si disponible)
    user_message = message
    if tool_context:
        # Limiter le contexte à 500 caractères pour éviter les timeouts
        short_context = tool_context[:500] + "..." if len(tool_context) > 500 else tool_context
        user_message = f"{message}\n\n[Contexte fiable scraped : {short_context}]"
    
    CHAT_MEMORY[session_id].append({
        "role": "user",
        "content": user_message
    })

    # ------------------------------------------------------------------------
    # 3) Appel LLM avec historique ou fallback
    # ------------------------------------------------------------------------
    try:
        print(f"🤖 Appel Ollama avec {len(CHAT_MEMORY[session_id])} messages en historique")
        reply = _call_ollama(CHAT_MEMORY[session_id])
        print(f"✅ Réponse Ollama reçue : {reply[:100]}...")
        
        # Sauvegarde de la réponse dans l'historique
        CHAT_MEMORY[session_id].append({
            "role": "assistant",
            "content": reply
        })
        
    except Exception as e:
        # En cas d'erreur Ollama, utiliser le fallback
        print(f"💥 Erreur Ollama : {e}")
        reply = _fallback_reply(message, tool_context)
        
        # Sauvegarder quand même le fallback dans l'historique
        CHAT_MEMORY[session_id].append({
            "role": "assistant",
            "content": reply
        })

    # ------------------------------------------------------------------------
    # 4) Retour du contrat attendu
    # ------------------------------------------------------------------------
    return {
        "reply": reply,
        "tools_used": tools_used,
        "sources": sources
    }

# import os
# import re
# import requests
# from typing import Optional, Dict, Any, List

# # Mémoire simple en RAM (MVP)
# CHAT_MEMORY: Dict[str, List[Dict[str, str]]] = {}

# """
# But
# ---
# Orchestrator = "chef d'orchestre" entre :

# 1) Backend principal (/chat)
#    → reçoit la question utilisateur

# 2) MCP Server (/execute)
#    → exécute des tools contrôlés (scraping, etc.)

# 3) Ollama (LLM local)
#    → génère la réponse finale


# Contrat de sortie (utilisé par backend/main.py)
# ----------------------------------------------
# handle_message(...) retourne toujours :

# {
#   "reply": str,
#   "tools_used": [str],
#   "sources": [{"title": "...", "url": "..."}]
# }
# """

# # ============================================================================
# # CONFIGURATION (ENV VARS)
# # ============================================================================

# # MCP
# MCP_URL = os.getenv("MCP_URL", "http://localhost:9001")
# MCP_EXECUTE_ENDPOINT = os.getenv("MCP_EXECUTE_ENDPOINT", "/execute")
# MCP_TIMEOUT = int(os.getenv("MCP_TIMEOUT", "30"))

# # OLLAMA
# OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
# OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
# OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "60"))


# # ============================================================================
# # MCP CALL
# # ============================================================================

# def _mcp_execute(tool: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Appel MCP via HTTP POST /execute
#     """
#     url = f"{MCP_URL}{MCP_EXECUTE_ENDPOINT}"
#     payload = {"tool": tool, "arguments": arguments}

#     resp = requests.post(url, json=payload, timeout=MCP_TIMEOUT)

#     if resp.status_code != 200:
#         raise RuntimeError(f"MCP error {resp.status_code}: {resp.text}")

#     return resp.json()


# # ============================================================================
# # OLLAMA CALL (LLM)
# # ============================================================================

# def _call_ollama(messages: List[Dict[str, str]], model: str = OLLAMA_MODEL) -> str:
#     """
#     Appel Ollama local avec historique de conversation.
#     """
#     payload = {
#         "model": model,
#         "messages": messages,
#         "stream": False
#     }

#     r = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
#     r.raise_for_status()

#     data = r.json()
#     return (data.get("message", {}).get("content") or "").strip()


# def _fallback_reply(message: str, tool_context: Optional[str] = None) -> str:
#     """
#     Réponse fallback (MVP) si Ollama n'est pas prêt ou en erreur.
#     """
#     base = (
#         "Je suis Floria (mode MVP sans modèle).\n\n"
#         "Pour t'aider au mieux, peux-tu préciser :\n"
#         "1) Quelle plante exactement ?\n"
#         "2) Exposition (lumière directe / indirecte) ?\n"
#         "3) Fréquence d'arrosage ?\n"
#         "4) Symptômes visibles (jaunissement, taches, feuilles molles) ?\n\n"
#         f"Tu as demandé : {message}\n"
#     )

#     if tool_context:
#         base += f"\nContexte (extraits de sources) : {tool_context}\n"

#     return base


# # ============================================================================
# # INTENT + ENTITY EXTRACTION (MVP)
# # ============================================================================

# def _detect_intent(message: str) -> str:
#     """
#     Détecte une intention simple :
#     - diagnostic : si symptômes détectés
#     - entretien  : sinon
#     """
#     msg = message.lower()

#     symptom_words = [
#         "jaunit", "jaunissent", "tache", "taches",
#         "molle", "pourrit", "brune", "brunes",
#         "tombe", "chute", "sec", "sèche", "seche",
#         "feuilles molles", "racines", "moisi", "champignon"
#     ]

#     return "diagnostic" if any(w in msg for w in symptom_words) else "entretien"


# def _extract_plant(message: str) -> Optional[str]:
#     """
#     Extraction simple du nom de plante depuis le message utilisateur.
#     """
#     msg = message.lower()

#     known = [
#         "monstera", "pothos", "cactus", "ficus",
#         "orchidée", "orchidee", "succulente",
#         "aloe", "aloé", "calathea", "philodendron",
#         "sansevieria", "zamioculcas", "yucca", "dracaena"
#     ]

#     for k in known:
#         if k in msg:
#             return k

#     m = re.search(r"\b(mon|ma|mes)\s+([a-zàâçéèêëîïôûùüÿñæœ-]{3,})\b", msg)
#     if m:
#         candidate = m.group(2)
#         if candidate not in ["plante", "feuille", "feuilles", "pot", "terreau"]:
#             return candidate

#     return None


# # ============================================================================
# # MAIN ENTRYPOINT (appelé par /chat)
# # ============================================================================

# def handle_message(message: str, session_id: str) -> Dict[str, Any]:
#     """
#     Point d'entrée principal de l'orchestrator avec gestion de l'historique.
#     """
#     intent = _detect_intent(message)
#     plant = _extract_plant(message)

#     tools_used: List[str] = []
#     sources: List[Dict[str, str]] = []
#     tool_context: Optional[str] = None

#     # ------------------------------------------------------------------------
#     # 1) Appel MCP si plante détectée
#     # ------------------------------------------------------------------------
#     if plant:
#         print(f"🌿 Plante détectée : {plant}")
#         try:
#             print(f"📞 Appel MCP avec query={plant}")
#             mcp_res = _mcp_execute(
#                 "fetch_plant_sources",
#                 {"query": plant, "limit": 2}
#             )
#             print(f"✅ Réponse MCP : {mcp_res}")

#             if mcp_res.get("status") == "success":
#                 tools_used.append(mcp_res.get("tool", "fetch_plant_sources"))

#                 result = mcp_res.get("result") or {}
#                 tool_context = result.get("summary")
#                 print(f"📝 Contexte récupéré : {tool_context[:200] if tool_context else 'VIDE'}...")

#                 for s in result.get("sources", []):
#                     if s.get("url"):
#                         sources.append({
#                             "title": s.get("source_name") or s.get("title") or plant,
#                             "url": s["url"]
#                         })
#                 print(f"🔗 Sources trouvées : {len(sources)}")
#             else:
#                 print(f"❌ MCP a échoué")
#                 tools_used.append("fetch_plant_sources_failed")

#         except Exception as e:
#             print(f"💥 Erreur MCP : {e}")
#             tools_used.append("fetch_plant_sources_failed")
#     else:
#         print(f"⚠️ Aucune plante détectée dans : {message}")

#     # ------------------------------------------------------------------------
#     # 2) Gestion de l'historique de conversation
#     # ------------------------------------------------------------------------
    
#     # Initialisation mémoire session si première fois
#     if session_id not in CHAT_MEMORY:
#         CHAT_MEMORY[session_id] = [
#             {
#                 "role": "system",
#                 "content": (
#                     "Tu es Floria, assistante experte en entretien des plantes. "
#                     "Réponds de façon naturelle, cohérente avec l'historique. "
#                     "Évite de reposer des questions déjà répondues. "
#                     "Ton : concis, posé, orienté solution."
#                 )
#             }
#         ]

#     # Ajout du message utilisateur (avec contexte MCP intégré si disponible)
#     user_message = message
#     if tool_context:
#         user_message = f"{message}\n\n[Contexte fiable scraped : {tool_context}]"
    
#     CHAT_MEMORY[session_id].append({
#         "role": "user",
#         "content": user_message
#     })

#     # ------------------------------------------------------------------------
#     # 3) Appel LLM avec historique ou fallback
#     # ------------------------------------------------------------------------
#     try:
#         reply = _call_ollama(CHAT_MEMORY[session_id])
        
#         # Sauvegarde de la réponse dans l'historique
#         CHAT_MEMORY[session_id].append({
#             "role": "assistant",
#             "content": reply
#         })
        
#     except Exception as e:
#         # En cas d'erreur Ollama, utiliser le fallback
#         reply = _fallback_reply(message, tool_context)
        
#         # Sauvegarder quand même le fallback dans l'historique
#         CHAT_MEMORY[session_id].append({
#             "role": "assistant",
#             "content": reply
#         })

#     # ------------------------------------------------------------------------
#     # 4) Retour du contrat attendu
#     # ------------------------------------------------------------------------
#     return {
#         "reply": reply,
#         "tools_used": tools_used,
#         "sources": sources
#     }

# # backend/agent/orchestrator.py

# import os
# import re
# import requests
# from typing import Optional, Dict, Any, List

# # Mémoire simple en RAM (MVP)
# CHAT_MEMORY: Dict[str, List[Dict[str, str]]] = {}

# """
# But
# ---
# Orchestrator = "chef d'orchestre" entre :

# 1) Backend principal (/chat)
#    → reçoit la question utilisateur

# 2) MCP Server (/execute)
#    → exécute des tools contrôlés (scraping, etc.)

# 3) Ollama (LLM local)
#    → génère la réponse finale


# Contrat de sortie (utilisé par backend/main.py)
# ----------------------------------------------
# handle_message(...) retourne toujours :

# {
#   "reply": str,
#   "tools_used": [str],
#   "sources": [{"title": "...", "url": "..."}]
# }
# """

# # ============================================================================
# # CONFIGURATION (ENV VARS)
# # ============================================================================

# # MCP
# MCP_URL = os.getenv("MCP_URL", "http://localhost:9001")
# MCP_EXECUTE_ENDPOINT = os.getenv("MCP_EXECUTE_ENDPOINT", "/execute")
# MCP_TIMEOUT = int(os.getenv("MCP_TIMEOUT", "30"))

# # OLLAMA
# OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
# OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
# OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "60"))


# # ============================================================================
# # MCP CALL
# # ============================================================================

# def _mcp_execute(tool: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Appel MCP via HTTP POST /execute
#     """
#     url = f"{MCP_URL}{MCP_EXECUTE_ENDPOINT}"
#     payload = {"tool": tool, "arguments": arguments}

#     resp = requests.post(url, json=payload, timeout=MCP_TIMEOUT)

#     if resp.status_code != 200:
#         raise RuntimeError(f"MCP error {resp.status_code}: {resp.text}")

#     return resp.json()


# # ============================================================================
# # OLLAMA CALL (LLM)
# # ============================================================================

# def _call_ollama(messages: List[Dict[str, str]], model: str = OLLAMA_MODEL) -> str:
#     """
#     Appel Ollama local avec historique de conversation.
#     """
#     payload = {
#         "model": model,
#         "messages": messages,
#         "stream": False
#     }

#     r = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
#     r.raise_for_status()

#     data = r.json()
#     return (data.get("message", {}).get("content") or "").strip()


# def _fallback_reply(message: str, tool_context: Optional[str] = None) -> str:
#     """
#     Réponse fallback (MVP) si Ollama n'est pas prêt ou en erreur.
#     """
#     base = (
#         "Je suis Floria (mode MVP sans modèle).\n\n"
#         "Pour t'aider au mieux, peux-tu préciser :\n"
#         "1) Quelle plante exactement ?\n"
#         "2) Exposition (lumière directe / indirecte) ?\n"
#         "3) Fréquence d'arrosage ?\n"
#         "4) Symptômes visibles (jaunissement, taches, feuilles molles) ?\n\n"
#         f"Tu as demandé : {message}\n"
#     )

#     if tool_context:
#         base += f"\nContexte (extraits de sources) : {tool_context}\n"

#     return base


# # ============================================================================
# # INTENT + ENTITY EXTRACTION (MVP)
# # ============================================================================

# def _detect_intent(message: str) -> str:
#     """
#     Détecte une intention simple :
#     - diagnostic : si symptômes détectés
#     - entretien  : sinon
#     """
#     msg = message.lower()

#     symptom_words = [
#         "jaunit", "jaunissent", "tache", "taches",
#         "molle", "pourrit", "brune", "brunes",
#         "tombe", "chute", "sec", "sèche", "seche",
#         "feuilles molles", "racines", "moisi", "champignon"
#     ]

#     return "diagnostic" if any(w in msg for w in symptom_words) else "entretien"


# def _extract_plant(message: str) -> Optional[str]:
#     """
#     Extraction simple du nom de plante depuis le message utilisateur.
#     """
#     msg = message.lower()

#     known = [
#         "monstera", "pothos", "cactus", "ficus",
#         "orchidée", "orchidee", "succulente",
#         "aloe", "aloé", "calathea", "philodendron",
#         "sansevieria", "zamioculcas", "yucca", "dracaena"
#     ]

#     for k in known:
#         if k in msg:
#             return k

#     m = re.search(r"\b(mon|ma|mes)\s+([a-zàâçéèêëîïôûùüÿñæœ-]{3,})\b", msg)
#     if m:
#         candidate = m.group(2)
#         if candidate not in ["plante", "feuille", "feuilles", "pot", "terreau"]:
#             return candidate

#     return None


# # ============================================================================
# # MAIN ENTRYPOINT (appelé par /chat)
# # ============================================================================

# def handle_message(message: str, session_id: str) -> Dict[str, Any]:
#     """
#     Point d'entrée principal de l'orchestrator avec gestion de l'historique.
#     """
#     intent = _detect_intent(message)
#     plant = _extract_plant(message)

#     tools_used: List[str] = []
#     sources: List[Dict[str, str]] = []
#     tool_context: Optional[str] = None

#     # ------------------------------------------------------------------------
#     # 1) Appel MCP si plante détectée
#     # ------------------------------------------------------------------------
#     if plant:
#         try:
#             mcp_res = _mcp_execute(
#                 "fetch_plant_sources",
#                 {"query": plant, "limit": 2}
#             )

#             if mcp_res.get("status") == "success":
#                 tools_used.append(mcp_res.get("tool", "fetch_plant_sources"))

#                 result = mcp_res.get("result") or {}
#                 tool_context = result.get("summary")

#                 for s in result.get("sources", []):
#                     if s.get("url"):
#                         sources.append({
#                             "title": s.get("source_name") or s.get("title") or plant,
#                             "url": s["url"]
#                         })
#             else:
#                 tools_used.append("fetch_plant_sources_failed")

#         except Exception:
#             tools_used.append("fetch_plant_sources_failed")

#     # ------------------------------------------------------------------------
#     # 2) Gestion de l'historique de conversation
#     # ------------------------------------------------------------------------
    
#     # Initialisation mémoire session si première fois
#     if session_id not in CHAT_MEMORY:
#         CHAT_MEMORY[session_id] = [
#             {
#                 "role": "system",
#                 "content": (
#                     "Tu es Floria, assistante experte en entretien des plantes. "
#                     "Réponds de façon naturelle, cohérente avec l'historique. "
#                     "Évite de reposer des questions déjà répondues. "
#                     "Ton : concis, posé, orienté solution."
#                 )
#             }
#         ]

#     # Injection du contexte MCP si disponible (avant le message user)
#     if tool_context:
#         CHAT_MEMORY[session_id].append({
#             "role": "system",
#             "content": f"Contexte fiable (sources vérifiées) : {tool_context}"
#         })

#     # Ajout du message utilisateur
#     CHAT_MEMORY[session_id].append({
#         "role": "user",
#         "content": message
#     })

#     # ------------------------------------------------------------------------
#     # 3) Appel LLM avec historique ou fallback
#     # ------------------------------------------------------------------------
#     try:
#         reply = _call_ollama(CHAT_MEMORY[session_id])
        
#         # Sauvegarde de la réponse dans l'historique
#         CHAT_MEMORY[session_id].append({
#             "role": "assistant",
#             "content": reply
#         })
        
#     except Exception as e:
#         # En cas d'erreur Ollama, utiliser le fallback
#         reply = _fallback_reply(message, tool_context)
        
#         # Sauvegarder quand même le fallback dans l'historique
#         CHAT_MEMORY[session_id].append({
#             "role": "assistant",
#             "content": reply
#         })

#     # ------------------------------------------------------------------------
#     # 4) Retour du contrat attendu
#     # ------------------------------------------------------------------------
#     return {
#         "reply": reply,
#         "tools_used": tools_used,
#         "sources": sources
#     }