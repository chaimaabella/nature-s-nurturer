# tools/scraping.py

import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from urllib.parse import quote, urljoin


# ============================================================================
# SOURCES AUTORISÉES (whitelist)
# ============================================================================

SOURCES = [
    {
        "name": "Conservation Nature",
        "type": "direct",  # URL directe
        "base_url": "https://www.conservation-nature.fr/plantes/",
        "search_pattern": "{base_url}{query}"
    },
    {
        "name": "Tela Botanica",
        "type": "search",  # Recherche avec paramètres
        "base_url": "https://www.tela-botanica.org",
        "search_url": "https://www.tela-botanica.org/bdtfx-nn-{query}",
        "search_fallback": "https://www.tela-botanica.org/eflore/?referentiel=bdtfx&recherche=étendue&masque={query}"
    },
    {
        "name": "Au Jardin Info",
        "type": "search",
        "base_url": "https://www.aujardin.info",
        "search_pattern": "https://www.aujardin.info/plantes/{query}.php"
    }
]


# ============================================================================
# HELPERS : nettoyage HTML + extraction du contenu pertinent
# ============================================================================

def _clean_soup(soup: BeautifulSoup) -> None:
    """Supprime les éléments HTML qui polluent le texte."""
    for tag in soup(["script", "style", "noscript", "svg", "canvas", "iframe"]):
        tag.decompose()

    for tag in soup.find_all(["header", "footer", "nav", "aside", "form", "button"]):
        tag.decompose()
    
    # Supprime les éléments de publicité et tracking
    for tag in soup.find_all(class_=re.compile(r"(ad|pub|tracking|social|share|cookie)", re.I)):
        tag.decompose()


def _extract_main_text(soup: BeautifulSoup) -> str:
    """
    Extraction intelligente du contenu principal.
    """
    candidates = [
        soup.find("main"),
        soup.find("article"),
        soup.find(id=re.compile(r"(content|contenu|main|page|article)", re.I)),
        soup.find(class_=re.compile(r"(content|contenu|entry|post|article|main)", re.I)),
        soup.find("div", class_=re.compile(r"(description|info|plant)", re.I))
    ]

    node = next((c for c in candidates if c is not None), None)
    if node is None:
        node = soup.body or soup

    text = node.get_text(separator="\n", strip=True)

    # Nettoyage texte
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def _extract_structured_info(soup: BeautifulSoup, text: str) -> str:
    """
    Extraction avancée : cherche des sections spécifiques sur les plantes.
    """
    # Cherche des sections clés
    sections_keywords = [
        "entretien", "arrosage", "exposition", "lumière", "température",
        "substrat", "terreau", "engrais", "rempotage", "taille",
        "multiplication", "maladies", "parasites", "toxicité"
    ]
    
    extracted_sections = []
    
    # Cherche des titres (h2, h3, strong) contenant ces mots-clés
    for heading in soup.find_all(["h2", "h3", "h4", "strong", "b"]):
        heading_text = heading.get_text(strip=True).lower()
        
        for keyword in sections_keywords:
            if keyword in heading_text:
                # Récupère le paragraphe suivant
                next_elem = heading.find_next(["p", "div", "ul"])
                if next_elem:
                    section_text = next_elem.get_text(separator=" ", strip=True)
                    if len(section_text) > 30:
                        extracted_sections.append(f"{heading.get_text(strip=True)}: {section_text}")
    
    if extracted_sections:
        return "\n".join(extracted_sections[:10])  # Max 10 sections
    
    return text


def _keep_useful_lines(text: str, min_len: int = 30, max_lines: int = 50) -> str:
    """
    Retire les lignes trop courtes et limite le nombre de lignes.
    """
    lines = [l.strip() for l in text.split("\n")]
    lines = [l for l in lines if len(l) >= min_len][:max_lines]
    compact = "\n".join(lines)
    compact = re.sub(r"\n{3,}", "\n\n", compact).strip()
    return compact


def _normalize_query(query: str) -> str:
    """
    Normalise la requête pour les URLs.
    """
    q = query.strip().lower()
    # Retire les accents pour les URLs
    replacements = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'â': 'a', 'ä': 'a',
        'ô': 'o', 'ö': 'o',
        'û': 'u', 'ù': 'u', 'ü': 'u',
        'ç': 'c', 'î': 'i', 'ï': 'i'
    }
    for old, new in replacements.items():
        q = q.replace(old, new)
    return q


