#!/bin/bash
# ============================================================================
#                        FlorIA - Guide de Démonstration
# ============================================================================
#
# Ce script guide l'utilisateur à travers toutes les étapes nécessaires
# pour faire tourner la démo FlorIA (frontend Netlify + backend local).
#
# PRÉREQUIS:
#   - macOS avec Homebrew installé
#   - Python 3.12+ installé
#   - Ollama installé (https://ollama.ai)
#   - Connexion internet
#
# ARCHITECTURE:
#   [Site Netlify] ---> [ngrok tunnel] ---> [Ce Mac] ---> [Ollama LLM]
#
# ============================================================================

set -e  # Arrêter en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
NGROK_URL=""

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

print_header() {
    echo ""
    echo -e "${CYAN}============================================================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}============================================================================${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}[ÉTAPE]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[ATTENTION]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERREUR]${NC} $1"
}

print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

wait_for_user() {
    echo ""
    echo -e "${YELLOW}Appuie sur ENTRÉE pour continuer...${NC}"
    read -r
}

# ============================================================================
# ÉTAPE 0 : AFFICHER LE GUIDE
# ============================================================================

print_header "FlorIA - Guide de Démonstration"

echo "Ce script va te guider à travers les étapes suivantes :"
echo ""
echo "  1. Vérification des prérequis (Homebrew, Python, Ollama)"
echo "  2. Installation de ngrok (tunnel pour exposer le backend)"
echo "  3. Configuration de ngrok (création compte + token)"
echo "  4. Installation des dépendances Python"
echo "  5. Lancement de la démo"
echo "  6. Configuration de l'URL sur Netlify"
echo ""
echo -e "${YELLOW}Temps estimé : 10-15 minutes pour la première configuration${NC}"
echo ""

wait_for_user

# ============================================================================
# ÉTAPE 1 : VÉRIFICATION DES PRÉREQUIS
# ============================================================================

print_header "ÉTAPE 1 : Vérification des prérequis"

# Vérifier Homebrew
print_step "Vérification de Homebrew..."
if command -v brew &> /dev/null; then
    print_success "Homebrew est installé"
else
    print_error "Homebrew n'est pas installé !"
    echo ""
    echo "Installe Homebrew avec cette commande :"
    echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    echo ""
    exit 1
fi

# Vérifier Python
print_step "Vérification de Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION est installé"
else
    print_error "Python 3 n'est pas installé !"
    echo "Installe Python avec : brew install python"
    exit 1
fi

# Vérifier Ollama
print_step "Vérification de Ollama..."
if command -v ollama &> /dev/null; then
    print_success "Ollama est installé"
else
    print_warning "Ollama n'est pas installé !"
    echo ""
    echo "Ollama est nécessaire pour le LLM local."
    echo "Installe-le depuis : https://ollama.ai"
    echo ""
    echo "Ou avec Homebrew :"
    echo "  brew install ollama"
    echo ""
    read -p "Veux-tu installer Ollama maintenant avec Homebrew ? (o/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        brew install ollama
        print_success "Ollama installé"
    else
        print_error "Ollama est requis. Installation annulée."
        exit 1
    fi
fi

print_success "Tous les prérequis de base sont OK"
wait_for_user

# ============================================================================
# ÉTAPE 2 : INSTALLATION DE NGROK
# ============================================================================

print_header "ÉTAPE 2 : Installation de ngrok"

print_info "ngrok permet d'exposer ton backend local sur internet."
print_info "C'est ce qui permet au site Netlify d'appeler ton Mac."
echo ""

if command -v ngrok &> /dev/null; then
    print_success "ngrok est déjà installé"
else
    print_step "Installation de ngrok via Homebrew..."
    brew install ngrok
    print_success "ngrok installé"
fi

wait_for_user

# ============================================================================
# ÉTAPE 3 : CONFIGURATION DE NGROK
# ============================================================================

print_header "ÉTAPE 3 : Configuration de ngrok"

echo "Pour utiliser ngrok, tu dois créer un compte gratuit et configurer ton token."
echo ""
echo -e "${CYAN}Instructions :${NC}"
echo ""
echo "  1. Ouvre ton navigateur et va sur : ${YELLOW}https://ngrok.com${NC}"
echo ""
echo "  2. Clique sur 'Sign up' et crée un compte gratuit"
echo "     (tu peux utiliser GitHub, Google, ou email)"
echo ""
echo "  3. Une fois connecté, va dans le Dashboard"
echo ""
echo "  4. Dans le menu de gauche, clique sur 'Your Authtoken'"
echo ""
echo "  5. Copie ton authtoken (ça ressemble à : 2abc123def456...)"
echo ""

wait_for_user

echo ""
read -p "Colle ton authtoken ngrok ici : " NGROK_TOKEN
echo ""

if [ -n "$NGROK_TOKEN" ]; then
    print_step "Configuration du token ngrok..."
    ngrok config add-authtoken "$NGROK_TOKEN"
    print_success "Token ngrok configuré"
