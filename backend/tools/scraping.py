# tools/scraping.py

import requests
from bs4 import BeautifulSoup
from typing import List, Dict


def scrape_plants(site: str, limit: int = 5) -> List[Dict[str, str]]:
    """
    Tool MCP : scrape des pages de plantes depuis un site statique.

    Args:
        site (str): URL du site à scraper
        limit (int): nombre maximum de pages/plantes à récupérer

    Returns:
        List[Dict]: liste de plantes avec titre + description
    """

    response = requests.get(site, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    results = []

    # On récupère les liens présents sur la page
    links = soup.find_all("a", href=True)

    for link in links:
        if len(results) >= limit:
            break

        href = link["href"]
        title = link.get_text(strip=True)

        # On ignore les liens vides ou trop courts
        if not title or len(title) < 3:
            continue

        # Gestion des liens relatifs
        if href.startswith("/"):
            href = site.rstrip("/") + href

        # On tente de scraper la page liée
        try:
            page = requests.get(href, timeout=10)
            page.raise_for_status()

            page_soup = BeautifulSoup(page.text, "html.parser")
            text = page_soup.get_text(separator=" ", strip=True)

            # On limite la taille du texte pour l’IA
            text = text[:1500]

            results.append({
                "title": title,
                "url": href,
                "content": text
            })

        except Exception:
            # Si une page échoue, on continue
            continue

    return results


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
# demande simplement : “Utilise le tool scrape_plants”

# 📌 Le tool :
# exécute
# contrôle
# retourne les données