def _try_scrape_url(url: str, source_name: str) -> Optional[Dict]:
    """
    Essaie de scraper une URL donnée.
    Retourne None si échec.
    """
    try:
        response = requests.get(
            url, 
            timeout=10,
            headers={'User-Agent': 'FlorIA-Bot/1.0 (Educational Project)'}
        )
        
        # Si 404 ou autre erreur, passer
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Nettoyage
        _clean_soup(soup)
        
        # Extraction structurée d'abord
        text = _extract_structured_info(soup, "")
        
        # Si pas de sections trouvées, extraction classique
        if not text or len(text) < 100:
            text = _extract_main_text(soup)
        
        text = _keep_useful_lines(text, max_lines=40)

        # Limite stricte pour Ollama
        text = text[:2000]

        if text and len(text) > 100:  # Au moins 100 caractères utiles
            return {
                "title": source_name,
                "url": url,
                "source_name": source_name,
                "content": text
            }

    except Exception as e:
        print(f"❌ Erreur scraping {url}: {e}")
        return None

    return None


# ============================================================================
# STRATÉGIES DE RECHERCHE PAR SOURCE
# ============================================================================

def _search_conservation_nature(query: str) -> List[str]:
    """URLs possibles pour Conservation Nature."""
    q = _normalize_query(query)
    return [
        f"https://www.conservation-nature.fr/plantes/{q}",
        f"https://www.conservation-nature.fr/plantes/genre-{q}",
    ]


def _search_tela_botanica(query: str) -> List[str]:
    """URLs possibles pour Tela Botanica."""
    q = _normalize_query(query)
    q_url = quote(query)
    return [
        f"https://www.tela-botanica.org/eflore/?referentiel=bdtfx&recherche=étendue&masque={q_url}",
        f"https://www.tela-botanica.org/bdtfx-nn-{q}",
    ]


def _search_aujardin(query: str) -> List[str]:
    """URLs possibles pour Au Jardin."""
    q = _normalize_query(query)
    return [
        f"https://www.aujardin.info/plantes/{q}.php",
        f"https://www.aujardin.info/recherche.php?q={quote(query)}",
    ]


# Mapping des sources vers leurs stratégies
SEARCH_STRATEGIES = {
    "Conservation Nature": _search_conservation_nature,
    "Tela Botanica": _search_tela_botanica,
    "Au Jardin Info": _search_aujardin,
}


# ============================================================================
# TOOL MCP : fetch_plant_sources
# ============================================================================

def fetch_plant_sources(query: str, limit: int = 3) -> Dict:
    """
    Tool MCP amélioré : recherche intelligente multi-sources.
    
    Args:
        query: nom de la plante
        limit: nombre maximum de sources
    
    Returns:
        Dict avec query, summary, sources
    """
    
    if not query or not query.strip():
        return {"query": query, "summary": None, "sources": []}

    results = []
    all_content = []

    print(f"🔍 Recherche pour : {query}")

    for source in SOURCES:
        if len(results) >= limit:
            break

        source_name = source["name"]
        strategy = SEARCH_STRATEGIES.get(source_name)
        
        if not strategy:
            continue

        # Obtenir les URLs à essayer pour cette source
        urls_to_try = strategy(query)
        
        # Essayer chaque URL jusqu'à ce qu'une fonctionne
        for url in urls_to_try:
            result = _try_scrape_url(url, source_name)
            
            if result:
                print(f"✅ Trouvé sur {source_name}: {url}")
                all_content.append(result["content"])
                results.append({
                    "title": result["title"],
                    "url": result["url"],
                    "source_name": result["source_name"]
                })
                break  # Passe à la source suivante
            else:
                print(f"⚠️  Échec: {url}")

    # Synthèse : combine les contenus trouvés
    summary = "\n\n---\n\n".join(all_content) if all_content else None

    # Limite finale stricte
    if summary and len(summary) > 2500:
        summary = summary[:2500] + "..."

    print(f"📊 Résultat: {len(results)} source(s) trouvée(s)")

    return {
        "query": query,
        "summary": summary,
        "sources": results
    }

# # tools/scraping.py

# import re
# import requests
# from bs4 import BeautifulSoup
# from typing import Dict


