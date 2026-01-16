# backend/agent/orchestrator.py

from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional, TypedDict

import requests


# ============================================================================
# Mémoire simple en RAM (MVP)
# - CHAT_MEMORY: historique messages (format Ollama)
# - SLOTS_MEMORY: infos collectées pour éviter les répétitions
# ============================================================================
CHAT_MEMORY: Dict[str, List[Dict[str, str]]] = {}
SLOTS_MEMORY: Dict[str, Dict[str, Any]] = {}


# ============================================================================
# CONFIGURATION (ENV VARS)
# ============================================================================
# MCP (dans ton cas, /execute est exposé par le même backend FastAPI)
MCP_URL = os.getenv("MCP_URL", "http://127.0.0.1:8000")
MCP_EXECUTE_ENDPOINT = os.getenv("MCP_EXECUTE_ENDPOINT", "/execute")
MCP_TIMEOUT = int(os.getenv("MCP_TIMEOUT", "30"))

# OLLAMA
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))


# ============================================================================
# Types
# ============================================================================
class SourceLink(TypedDict):
    title: str
    url: str


# ============================================================================
# Helpers : intents / greeting / slot extraction
# ============================================================================
def _is_greeting(message: str) -> bool:
    msg = (message or "").strip().lower()
    if not msg:
        return False
    greetings = ("salut", "bonjour", "bonsoir", "hello", "coucou", "yo", "hey")
    return msg == msg.split()[0] and msg in greetings or msg.startswith(greetings)


def _looks_like_plant_question(message: str) -> bool:
    """
    Détecte si le message parle de plantes, même sans nom explicite.
    """
    msg = (message or "").lower()
    keywords = [
        "plante", "feuille", "feuilles", "arros", "rempot", "terreau", "substrat",
        "lumiere", "lumière", "exposition", "tache", "taches", "jauni", "jaun",
        "brun", "molle", "pourri", "pourrit", "racine", "parasite", "cochenille",
        "puceron", "thrips", "champignon", "moisi",
    ]
    return any(k in msg for k in keywords)


def _detect_intent(message: str) -> str:
    msg = (message or "").lower()

    symptom_words = [
        "jaunit", "jaunissent", "jauni", "jaune",
        "tache", "taches",
        "molle", "molles",
        "pourrit", "pourri", "pourriture",
        "brune", "brunes",
        "tombe", "chute",
        "sec", "sèche", "seche",
        "racines",
        "moisi", "champignon",
        "parasite", "insecte",
    ]
    if any(w in msg for w in symptom_words):
        return "diagnostic"

    if any(k in msg for k in ["c'est quoi", "quelle plante", "identifier", "identification"]):
        return "identification"

    return "entretien"


def _extract_plant(message: str) -> Optional[str]:
    """
    Extraction simple du nom de plante.
    """
    msg = (message or "").lower()

    known = [
        "monstera", "pothos", "cactus", "ficus",
        "orchidée", "orchidee", "succulente",
        "aloe", "aloé", "calathea", "philodendron",
        "sansevieria", "zamioculcas", "yucca", "dracaena",
        "tournesol", "basilic", "tomate", "rose", "lavande", "fougère", "fougere",
    ]
    for k in known:
        if k in msg:
            return k

    # pattern "mon/ma/mes X"
    m = re.search(r"\b(mon|ma|mes)\s+([a-zàâçéèêëîïôûùüÿñæœ-]{3,})\b", msg)
    if m:
        candidate = m.group(2)
        if candidate not in {"plante", "feuille", "feuilles", "pot", "terreau", "arrosage"}:
            return candidate

    return None


