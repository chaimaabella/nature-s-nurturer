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
MCP_URL = os.getenv("MCP_URL", "http://localhost:9001")
MCP_EXECUTE_ENDPOINT = os.getenv("MCP_EXECUTE_ENDPOINT", "/execute")
MCP_TIMEOUT = int(os.getenv("MCP_TIMEOUT", "30"))

# OLLAMA
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "60"))


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
        "sansevieria", "zamioculcas", "yucca", "dracaena"
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
        try:
            mcp_res = _mcp_execute(
                "fetch_plant_sources",
                {"query": plant, "limit": 2}
            )

            if mcp_res.get("status") == "success":
                tools_used.append(mcp_res.get("tool", "fetch_plant_sources"))

                result = mcp_res.get("result") or {}
                tool_context = result.get("summary")

                for s in result.get("sources", []):
                    if s.get("url"):
                        sources.append({
                            "title": s.get("source_name") or s.get("title") or plant,
                            "url": s["url"]
                        })
            else:
                tools_used.append("fetch_plant_sources_failed")

        except Exception:
            tools_used.append("fetch_plant_sources_failed")

    # ------------------------------------------------------------------------
    # 2) Gestion de l'historique de conversation
    # ------------------------------------------------------------------------
    
    # Initialisation mémoire session si première fois
    if session_id not in CHAT_MEMORY:
        CHAT_MEMORY[session_id] = [
            {
                "role": "system",
                "content": (
                    "Tu es Floria, assistante experte en entretien des plantes. "
                    "Réponds de façon naturelle, cohérente avec l'historique. "
                    "Évite de reposer des questions déjà répondues. "
                    "Ton : concis, posé, orienté solution."
                )
            }
        ]

    # Injection du contexte MCP si disponible (avant le message user)
    if tool_context:
        CHAT_MEMORY[session_id].append({
            "role": "system",
            "content": f"Contexte fiable (sources vérifiées) : {tool_context}"
        })

    # Ajout du message utilisateur
    CHAT_MEMORY[session_id].append({
        "role": "user",
        "content": message
    })

    # ------------------------------------------------------------------------
    # 3) Appel LLM avec historique ou fallback
    # ------------------------------------------------------------------------
    try:
        reply = _call_ollama(CHAT_MEMORY[session_id])
        
        # Sauvegarde de la réponse dans l'historique
        CHAT_MEMORY[session_id].append({
            "role": "assistant",
            "content": reply
        })
        
    except Exception as e:
        # En cas d'erreur Ollama, utiliser le fallback
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