# # ============================================================================
# # SOURCES AUTORISÉES (whitelist)
# # ============================================================================

# SOURCES = [
#     {
#         "name": "Conservation Nature",
#         "base_url": "https://www.conservation-nature.fr/types/"
#     },

#     {
#         "name": "Conservation Nature",
#         "base_url": "https://www.conservation-nature.fr/plantes/"
#     },

#     # {
#     #     "name": "Nature & Jardin",
#     #     "base_url": "http://nature.jardin.free.fr"
#     # }
# ]


# # ============================================================================
# # HELPERS : nettoyage HTML + extraction du contenu pertinent
# # ============================================================================

# def _clean_soup(soup: BeautifulSoup) -> None:
#     """Supprime les éléments HTML qui polluent le texte (menus, scripts, etc.)."""
#     for tag in soup(["script", "style", "noscript", "svg", "canvas", "iframe"]):
#         tag.decompose()

#     # Supprime les zones de navigation / chrome de page
#     for tag in soup.find_all(["header", "footer", "nav", "aside", "form"]):
#         tag.decompose()


# def _extract_main_text(soup: BeautifulSoup) -> str:
#     """
#     Tente d'extraire le contenu principal d'une page (main/article/containers usuels).
#     Fallback : body complet.
#     """
#     candidates = [
#         soup.find("main"),
#         soup.find("article"),
#         soup.find(id=re.compile(r"(content|contenu|main|page)", re.I)),
#         soup.find(class_=re.compile(r"(content|contenu|entry|post|article|main)", re.I)),
#     ]

#     node = next((c for c in candidates if c is not None), None)
#     if node is None:
#         node = soup.body or soup

#     text = node.get_text(separator="\n", strip=True)

#     # Nettoyage texte (lignes vides et espaces)
#     text = re.sub(r"\n{3,}", "\n\n", text)
#     text = re.sub(r"[ \t]{2,}", " ", text)
#     return text.strip()


# def _keep_useful_lines(text: str, min_len: int = 30) -> str:
#     """Retire les lignes trop courtes (souvent menus/duplicats) et compacte."""
#     lines = [l.strip() for l in text.split("\n")]
#     lines = [l for l in lines if len(l) >= min_len]
#     compact = "\n".join(lines)
#     compact = re.sub(r"\n{3,}", "\n\n", compact).strip()
#     return compact


# # ============================================================================
# # TOOL MCP : fetch_plant_sources
# # ============================================================================

# def fetch_plant_sources(query: str, limit: int = 2) -> Dict:
#     """
#     Tool MCP : récupère des informations botaniques fiables
#     à partir de sites spécialisés, à partir d’un nom de plante.

#     Args:
#         query (str): nom de la plante (ex: "monstera")
#         limit (int): nombre maximum de sources à retourner

#     Returns:
#         Dict contenant :
#         - query
#         - summary (texte nettoyé et pertinent)
#         - sources (liste de liens)
#     """

#     results = []
#     summaries = []

#     # Normalisation légère de la query (évite espaces, accents bizarres, etc.)
#     q = (query or "").strip().lower()
#     if not q:
#         return {"query": query, "summary": None, "sources": []}

#     for source in SOURCES:
#         if len(results) >= limit:
#             break

#         # Construction simple de l’URL à partir de la plante
#         # (MVP : suppose que la page est accessible via base_url + query)
#         url = source["base_url"].rstrip("/") + "/" + q

#         try:
#             response = requests.get(url, timeout=10)
#             response.raise_for_status()

#             soup = BeautifulSoup(response.text, "html.parser")

#             # Nettoyage + extraction du contenu principal
#             _clean_soup(soup)
#             text = _extract_main_text(soup)
#             text = _keep_useful_lines(text)

#             # Limite la taille pour l’IA (réduit tokens = réduit latence)
#             text = text[:1500]

#             if text:
#                 summaries.append(text)
#                 results.append({
#                     "title": source["name"],
#                     "url": url,
#                     "source_name": source["name"]
#                 })

#         except Exception:
#             # Si un site échoue, on continue avec les autres
#             continue

#     # Résumé simple (MVP) : concaténation des extraits propres
#     summary = "\n\n".join(summaries) if summaries else None

#     return {
#         "query": q,
#         "summary": summary,
#         "sources": results
#     }


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
