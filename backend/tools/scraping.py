# tools/scraping.py

from __future__ import annotations

import re
import unicodedata
from typing import Dict, List, Optional, TypedDict

import requests
from bs4 import BeautifulSoup


# ============================================================================
# SOURCES AUTORISÉES (whitelist)
# - patterns: liste de formats d'URL à tester (dans l'ordre)
# ============================================================================
SOURCES = [
    {
        "name": "Conservation Nature",
        "patterns": [
            "https://www.conservation-nature.fr/plantes/{slug}",
            # fallback éventuel si le site a d'autres routes (garde une seule whitelist)
        ],
    },
    {
        "name": "Nature & Jardin",
        "patterns": [
            # Le site a souvent des structures variables ; on teste plusieurs chemins "safe"
            "http://nature.jardin.free.fr/{slug}.html",
            "http://nature.jardin.free.fr/{slug}/index.html",
            "http://nature.jardin.free.fr/{slug}/",
            "http://nature.jardin.free.fr/{slug}",
        ],
    },
]


# ============================================================================
# Types
# ============================================================================
class SourceLink(TypedDict):
    title: str
    url: str
    source_name: str


class FetchPlantSourcesResult(TypedDict):
    query: str
    normalized_query: str
    summary: Optional[str]
    sources: List[SourceLink]


# ============================================================================
# Helpers
# ============================================================================
def _normalize_query(q: str) -> str:
    """
    Normalise une requête "plante" pour l'URL :
    - trim, lower
    - retire accents
    - garde lettres/chiffres/espaces/tirets
    - espaces -> tirets
    """
    q = (q or "").strip().lower()
    if not q:
        return ""

    q = unicodedata.normalize("NFKD", q)
    q = "".join(c for c in q if not unicodedata.combining(c))  # remove accents
    q = re.sub(r"[^a-z0-9\s-]", " ", q)
    q = re.sub(r"\s+", " ", q).strip()
    q = q.replace(" ", "-")
    q = re.sub(r"-{2,}", "-", q)
    return q


def _candidate_slugs(normalized_query: str) -> List[str]:
    """
    Génère des slugs candidats.
    Exemple:
      "monstera-deliciosa" -> ["monstera-deliciosa", "monstera"]
      "ficus" -> ["ficus"]
    """
    if not normalized_query:
        return []
    parts = [p for p in normalized_query.split("-") if p]
    if len(parts) >= 2:
        return [normalized_query, parts[0]]
    return [normalized_query]


def _clean_dom(soup: BeautifulSoup) -> None:
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()


def _pick_best_container(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Essaie de sélectionner une zone "contenu" avant fallback global,
    pour éviter menus/sidebars.
    """
    selectors = [
        "main",
        "article",
        "#content",
        ".content",
        "#page",
        ".page",
    ]
    for sel in selectors:
        node = soup.select_one(sel)
        if node:
            return node  # type: ignore[return-value]
    return soup


def _extract_text(soup: BeautifulSoup, max_chars: int = 1800) -> str:
    _clean_dom(soup)
    container = _pick_best_container(soup)
    text = container.get_text(separator=" ", strip=True)
    text = " ".join(text.split())
    if len(text) > max_chars:
        text = text[:max_chars].rstrip() + "…"
    return text


def _http_get(url: str, headers: Dict[str, str], timeout: int = 12) -> Optional[str]:
    """
    GET robuste: renvoie le HTML (str) ou None.
    """
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        if r.status_code != 200:
            return None
        # Certains sites servent en ISO-8859-1; requests le gère souvent, sinon fallback
        r.encoding = r.encoding or "utf-8"
        return r.text
    except requests.RequestException:
        return None


# ============================================================================
# TOOL MCP : fetch_plant_sources
# ============================================================================
def fetch_plant_sources(query: str, limit: int = 2) -> FetchPlantSourcesResult:
    """
    Tool MCP : récupère des informations botaniques (texte + sources)
    à partir d’un nom de plante, depuis une whitelist de sites.

    Retour:
    - summary = concat d'extraits structurés "Source + URL + extrait"
    - sources = liens réellement testés et OK
    """
    normalized_query = _normalize_query(query)

    if not normalized_query:
        return {
            "query": query,
            "normalized_query": normalized_query,
            "summary": None,
            "sources": [],
        }

    max_sources = max(1, int(limit))
    results: List[SourceLink] = []
    summaries: List[str] = []

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        )
    }

    slug_candidates = _candidate_slugs(normalized_query)

    for source in SOURCES:
        if len(results) >= max_sources:
            break

        # On teste plusieurs slugs + plusieurs patterns pour maximiser la réussite
        for slug in slug_candidates:
            if len(results) >= max_sources:
                break

            for pattern in source["patterns"]:
                if len(results) >= max_sources:
                    break

                url = pattern.format(slug=slug)

                html = _http_get(url, headers=headers, timeout=12)
                if not html:
                    continue

                soup = BeautifulSoup(html, "html.parser")
                text = _extract_text(soup, max_chars=1800)

                # Écarte pages trop vides / non pertinentes
                if len(text) < 250:
                    continue

                # Évite doublons si plusieurs patterns mènent au même contenu
                if any(r["url"] == url for r in results):
                    continue

                summaries.append(
                    f"SOURCE: {source['name']}\nURL: {url}\nEXTRAIT: {text}"
                )

                results.append(
                    {
                        "title": source["name"],
                        "url": url,
                        "source_name": source["name"],
                    }
                )

                # dès qu'on a trouvé 1 page valide pour cette source, on passe à la suivante
                break

    summary = "\n\n---\n\n".join(summaries) if summaries else None

    return {
        "query": query,
        "normalized_query": normalized_query,
        "summary": summary,
        "sources": results,
    }
