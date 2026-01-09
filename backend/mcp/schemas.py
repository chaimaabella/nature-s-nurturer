# mcp/schemas.py

from pydantic import BaseModel
from typing import Dict, Any

class ToolRequest(BaseModel):
    """
    Schéma pour envoyer un appel de l'IA au MCP.
    """
    tool: str  # nom du tool à exécuter
    arguments: Dict[str, Any] = {}  # arguments du tool (facultatif)

class ToolResponse(BaseModel):
    """
    Schéma pour la réponse du MCP vers l'IA.
    """
    status: str  # "success" ou "error"
    tool: str  # nom du tool exécuté
    result: Any = None  # résultat renvoyé par le tool
    message: str = ""  # message optionnel (erreur ou info)


# À quoi sert ce fichier ?

# ToolRequest : décrit ce que l’IA envoie
# Exemple JSON envoyé par l’IA :

# {
#   "tool": "scrape_plants",
#   "arguments": {
#     "site": "https://www.conservation-nature.fr/plantes/",
#     "limit": 3
#   }
# }

# ToolResponse : décrit ce que renvoie le MCP
# Exemple JSON renvoyé par le MCP :

# {
#   "status": "success",
#   "tool": "scrape_plants",
#   "result": [
#     {"title": "Plante 1", "url": "...", "content": "..."},
#     {"title": "Plante 2", "url": "...", "content": "..."}
#   ],
#   "message": ""
# }