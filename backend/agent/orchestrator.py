# backend/agent/orchestrator.py

import os
import re
import requests
from typing import Optional, Dict, Any, List
import unicodedata


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
MCP_TIMEOUT = int(os.getenv("MCP_TIMEOUT", "600"))  # Augmenté à 60 secondes

# OLLAMA
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "1200"))  # Augmenté à 120 secondes


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


def normaliser(chaine):

    chaine = unicodedata.normalize('NFD', chaine)

    chaine = chaine.encode('ascii', 'ignore').decode('utf-8')

    chaine = re.sub(r'[^a-zA-Z0-9\s]', '', chaine)

    return chaine.lower().split()

def _extract_plant(message: str) -> Optional[str]:
    """
    Extraction simple du nom de plante depuis le message utilisateur.
    """
    msg = normaliser(message)

    known = {
  "a": [
    {"nom_vernaculaire":"acanthe","nom_latin":"acanthus"},
    {"nom_vernaculaire":"agapanthe","nom_latin":"agapanthus"},
    {"nom_vernaculaire":"agave","nom_latin":"agave"},
    {"nom_vernaculaire":"ajania","nom_latin":"ajania"},
    {"nom_vernaculaire":"albizia","nom_latin":"albizia"},
    {"nom_vernaculaire":"aloes","nom_latin":"aloe"},
    {"nom_vernaculaire":"alysse","nom_latin":"alyssum"},
    {"nom_vernaculaire":"amarante","nom_latin":"amaranthus"},
    {"nom_vernaculaire":"amaryllis","nom_latin":"amaryllis"},
    {"nom_vernaculaire":"ambroisie","nom_latin":"ambrosia"},
    {"nom_vernaculaire":"amelanchier","nom_latin":"amelanchier"},
    {"nom_vernaculaire":"ananas","nom_latin":"ananas"},
    {"nom_vernaculaire":"ancolie","nom_latin":"aquilegia"},
    {"nom_vernaculaire":"arachide","nom_latin":"arachis"},
    {"nom_vernaculaire":"armoise","nom_latin":"artemisia"},
    {"nom_vernaculaire":"arnica","nom_latin":"arnica"},
    {"nom_vernaculaire":"arum","nom_latin":"arum"},
    {"nom_vernaculaire":"asclepiade","nom_latin":"asclepias"},
    {"nom_vernaculaire":"aster","nom_latin":"aster"},
    {"nom_vernaculaire":"astragalus","nom_latin":"astragalus"},
    {"nom_vernaculaire":"aubepine","nom_latin":"crataegus"},
    {"nom_vernaculaire":"aulne","nom_latin":"alnus"},
    {"nom_vernaculaire":"averrhoa","nom_latin":"averrhoa"},
    {"nom_vernaculaire":"azalee","nom_latin":"rhododendron"}
  ],
  "b": [
    {"nom_vernaculaire":"bambou","nom_latin":"bambusa"},
    {"nom_vernaculaire":"bananier","nom_latin":"musa"},
    {"nom_vernaculaire":"baobab","nom_latin":"adansonia"},
    {"nom_vernaculaire":"belle de nuit","nom_latin":"mirabilis"},
    {"nom_vernaculaire":"berberis","nom_latin":"berberis"},
    {"nom_vernaculaire":"bignone","nom_latin":"campsis"},
    {"nom_vernaculaire":"bougainvillier","nom_latin":"bougainvillea"},
    {"nom_vernaculaire":"bouleau","nom_latin":"betula"},
    {"nom_vernaculaire":"bourrache","nom_latin":"borago"},
    {"nom_vernaculaire":"browallia","nom_latin":"browallia"},
    {"nom_vernaculaire":"buis","nom_latin":"buxus"}
  ],
  "c": [
    {"nom_vernaculaire":"callune","nom_latin":"calluna"},
    {"nom_vernaculaire":"calypso","nom_latin":"calypso"},
    {"nom_vernaculaire":"campanule","nom_latin":"campanula"},
    {"nom_vernaculaire":"capucine","nom_latin":"tropaeolum"},
    {"nom_vernaculaire":"carline","nom_latin":"carlina"},
    {"nom_vernaculaire":"casse","nom_latin":"cassia"},
    {"nom_vernaculaire":"catalpa","nom_latin":"catalpa"},
    {"nom_vernaculaire":"cercis","nom_latin":"cercis"},
    {"nom_vernaculaire":"chalef","nom_latin":"elaeagnus"},
    {"nom_vernaculaire":"chanvre","nom_latin":"cannabis"},
    {"nom_vernaculaire":"charme","nom_latin":"carpinus"},
    {"nom_vernaculaire":"chicoree","nom_latin":"cichorium"},
    {"nom_vernaculaire":"chrysantheme","nom_latin":"chrysanthemum"},
    {"nom_vernaculaire":"cirse","nom_latin":"cirsium"},
    {"nom_vernaculaire":"citrus","nom_latin":"citrus"},
    {"nom_vernaculaire":"cocotier","nom_latin":"cocos"},
    {"nom_vernaculaire":"cohosh bleu","nom_latin":"caulophyllum"},
    {"nom_vernaculaire":"colchique","nom_latin":"colchicum"},
    {"nom_vernaculaire":"consoude","nom_latin":"symphytum"},
    {"nom_vernaculaire":"cosmos","nom_latin":"cosmos"},
    {"nom_vernaculaire":"cotoneaster","nom_latin":"cotoneaster"},
    {"nom_vernaculaire":"courge","nom_latin":"cucurbita"},
    {"nom_vernaculaire":"crocus","nom_latin":"crocus"},
    {"nom_vernaculaire":"cumin","nom_latin":"cuminum"},
    {"nom_vernaculaire":"curcuma","nom_latin":"curcuma"},
    {"nom_vernaculaire":"cyclamen","nom_latin":"cyclamen"}
  ],
  "d": [
    {"nom_vernaculaire":"dahlia","nom_latin":"dahlia"},
    {"nom_vernaculaire":"dasylirion","nom_latin":"dasylirion"},
    {"nom_vernaculaire":"datura","nom_latin":"datura"},
    {"nom_vernaculaire":"dauphinelles","nom_latin":"delphinium"},
    {"nom_vernaculaire":"desmodium","nom_latin":"desmodium"},
    {"nom_vernaculaire":"dionee","nom_latin":"dionaea"},
    {"nom_vernaculaire":"diospyros","nom_latin":"diospyros"}
  ],
  "e": [
    {"nom_vernaculaire":"erable","nom_latin":"acer"},
    {"nom_vernaculaire":"erigeron","nom_latin":"erigeron"},
    {"nom_vernaculaire":"eucalyptus","nom_latin":"eucalyptus"},
    {"nom_vernaculaire":"euphorbe","nom_latin":"euphorbia"}
  ],
  "f": [
    {"nom_vernaculaire":"faux cypres","nom_latin":"chamaecyparis"},
    {"nom_vernaculaire":"ficus","nom_latin":"ficus"},
    {"nom_vernaculaire":"fittonia","nom_latin":"fittonia"},
    {"nom_vernaculaire":"forsythia","nom_latin":"forsythia"},
    {"nom_vernaculaire":"fraisier","nom_latin":"fragaria"},
    {"nom_vernaculaire":"fusain","nom_latin":"euonymus"},
    {"nom_vernaculaire":"fetuque","nom_latin":"festuca"}
  ],
  "g": [
    {"nom_vernaculaire":"galinsoga","nom_latin":"galinsoga"},
    {"nom_vernaculaire":"gaura","nom_latin":"gaura"},
    {"nom_vernaculaire":"gelsemium","nom_latin":"gelsemium"},
    {"nom_vernaculaire":"gentiane","nom_latin":"gentiana"},
    {"nom_vernaculaire":"genet","nom_latin":"genista"},
    {"nom_vernaculaire":"germandree","nom_latin":"teucrium"},
    {"nom_vernaculaire":"gingembre","nom_latin":"zingiber"},
    {"nom_vernaculaire":"gingembre sauvage","nom_latin":"hedychium"},
    {"nom_vernaculaire":"ginseng","nom_latin":"panax"},
    {"nom_vernaculaire":"glycine","nom_latin":"glycine"},
    {"nom_vernaculaire":"glycine (ornementale)","nom_latin":"wisteria"},
    {"nom_vernaculaire":"grenadier","nom_latin":"punica"},
    {"nom_vernaculaire":"grevillea","nom_latin":"grevillea"},
    {"nom_vernaculaire":"griffe de sorciere","nom_latin":"carpobrotus"},
    {"nom_vernaculaire":"groseillier","nom_latin":"ribes"},
    {"nom_vernaculaire":"gypsophile","nom_latin":"gypsophila"}
  ],
  "h": [
    {"nom_vernaculaire":"haworthia","nom_latin":"haworthia"},
    {"nom_vernaculaire":"hibiscus","nom_latin":"hibiscus"},
    {"nom_vernaculaire":"houx","nom_latin":"ilex"},
    {"nom_vernaculaire":"heliotrope","nom_latin":"heliotropium"}
  ],
  "i": [
    {"nom_vernaculaire":"if","nom_latin":"taxus"},
    {"nom_vernaculaire":"iris","nom_latin":"iris"}
  ],
  "j": [
    {"nom_vernaculaire":"jasmin","nom_latin":"jasminum"},
    {"nom_vernaculaire":"jasmin etoile","nom_latin":"trachelospermum"}
  ],
  "k": [
    {"nom_vernaculaire":"kiwi","nom_latin":"actinidia"},
    {"nom_vernaculaire":"kumquat","nom_latin":"fortunella"}
  ],
  "l": [
    {"nom_vernaculaire":"laser","nom_latin":"laser"},
    {"nom_vernaculaire":"laurier","nom_latin":"laurus"},
    {"nom_vernaculaire":"lavande","nom_latin":"lavandula"},
    {"nom_vernaculaire":"lens","nom_latin":"lens"},
    {"nom_vernaculaire":"lewisia","nom_latin":"lewisia"},
    {"nom_vernaculaire":"liatris","nom_latin":"liatris"},
    {"nom_vernaculaire":"lierre","nom_latin":"hedera"},
    {"nom_vernaculaire":"lilas","nom_latin":"syringa"},
    {"nom_vernaculaire":"lilas de californie","nom_latin":"ceanothus"},
    {"nom_vernaculaire":"lin","nom_latin":"linum"},
    {"nom_vernaculaire":"liquidambar","nom_latin":"liquidambar"},
    {"nom_vernaculaire":"litchi","nom_latin":"litchi"},
    {"nom_vernaculaire":"lotus","nom_latin":"nymphaea"},
    {"nom_vernaculaire":"lupin","nom_latin":"lupinus"},
    {"nom_vernaculaire":"luzerne","nom_latin":"medicago"},
    {"nom_vernaculaire":"lychnis","nom_latin":"lychnis"},
    {"nom_vernaculaire":"lycium","nom_latin":"lycium"},
    {"nom_vernaculaire":"lys","nom_latin":"lilium"}
  ],
    "m": [
    {"nom_vernaculaire":"macadamia","nom_latin":"macadamia"},
    {"nom_vernaculaire":"magnolia","nom_latin":"magnolia"},
    {"nom_vernaculaire":"marguerite","nom_latin":"leucanthemum"},
    {"nom_vernaculaire":"mauve","nom_latin":"malva"},
    {"nom_vernaculaire":"melissa","nom_latin":"melissa"},
    {"nom_vernaculaire":"menthe","nom_latin":"mentha"},
    {"nom_vernaculaire":"millepertuis","nom_latin":"hypericum"},
    {"nom_vernaculaire":"mimosa","nom_latin":"acacia"},
    {"nom_vernaculaire":"miscanthus","nom_latin":"miscanthus"},
    {"nom_vernaculaire":"myosotis","nom_latin":"myosotis"},
    {"nom_vernaculaire":"myrte","nom_latin":"myrtus"},
    {"nom_vernaculaire":"myrtillier","nom_latin":"vaccinium"}
  ],
  "n": [
    {"nom_vernaculaire":"narcisse","nom_latin":"narcissus"},
    {"nom_vernaculaire":"nigelle","nom_latin":"nigella"},
    {"nom_vernaculaire":"noisetier","nom_latin":"corylus"},
    {"nom_vernaculaire":"nothofagus","nom_latin":"nothofagus"},
    {"nom_vernaculaire":"noyer","nom_latin":"juglans"}
  ],
  "o": [
    {"nom_vernaculaire":"ophrys","nom_latin":"ophrys"},
    {"nom_vernaculaire":"orge","nom_latin":"hordeum"},
    {"nom_vernaculaire":"origan","nom_latin":"origanum"},
    {"nom_vernaculaire":"orme","nom_latin":"ulmus"},
    {"nom_vernaculaire":"ornithogale","nom_latin":"ornithogalum"},
    {"nom_vernaculaire":"oseille","nom_latin":"rumex"},
    {"nom_vernaculaire":"osmanthe","nom_latin":"osmanthus"}
  ],
  "p": [
    {"nom_vernaculaire":"papyrus","nom_latin":"cyperus"},
    {"nom_vernaculaire":"passiflore","nom_latin":"passiflora"},
    {"nom_vernaculaire":"pastel","nom_latin":"isatis"},
    {"nom_vernaculaire":"pavot","nom_latin":"papaver"},
    {"nom_vernaculaire":"persea","nom_latin":"persea"},
    {"nom_vernaculaire":"pilea","nom_latin":"pilea"},
    {"nom_vernaculaire":"piment","nom_latin":"capsicum"},
    {"nom_vernaculaire":"pin","nom_latin":"pinus"},
    {"nom_vernaculaire":"pissenlit","nom_latin":"taraxacum"},
    {"nom_vernaculaire":"pivoine","nom_latin":"paeonia"},
    {"nom_vernaculaire":"platane","nom_latin":"platanus"},
    {"nom_vernaculaire":"poirier","nom_latin":"pyrus"},
    {"nom_vernaculaire":"pommier","nom_latin":"malus"},
    {"nom_vernaculaire":"primevere","nom_latin":"primula"},
    {"nom_vernaculaire":"prunus","nom_latin":"prunus"},
    {"nom_vernaculaire":"pterocaryer","nom_latin":"pterocarya"}
  ],
  "r": [
    {"nom_vernaculaire":"radis","nom_latin":"raphanus"},
    {"nom_vernaculaire":"raiponce","nom_latin":"phyteuma"},
    {"nom_vernaculaire":"renoncule","nom_latin":"ranunculus"},
    {"nom_vernaculaire":"rhodiola","nom_latin":"rhodiola"},
    {"nom_vernaculaire":"rhubarbe","nom_latin":"rheum"},
    {"nom_vernaculaire":"romarin","nom_latin":"rosmarinus"},
    {"nom_vernaculaire":"ronce","nom_latin":"rubus"},
    {"nom_vernaculaire":"rosier","nom_latin":"rosa"}
  ],
  "s": [
    {"nom_vernaculaire":"sagine","nom_latin":"sagina"},
    {"nom_vernaculaire":"sagittaire","nom_latin":"sagittaria"},
    {"nom_vernaculaire":"salicorne","nom_latin":"salicornia"},
    {"nom_vernaculaire":"salsifis","nom_latin":"tragopogon"},
    {"nom_vernaculaire":"sapin","nom_latin":"abies"},
    {"nom_vernaculaire":"sarriette","nom_latin":"satureja"},
    {"nom_vernaculaire":"sedum","nom_latin":"sedum"},
    {"nom_vernaculaire":"sensitive","nom_latin":"mimosa"},
    {"nom_vernaculaire":"souci","nom_latin":"calendula"},
    {"nom_vernaculaire":"stevia","nom_latin":"stevia"},
    {"nom_vernaculaire":"sumac","nom_latin":"rhus"},
    {"nom_vernaculaire":"sureau","nom_latin":"sambucus"},
    {"nom_vernaculaire":"senecon","nom_latin":"senecio"}
  ],
  "t": [
    {"nom_vernaculaire":"tabac","nom_latin":"nicotiana"},
    {"nom_vernaculaire":"tamaris","nom_latin":"tamarix"},
    {"nom_vernaculaire":"thunbergia","nom_latin":"thunbergia"},
    {"nom_vernaculaire":"thuya","nom_latin":"thuja"},
    {"nom_vernaculaire":"thym","nom_latin":"thymus"},
    {"nom_vernaculaire":"tillandsia","nom_latin":"tillandsia"},
    {"nom_vernaculaire":"tilleul","nom_latin":"tilia"},
    {"nom_vernaculaire":"tournesol","nom_latin":"helianthus"},
    {"nom_vernaculaire":"trachycarpus","nom_latin":"trachycarpus"},
    {"nom_vernaculaire":"trille","nom_latin":"trillium"},
    {"nom_vernaculaire":"tulipe","nom_latin":"tulipa"}
  ],
  "v": [
    {"nom_vernaculaire":"verveine","nom_latin":"verbena"},
    {"nom_vernaculaire":"victoria","nom_latin":"victoria"},
    {"nom_vernaculaire":"vigne vierge","nom_latin":"ampelopsis"},
    {"nom_vernaculaire":"violette","nom_latin":"viola"}
  ],
  "y": [
    {"nom_vernaculaire":"yucca","nom_latin":"yucca"}
  ],
  "z": [
    {"nom_vernaculaire":"zantedeschia","nom_latin":"zantedeschia"}
  ]
}

    for mot in msg:

        for k in known.get(mot[0], []):

            if mot == k["nom_vernaculaire"]:

                return k["nom_latin"].replace(" ", "-")

            elif mot == k["nom_latin"]:

                return k["nom_latin"].replace(" ", "-")

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
