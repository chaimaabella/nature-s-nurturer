### Repository: https://github.com/chaimaabella/FlorIA

# 🌱 FlorIA

> Assistant conversationnel intelligent pour prendre soin de vos plantes

FlorIA est un chatbot IA qui aide les propriétaires de plantes à mieux comprendre, entretenir et préserver leurs végétaux grâce à un agent IA local et des outils de scraping spécialisés.

---

## ✨ Fonctionnalités

- 🤖 **Chatbot en langage naturel** — Posez vos questions simplement
- 🌐 **Données enrichies** — Scraping de sites botaniques spécialisés
- 🧠 **Agent IA intelligent** — Décide automatiquement d'utiliser les outils appropriés
- 📚 **Réponses contextualisées** — Informations structurées et pertinentes
- 🔌 **Architecture MCP** — Model Context Protocol pour l'orchestration des outils

---

## 🏗️ Architecture

```
┌─────────────────┐
│    Frontend     │  TypeScript / React / Vite
│   (Netlify)     │
└────────┬────────┘
         │ HTTP (REST)
         ▼
┌─────────────────┐
│    Backend      │  FastAPI
│    main.py      │
│  ┌───────────┐  │
│  │   Agent   │  │  ← Ollama (LLM local)
│  │Orchestrat.│  │
│  └─────┬─────┘  │
└────────┼────────┘
         │ Appel interne
         ▼
┌─────────────────┐
│      MCP        │  Model Context Protocol
│   server.py     │
│  ┌───────────┐  │
│  │   Tools   │  │  ← scraping.py
│  └───────────┘  │
└────────┬────────┘
         ▼
    🌐 Sites web
```

### Flux de données
1. L'utilisateur pose une question dans le frontend
2. Le backend transmet la requête à l'agent IA
3. L'agent analyse et décide d'utiliser un tool si nécessaire
4. Le MCP exécute le tool (scraping de sites botaniques)
5. Les données enrichies sont renvoyées à l'agent
6. La réponse finale est affichée à l'utilisateur

---

## 🔧 Prérequis

- **Python** 3.10+
- **Node.js** 18+
- **Ollama** — [https://ollama.ai](https://ollama.ai)
- **Git**

---

## 📦 Installation

### 1. Cloner le projet
```bash
git clone https://github.com/chaimaabella/nature-s-nurturer.git
cd nature-s-nurturer
```

### 2. Backend (FastAPI)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Frontend (React)
```bash
cd frontend
npm install
```

### 4. Ollama (LLM)
```bash
ollama pull llama3.1:8b
```

---

## 🚀 Utilisation

### Lancer le backend
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```
→ Backend accessible sur `http://localhost:8000`

### Lancer le frontend
```bash
cd frontend
npm run dev
```
→ Frontend accessible sur `http://localhost:5173`

---

## 🎬 Démo / Soutenance

Pour faire une démo avec le frontend déployé sur Netlify et le backend local :

```bash
./DEMO.sh
```

Ce script interactif guide à travers :
- Installation des prérequis (ngrok, Ollama)
- Configuration du tunnel ngrok
- Lancement du backend

Voir aussi : [`DEMO_NETLIFY.md`](./DEMO_NETLIFY.md) pour la configuration Netlify.

---

## 📁 Structure du projet

```
nature-s-nurturer/
├── frontend/                 # Application React
│   ├── src/
│   │   ├── components/       # Composants UI (shadcn)
│   │   ├── pages/            # Pages (Chat, Index, etc.)
│   │   ├── hooks/            # Hooks personnalisés
│   │   └── lib/              # Utilitaires
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                  # API FastAPI
│   ├── main.py               # Point d'entrée API
│   ├── agent/
│   │   └── orchestrator.py   # Agent IA + mémoire
│   ├── mcp/
│   │   ├── server.py         # Serveur MCP
│   │   ├── registry.py       # Registre des tools
│   │   └── schemas.py        # Schémas Pydantic
│   └── tools/
│       └── scraping.py       # Tool de scraping
│
├── DEMO.sh                   # Script de démo
├── DEMO_NETLIFY.md           # Guide Netlify
└── README.md
```

---

## 🛠️ Technologies

### Frontend
- **TypeScript** + **React 18**
- **Vite** — Build tool
- **shadcn/ui** — Composants UI
- **Tailwind CSS** — Styling
- **React Router** — Navigation

### Backend
- **Python** + **FastAPI**
- **Pydantic** — Validation
- **Uvicorn** — Serveur ASGI

### IA & Scraping
- **Ollama** — LLM local
- **Llama 3.1** — Modèle de langage
- **BeautifulSoup4** — Parsing HTML
- **Requests** — HTTP client

---

## 🗓️ Roadmap

### ✅ MVP Actuel
- Architecture agent + MCP fonctionnelle
- Tool de scraping multi-sources
- Chatbot conversationnel
- Mémoire de session

### 🔜 Évolutions possibles
- 📸 Diagnostic visuel (analyse d'images)
- 💾 Historique persistant
- 🌍 Sources multiples (APIs, bases de données)
- 🌐 Multi-langue

---

## 📖 Documentation

Documentation technique détaillée :
👉 [FlorIA — Documentation Notion](https://www.notion.so/FlorIA-ChatBot-Documentation-2e2493b6538a80aa9c81c5965d2751a2)

---

## 👥 Auteurs

Projet réalisé dans le cadre d'un projet pédagogique EPITECH.

---

## 📝 Licence

MIT License

---

<div align="center">
  <strong>🌱 Projet pédagogique — Architecture agentique & IA locale 🌱</strong>
</div>
