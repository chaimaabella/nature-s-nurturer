# tools/scraping.py

import re
import requests
from bs4 import BeautifulSoup
from typing import Dict


# ============================================================================
# SOURCES AUTORISÉES (whitelist)
# ============================================================================

SOURCES = [
    {
        "name": "Conservation Nature",
        "base_url": "https://www.conservation-nature.fr/types/"
    },

    {
        "name": "Conservation Nature",
        "base_url": "https://www.conservation-nature.fr/plantes/"
    },

    # {
    #     "name": "Nature & Jardin",
    #     "base_url": "http://nature.jardin.free.fr"
    # }
]


# ============================================================================
# HELPERS : nettoyage HTML + extraction du contenu pertinent
# ============================================================================

def _clean_soup(soup: BeautifulSoup) -> None:
    """Supprime les éléments HTML qui polluent le texte (menus, scripts, etc.)."""
    for tag in soup(["script", "style", "noscript", "svg", "canvas", "iframe"]):
        tag.decompose()

    # Supprime les zones de navigation / chrome de page
    for tag in soup.find_all(["header", "footer", "nav", "aside", "form"]):
        tag.decompose()


def _extract_main_text(soup: BeautifulSoup) -> str:
    """
    Tente d'extraire le contenu principal d'une page (main/article/containers usuels).
    Fallback : body complet.
    """
    candidates = [
        soup.find("main"),
        soup.find("article"),
        soup.find(id=re.compile(r"(content|contenu|main|page)", re.I)),
        soup.find(class_=re.compile(r"(content|contenu|entry|post|article|main)", re.I)),
    ]

    node = next((c for c in candidates if c is not None), None)
    if node is None:
        node = soup.body or soup

    text = node.get_text(separator="\n", strip=True)

    # Nettoyage texte (lignes vides et espaces)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def _keep_useful_lines(text: str, min_len: int = 30) -> str:
    """Retire les lignes trop courtes (souvent menus/duplicats) et compacte."""
    lines = [l.strip() for l in text.split("\n")]
    lines = [l for l in lines if len(l) >= min_len]
    compact = "\n".join(lines)
    compact = re.sub(r"\n{3,}", "\n\n", compact).strip()
    return compact


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
        - summary (texte nettoyé et pertinent)
        - sources (liste de liens)
    """

    results = []
    summaries = []

    # Normalisation légère de la query (évite espaces, accents bizarres, etc.)
    q = (query or "").strip().lower()
    if not q:
        return {"query": query, "summary": None, "sources": []}

    for source in SOURCES:
        if len(results) >= limit:
            break

        # Construction simple de l’URL à partir de la plante
        # (MVP : suppose que la page est accessible via base_url + query)
        url = source["base_url"].rstrip("/") + "/" + q

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Nettoyage + extraction du contenu principal
            _clean_soup(soup)
            text = _extract_main_text(soup)
            text = _keep_useful_lines(text)

            # Limite la taille pour l’IA (réduit tokens = réduit latence)
            text = text[:1500]

            if text:
                summaries.append(text)
                results.append({
                    "title": source["name"],
                    "url": url,
                    "source_name": source["name"]
                })

        except Exception:
            # Si un site échoue, on continue avec les autres
            continue

    # Résumé simple (MVP) : concaténation des extraits propres
    summary = "\n\n".join(summaries) if summaries else None

    return {
        "query": q,
        "summary": summary,
        "sources": results
    }


# 🧠 À quoi sert tools/scraping.py ?
#
# 👉 C’est un tool MCP
# 👉 Il fait une action concrète que l’IA ne peut pas faire seule
#
# Son rôle précis :
# - aller sur un site web statique
# - récupérer des pages de plantes
# - extraire du texte PERTINENT (sans menus/footer/scripts)
# - retourner un résultat structuré à l’agent IA
#
# 📌 L’IA :
# - ne scrape pas
# - ne connaît pas le HTML
# - demande simplement : “Utilise le tool fetch_plant_sources”
#
# 📌 Le tool :
# - exécute
# - contrôle
# - retourne les données
