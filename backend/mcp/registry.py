# mcp/registry.py

# Import des tools existants
from tools.scraping import scrape_plants

# Registry : nom du tool → fonction Python
TOOLS = {
    "scrape_plants": scrape_plants,
    # Ajouter ici d'autres tools si besoin
}

def list_tools():
    """
    Retourne la liste des tools disponibles
    """
    return list(TOOLS.keys())


# 🧠 À quoi ser ce fichier ?

# C’est la liste des tools autorisés
# Il empêche l’IA d’exécuter n’importe quoi
# Il relie le nom du tool (chaîne) à la fonction Python correspondante
# Le MCP va s’y référer pour savoir ce qu’il peut exécuter

# Concrètement :
# Si l’IA demande "scrape_plants", le MCP regarde dans ce registre, trouve la fonction scrape_plants et l’exécute.