def _extract_slots(message: str) -> Dict[str, Any]:
    """
    Récupère quelques infos utiles dans le message (MVP).
    """
    msg = (message or "").lower()
    slots: Dict[str, Any] = {}

    # exposition
    if "lumière directe" in msg or "lumiere directe" in msg:
        slots["exposition"] = "directe"
    elif "lumière indirecte" in msg or "lumiere indirecte" in msg:
        slots["exposition"] = "indirecte"
    elif "ombre" in msg:
        slots["exposition"] = "ombre"

    # arrosage : "1 fois par semaine", "2x/semaine", "tous les 3 jours"
    m = re.search(r"\b(\d+)\s*(x|fois)\s*(/|par)\s*(semaine|mois|jour|jours)\b", msg)
    if m:
        slots["arrosage"] = m.group(0)

    m2 = re.search(r"\btous\s+les\s+(\d+)\s+(jour|jours|semaine|semaines)\b", msg)
    if m2:
        slots["arrosage"] = m2.group(0)

    if "trop arros" in msg:
        slots["arrosage_note"] = "trop"
    if "pas assez arros" in msg:
        slots["arrosage_note"] = "pas assez"

    # symptômes (liste courte)
    symptoms = []
    candidates = [
        "feuilles jaunes", "feuilles brunes", "taches", "feuilles molles",
        "chute de feuilles", "pourriture", "moisi", "parasites",
    ]
    for s in candidates:
        if s in msg:
            symptoms.append(s)
    if symptoms:
        slots["symptomes"] = symptoms

    return slots


def _build_missing_questions(intent: str, slots: Dict[str, Any]) -> List[str]:
    """
    Questions ciblées, max 3, uniquement si nécessaire.
    """
    questions: List[str] = []

    # plante est la plus critique (si pas connue)
    if not slots.get("plant"):
        questions.append("Quelle est la plante (nom) ? Si tu ne sais pas, une photo aiderait.")

    if intent == "diagnostic":
        if not slots.get("exposition"):
            questions.append("Elle est en lumière directe, indirecte ou plutôt à l’ombre ?")
        if not slots.get("arrosage"):
            questions.append("À quelle fréquence arroses-tu (ex: 1x/semaine) et le pot a-t-il un trou de drainage ?")

    elif intent == "entretien":
        if not slots.get("exposition"):
            questions.append("Elle est en lumière directe ou indirecte ?")
        if not slots.get("arrosage"):
            questions.append("Tu l’arroses à quelle fréquence ?")

    elif intent == "identification":
        # on évite de spam, seulement si pas de plante
        if not slots.get("plant"):
            questions.append("Tu peux décrire les feuilles (forme, taille) et la tige, ou envoyer une photo ?")

    return questions[:3]


