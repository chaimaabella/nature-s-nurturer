# mcp/server.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from mcp.registry import TOOLS, list_tools

app = FastAPI(title="MCP Server")

# Schéma pour recevoir les appels de l'IA
class ToolRequest(BaseModel):
    tool: str            # nom du tool à exécuter
    arguments: Dict[str, Any] = {}  # arguments du tool

# Route principale pour exécuter un tool
@app.post("/execute")
def execute_tool(request: ToolRequest):
    tool_name = request.tool
    args = request.arguments

    # Vérification si le tool existe dans le registre
    if tool_name not in TOOLS:
        raise HTTPException(status_code=400, detail=f"Tool '{tool_name}' non disponible. Outils disponibles : {list_tools()}")

    # Exécution du tool
    try:
        result = TOOLS[tool_name](**args)
        return {"status": "success", "tool": tool_name, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'exécution du tool : {str(e)}")

# Route pour lister tous les tools disponibles
@app.get("/tools")
def get_tools():
    return {"available_tools": list_tools()}


# 🧠 À quoi sert ce fichier ?

# C’est le cerveau du MCP
# Il reçoit une demande de l’agent IA (quel tool + quels arguments)
# Il vérifie si le tool est autorisé (via registry.py)
# Il exécute le tool et retourne le résultat
# Permet à l’IA de ne pas toucher au scraping directement

# Concrètement : l’IA dit "scrape_plants", le MCP s’assure que ce tool existe, l’exécute et renvoie le résultat.