# tools/scraping.py

import requests
from bs4 import BeautifulSoup
from typing import List, Dict


# ============================================================================
# SOURCES AUTORISÉES
# ============================================================================

SOURCES = [
    {
        "name": "Conservation Nature",
        "base_url": "https://www.conservation-nature.fr/plantes/"
    },
    {
        "name": "Nature & Jardin",
        "base_url": "http://nature.jardin.free.fr"
    }
]


# ============================================================================
# TOOL MCP : fetch_plant_sources
# ============================================================================

def fetch_plant_sources(query: str, limit: int = 2) -> Dict:
    """
    Tool MCP : récupère des informations botaniques fiables
    à partir de sites spécialisés, à partir d’un nom de plante.

    Args:
        query (str): nom de la plante (ex: "monstera")
        limit (int): nombre maximum de sources à retourner

    Returns:
        Dict contenant :
        - query
        - summary (texte résumé)
        - sources (liste de liens)
    """

    results = []
    summaries = []

    for source in SOURCES:
        if len(results) >= limit:
            break

        # Construction de l’URL à partir de la plante
        url = source["base_url"] + query

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extraction simple du texte de la page
            text = soup.get_text(separator=" ", strip=True)

            # On limite la taille pour l’IA
            text = text[:1500]

            summaries.append(text)

            results.append({
                "title": source["name"],
                "url": url,
                "source_name": source["name"]
            })

        except Exception:
            # Si un site échoue, on continue avec les autres
            continue

    # Résumé simple (MVP) : concaténation des extraits
    summary = "\n\n".join(summaries) if summaries else None

    return {
        "query": query,
        "summary": summary,
        "sources": results
    }

# 🧠 À quoi sert tools/scraping.py ?

# 👉 C’est un tool MCP
# 👉 Il fait une action concrète que l’IA ne peut pas faire seule

# Son rôle précis :
# aller sur un site web statique
# récupérer des pages de plantes
# extraire du texte propre
# retourner un résultat structuré à l’agent IA

# 📌 L’IA :
# ne scrape pas
# ne connaît pas le HTML
# demande simplement : “Utilise le tool fetch_plant_sources”

# 📌 Le tool :
# exécute
# contrôle
# retourne les données