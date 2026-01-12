# Flore

Assistant intelligent pour prendre soin de vos plantes.

## Démarrage

```bash
npm install
npm run dev
```

## Production

```bash
npm run build
npm run preview
```

# 🌱 Assistant Plantes IA

Un assistant conversationnel intelligent permettant d’aider les propriétaires de plantes à mieux comprendre, entretenir et préserver leurs végétaux grâce à un agent IA local et des outils de scraping spécialisés.

---

## 📋 Table des matières
- À propos
- Fonctionnalités
- Architecture
- Prérequis
- Installation
- Utilisation
- Structure du projet
- Technologies
- Roadmap
- Documentation
- Contribuer
- Licence

---

## 🌿 À propos

**Assistant Plantes IA** est un prototype d’agent conversationnel intelligent intégré à une application web.  
Il permet à un utilisateur de poser des questions en langage naturel sur l’entretien des plantes et d’obtenir des réponses enrichies par des données issues de sites botaniques spécialisés.

### Problème identifié
- ❌ Informations dispersées et parfois contradictoires
- ❌ Difficulté à trouver des conseils concrets et applicables
- ❌ Manque de contextualisation selon la plante ou le problème

### Notre approche
- ✅ Agent conversationnel local (LLM open-source)
- ✅ Données récupérées dynamiquement via scraping
- ✅ Séparation claire entre raisonnement (IA) et exécution (tools)
- ✅ Architecture modulaire et pédagogique

---

## ✨ Fonctionnalités

### MVP actuel
- 🤖 Chatbot en langage naturel
- 🌐 Scraping de sites botaniques sélectionnés
- 🧠 Agent IA capable de décider d’utiliser un tool
- 📚 Réponses enrichies avec contenu structuré
- 🔌 Architecture MCP simulée

### En développement / évolutions possibles
- 📸 Analyse d’images (diagnostic visuel)
- 📝 Formulaire guidé
- 💾 Historique des conversations
- 🌍 Multiples sources (PDF, APIs, bases de données)

---

## 🏗️ Architecture
┌─────────────┐
│ Frontend │ JavaScript / React
└──────┬──────┘
│ HTTP (REST)
▼
┌─────────────┐
│ Backend │ FastAPI
│ main.py │
│ │
│ ┌────────┐ │
│ │ Agent │ │ Ollama (LLM local)
│ │Orchest.│ │
│ └───┬────┘ │
└──────┼──────┘
│ Appel interne
▼
┌─────────────┐
│ MCP │ Model Context Protocol
│ server.py │
│ │
│ ┌─────────┐ │
│ │ Tools │ │ scraping.py
│ └─────────┘ │
└─────────────┘
│
▼
🌐 Sites web


### Flux de données
1. L’utilisateur pose une question dans le frontend
2. Le backend transmet la requête à l’agent IA
3. L’agent analyse la requête et décide d’utiliser un tool
4. Le MCP exécute le tool (scraping)
5. Les données sont renvoyées à l’agent
6. Le backend renvoie la réponse au frontend

---

## 🔧 Prérequis

- Python 3.10+
- Node.js 18+
- Git
- Ollama installé en local  
  👉 https://ollama.com

---

## 📦 Installation

### 1. Cloner le projet
```bash
git clone https://github.com/ton-username/assistant-plantes-ia.git
cd assistant-plantes-ia

2. Installer Ollama et le modèle
ollama pull llama3.1

3. Backend (FastAPI + MCP)
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi pydantic "uvicorn[standard]" requests beautifulsoup4

4. Frontend
cd frontend
npm install

🚀 Utilisation
Lancer le backend
cd backend
source venv/bin/activate
uvicorn main:app --reload


➡️ Backend accessible sur :
http://127.0.0.1:8000

Lancer le frontend
cd frontend
npm run dev


➡️ Frontend accessible sur :
http://localhost:5173

🧪 Tester le MCP / tools
Lister les tools
GET http://127.0.0.1:8000/tools

Tester le scraping
POST http://127.0.0.1:8000/execute

{
  "tool": "fetch_plant_sources",
  "arguments": {
    "site": "https://www.conservation-nature.fr/plantes/",
    "limit": 3
  }
}

📁 Structure du projet
assistant-plantes-ia/
├── frontend/
│   └── src/
│       ├── components/
│       ├── services/
│       └── App.jsx
│
├── backend/
│   ├── main.py
│   ├── agent/
│   │   └── orchestrator.py
│   ├── mcp/
│   │   ├── server.py
│   │   ├── registry.py
│   │   └── schemas.py
│   └── tools/
│       └── scraping.py
│
├── docs/
│   └── documentation_technique.md
│
└── README.md

🛠️ Technologies

Frontend
JavaScript
React
Fetch API
Vite

Backend
Python
FastAPI
Pydantic
Uvicorn

IA
Ollama
Modèle LLM open-source (Llama 3.1)

Scraping
Requests
BeautifulSoup4

🗓️ Roadmap

Version actuelle (MVP)
Architecture agent + MCP
Tool de scraping fonctionnel
Chatbot simple

Évolutions possibles
Multi-tools
RAG / base vectorielle
Historique utilisateur
Diagnostic visuel
Multi-langue

📖 Documentation
La documentation technique détaillée est disponible dans :
https://www.notion.so/FlorIA-ChatBot-Documentation-2e2493b6538a80aa9c81c5965d2751a2

🤝 Contribuer
Fork le projet
Créer une branche
Ajouter une fonctionnalité ou un tool
Documenter les changements

📝 Licence
MIT License

👤 Auteur
[Nos prénoms]
GitHub : lien

<div align="center"> <strong>🌱 Projet pédagogique — Architecture agentique & IA locale 🌱</strong> </div> ```