else
    print_warning "Aucun token fourni. Tu devras le configurer plus tard avec :"
    echo "  ngrok config add-authtoken <TON_TOKEN>"
fi

wait_for_user

# ============================================================================
# ÉTAPE 4 : INSTALLATION DES DÉPENDANCES PYTHON
# ============================================================================

print_header "ÉTAPE 4 : Installation des dépendances Python"

cd "$BACKEND_DIR"

# Créer le venv s'il n'existe pas
if [ ! -d "venv" ]; then
    print_step "Création de l'environnement virtuel Python..."
    python3 -m venv venv
    print_success "Environnement virtuel créé"
fi

# Activer le venv et installer les dépendances
print_step "Installation des dépendances Python..."
source venv/bin/activate
pip install -q -r requirements.txt
print_success "Dépendances installées"

cd "$SCRIPT_DIR"

wait_for_user

# ============================================================================
# ÉTAPE 5 : TÉLÉCHARGEMENT DU MODÈLE OLLAMA
# ============================================================================

print_header "ÉTAPE 5 : Préparation du modèle Ollama"

print_info "Le backend utilise le modèle 'llama3.1:8b' par défaut."
print_info "Ce modèle fait environ 4.7 GB et peut prendre quelques minutes à télécharger."
echo ""

# Vérifier si Ollama tourne
if ! pgrep -x "ollama" > /dev/null; then
    print_step "Démarrage de Ollama..."
    ollama serve &> /dev/null &
    sleep 3
fi

# Vérifier si le modèle est déjà téléchargé
if ollama list 2>/dev/null | grep -q "llama3.1:8b"; then
    print_success "Le modèle llama3.1:8b est déjà téléchargé"
else
    print_warning "Le modèle llama3.1:8b n'est pas encore téléchargé"
    echo ""
    read -p "Veux-tu le télécharger maintenant ? (o/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        print_step "Téléchargement du modèle (peut prendre plusieurs minutes)..."
        ollama pull llama3.1:8b
        print_success "Modèle téléchargé"
    else
        print_warning "Tu devras télécharger le modèle plus tard avec : ollama pull llama3.1:8b"
    fi
fi

wait_for_user

# ============================================================================
# ÉTAPE 6 : LANCEMENT DE LA DÉMO
# ============================================================================

print_header "ÉTAPE 6 : Lancement de la démo"

echo "Tout est prêt ! Voici ce qui va se passer :"
echo ""
echo "  1. Ollama va démarrer (s'il ne tourne pas déjà)"
echo "  2. Le backend FastAPI va démarrer sur le port 8000"
echo "  3. ngrok va créer un tunnel et afficher une URL publique"
echo ""
echo -e "${YELLOW}IMPORTANT : Note bien l'URL HTTPS que ngrok va afficher !${NC}"
echo -e "${YELLOW}Tu en auras besoin pour l'étape suivante.${NC}"
echo ""

wait_for_user

# Démarrer Ollama si nécessaire
if ! pgrep -x "ollama" > /dev/null; then
    print_step "Démarrage de Ollama..."
    ollama serve &> /dev/null &
    sleep 3
    print_success "Ollama démarré"
fi

# Démarrer le backend
print_step "Démarrage du backend FastAPI..."
cd "$BACKEND_DIR"
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 &> /dev/null &
BACKEND_PID=$!
cd "$SCRIPT_DIR"
sleep 2

# Vérifier que le backend répond
if curl -s http://localhost:8000/tools > /dev/null 2>&1; then
    print_success "Backend démarré (PID: $BACKEND_PID)"
else
    print_warning "Le backend met du temps à démarrer, attends quelques secondes..."
fi

echo ""
print_header "NGROK - TUNNEL ACTIF"

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                                        ║${NC}"
echo -e "${GREEN}║  ngrok va s'ouvrir maintenant et afficher une URL comme :             ║${NC}"
echo -e "${GREEN}║                                                                        ║${NC}"
echo -e "${GREEN}║     Forwarding  ${YELLOW}https://abc123.ngrok-free.app${GREEN} -> http://localhost:8000  ║${NC}"
echo -e "${GREEN}║                                                                        ║${NC}"
echo -e "${GREEN}║  ${CYAN}COPIE L'URL HTTPS !${GREEN} Tu en auras besoin pour Netlify.               ║${NC}"
echo -e "${GREEN}║                                                                        ║${NC}"
echo -e "${GREEN}║  Pour arrêter la démo : appuie sur Ctrl+C                              ║${NC}"
echo -e "${GREEN}║                                                                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Fonction de cleanup
cleanup() {
    echo ""
    print_step "Arrêt de la démo..."
    kill $BACKEND_PID 2>/dev/null || true
    print_success "Démo arrêtée"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Lancer ngrok
ngrok http 8000

# ============================================================================
# FIN DU SCRIPT
# ============================================================================
