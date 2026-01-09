# backend/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mcp.server import execute_tool, get_tools
from mcp.schemas import ToolRequest, ToolResponse

app = FastAPI(title="Backend MCP Connector")

# Autoriser le frontend à communiquer (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # pour dev, sinon mettre l'URL du front
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route pour vérifier la disponibilité des tools
@app.get("/tools")
def list_tools():
    return get_tools()

# Route pour exécuter un tool via le MCP
@app.post("/execute", response_model=ToolResponse)
def run_tool(request: ToolRequest):
    try:
        result = execute_tool(request)
        return ToolResponse(
            status="success",
            tool=request.tool,
            result=result
        )
    except HTTPException as e:
        # Erreurs renvoyées par le MCP
        return ToolResponse(
            status="error",
            tool=request.tool,
            message=e.detail
        )
    except Exception as e:
        # Autres erreurs
        return ToolResponse(
            status="error",
            tool=request.tool,
            message=str(e)
        )


# 🧠 À quoi sert ce fichier ?
# Sert de pont entre le frontend et le MCP
# Reçoit les requêtes de l’utilisateur (via le front)
# Transmet ces requêtes au MCP pour exécution des tools
# Retourne le résultat à l’utilisateur

# Concrètement :
# Front → Main.py → MCP → Tool → Résultat → Main.py → Front