# ============================================================================
# MCP CALL
# ============================================================================
def _mcp_execute(tool: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{MCP_URL}{MCP_EXECUTE_ENDPOINT}"
    payload = {"tool": tool, "arguments": arguments}

    resp = requests.post(url, json=payload, timeout=MCP_TIMEOUT)
    if resp.status_code != 200:
        raise RuntimeError(f"MCP error {resp.status_code}: {resp.text}")

    return resp.json()


def _unwrap_mcp_result(mcp_res: Dict[str, Any]) -> Dict[str, Any]:
    """
    Gère les retours imbrqués : result.result
    """
    result = mcp_res.get("result") or {}
    if isinstance(result, dict) and "result" in result and isinstance(result.get("result"), dict):
        result = result["result"]
    return result if isinstance(result, dict) else {}


# ============================================================================
# OLLAMA CALL
# ============================================================================
def _call_ollama(messages: List[Dict[str, str]], model: str = OLLAMA_MODEL) -> str:
    payload = {"model": model, "messages": messages, "stream": False}
    r = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    return (data.get("message", {}).get("content") or "").strip()


# ============================================================================
# System prompt (anti-répétition + priorité aux sources)
# ============================================================================
SYSTEM_PROMPT = (
    "Tu es FlorIA, assistant spécialisé plantes.\n"
    "Règles strictes:\n"
    "- Réponds d’abord à la question posée.\n"
    "- Ne répète pas un questionnaire à chaque message.\n"
    "- Pose des questions UNIQUEMENT si nécessaire, max 3, et seulement sur les infos manquantes.\n"
    "- Si l'utilisateur dit juste bonjour, réponds simplement.\n"
    "- Si des extraits de sources sont fournis, base-toi dessus en priorité.\n"
    "- Si l’info n’est pas dans les sources, dis-le et propose une solution prudente.\n"
    "Style: clair, actionnable, listes courtes.\n"
)


# ============================================================================
# MAIN
# ============================================================================
def handle_message(message: str, session_id: str) -> Dict[str, Any]:
    message = message or ""
    intent = _detect_intent(message)

    tools_used: List[str] = []
    sources: List[SourceLink] = []
    tool_summary: Optional[str] = None

    # init session memory
    if session_id not in CHAT_MEMORY:
        CHAT_MEMORY[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    if session_id not in SLOTS_MEMORY:
        SLOTS_MEMORY[session_id] = {}

    # update slots from message
    slots = SLOTS_MEMORY[session_id]
    extracted = _extract_slots(message)
    for k, v in extracted.items():
        slots[k] = v

    plant = _extract_plant(message)
    if plant:
        slots["plant"] = plant

    # 1) Greeting simple -> réponse courte
    if _is_greeting(message) and not _looks_like_plant_question(message):
        reply = "Bonjour. Dis-moi quelle plante tu as et ce que tu veux (entretien ou problème), et je t’aide."
        CHAT_MEMORY[session_id].append({"role": "user", "content": message})
        CHAT_MEMORY[session_id].append({"role": "assistant", "content": reply})
        return {"reply": reply, "tools_used": tools_used, "sources": sources}

    # 2) Décider si on scrape
    # - on scrape si on connaît la plante et que ça ressemble à une question plante
    # - ou si intent=diagnostic (souvent besoin d’info)
    should_scrape = bool(slots.get("plant")) and (_looks_like_plant_question(message) or intent == "diagnostic")

    if should_scrape:
        try:
            mcp_res = _mcp_execute("fetch_plant_sources", {"query": slots["plant"], "limit": 2})
            if mcp_res.get("status") == "success":
                tools_used.append(mcp_res.get("tool", "fetch_plant_sources"))
                result = _unwrap_mcp_result(mcp_res)

                tool_summary = result.get("summary")
                for s in (result.get("sources") or []):
                    url = s.get("url")
                    if url:
                        sources.append(
                            {
                                "title": s.get("source_name") or s.get("title") or str(slots["plant"]),
                                "url": url,
                            }
                        )
            else:
                tools_used.append("fetch_plant_sources_failed")
        except Exception:
            tools_used.append("fetch_plant_sources_failed")

    # 3) Contexte sources en SYSTEM (court)
    if tool_summary:
        short_context = tool_summary[:1000] + "…" if len(tool_summary) > 1000 else tool_summary
        CHAT_MEMORY[session_id].append(
            {
                "role": "system",
                "content": (
                    "EXTRAITS DE SOURCES FIABLES (à utiliser en priorité). "
                    "Si une info n’est pas dans ces extraits, dis: 'Je ne l’ai pas trouvé dans les sources'.\n\n"
                    f"{short_context}"
                ),
            }
        )

    # 4) Etat slots connus (évite répétition) - court
    state_parts = []
    if slots.get("plant"):
        state_parts.append(f"Plante={slots['plant']}")
    if slots.get("exposition"):
        state_parts.append(f"Exposition={slots['exposition']}")
    if slots.get("arrosage"):
        state_parts.append(f"Arrosage={slots['arrosage']}")
    if slots.get("symptomes"):
        state_parts.append("Symptomes=" + ", ".join(slots["symptomes"]))

    if state_parts:
        CHAT_MEMORY[session_id].append(
            {"role": "system", "content": "INFOS CONNUES (ne pas redemander): " + " | ".join(state_parts)}
        )

    # 5) user message
    CHAT_MEMORY[session_id].append({"role": "user", "content": message})

    # 6) questions manquantes (max 3)
    missing_questions = _build_missing_questions(intent=intent, slots=slots)

    # 7) call LLM
    try:
        reply = _call_ollama(CHAT_MEMORY[session_id])

        if missing_questions:
            reply = reply.rstrip() + "\n\nPour affiner:\n" + "\n".join(f"- {q}" for q in missing_questions)

        CHAT_MEMORY[session_id].append({"role": "assistant", "content": reply})
    except Exception:
        base = "Je peux t’aider, mais il me manque quelques infos."
        if missing_questions:
            base += "\n\nDis-moi:\n" + "\n".join(f"- {q}" for q in missing_questions)
        reply = base
        CHAT_MEMORY[session_id].append({"role": "assistant", "content": reply})

    return {"reply": reply, "tools_used": tools_used, "sources": sources}
