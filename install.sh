#!/usr/bin/env bash
# ==============================================================================
# Antigravity Auto - Script d'installation universel pour Linux
# https://github.com/LOLMANREX/antigravity-auto
# ==============================================================================
set -e

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
CYAN="\033[0;36m"
RED="\033[0;31m"
RESET="\033[0m"

echo -e "${CYAN}${BOLD}"
echo "============================================================"
echo "    Installation d'Antigravity Auto pour Linux"
echo "============================================================"
echo -e "${RESET}"

# Définition des répertoires
BIN_DIR="$HOME/.local/bin"
SHARE_DIR="$HOME/.local/share/antigravity-auto"
mkdir -p "$BIN_DIR"
mkdir -p "$SHARE_DIR"

# 1. Vérification / Installation de Antigravity CLI (agy)
echo -e "${BOLD}[1/5] Vérification d'Antigravity CLI (agy)...${RESET}"
AGY_BIN="$(which agy 2>/dev/null || echo "$HOME/.local/bin/agy")"

if [ ! -x "$AGY_BIN" ]; then
    echo -e "${YELLOW}[!] Antigravity CLI ('agy') n'est pas encore installé.${RESET}"
    echo -e "${CYAN}[+] Installation automatique d'Antigravity CLI via le script officiel...${RESET}"
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL https://antigravity.google/cli/install.sh | bash
    elif command -v wget >/dev/null 2>&1; then
        wget -qO- https://antigravity.google/cli/install.sh | bash
    else
        echo -e "${RED}[✗] Ni curl ni wget n'est installé. Installez curl ou wget d'abord.${RESET}"
        exit 1
    fi
    AGY_BIN="$(which agy 2>/dev/null || echo "$HOME/.local/bin/agy")"
fi

if [ -x "$AGY_BIN" ]; then
    echo -e "${GREEN}[✓] Antigravity CLI détecté : $AGY_BIN${RESET}"
else
    echo -e "${YELLOW}[!] Binaire agy non localisé immédiatement, l'installation continue...${RESET}"
fi

# 2. Déploiement des scripts Python et fichiers du repo
echo -e "${BOLD}[2/5] Déploiement des scripts dans $SHARE_DIR...${RESET}"

CURRENT_DIR=""
if [ -n "$BASH_SOURCE" ] && [ -f "$BASH_SOURCE" ]; then
    CURRENT_DIR="$(cd "$(dirname "$BASH_SOURCE")" && pwd)"
fi

# Si exécuté depuis un clone local contenant auto_enter_cli.py
if [ -n "$CURRENT_DIR" ] && [ -f "$CURRENT_DIR/auto_enter_cli.py" ]; then
    cp -u "$CURRENT_DIR/auto_enter_cli.py" "$SHARE_DIR/" 2>/dev/null || cp "$CURRENT_DIR/auto_enter_cli.py" "$SHARE_DIR/"
    [ -f "$CURRENT_DIR/auto_enter_app.py" ] && cp -u "$CURRENT_DIR/auto_enter_app.py" "$SHARE_DIR/" 2>/dev/null || true
    echo -e "${GREEN}[✓] Scripts copiés depuis le répertoire local ($CURRENT_DIR).${RESET}"
else
    # Si exécuté via curl/pipe
    echo -e "${CYAN}[+] Téléchargement des scripts depuis GitHub...${RESET}"
    RAW_BASE="https://raw.githubusercontent.com/LOLMANREX/antigravity-auto/main"
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "$RAW_BASE/auto_enter_cli.py" -o "$SHARE_DIR/auto_enter_cli.py"
    elif command -v wget >/dev/null 2>&1; then
        wget -q "$RAW_BASE/auto_enter_cli.py" -O "$SHARE_DIR/auto_enter_cli.py"
    fi
    echo -e "${GREEN}[✓] Scripts téléchargés dans $SHARE_DIR.${RESET}"
fi
chmod +x "$SHARE_DIR/auto_enter_cli.py" 2>/dev/null || true

# 3. Création des commandes globales dans ~/.local/bin
echo -e "${BOLD}[3/5] Installation des commandes globales dans $BIN_DIR...${RESET}"

# agy-auto
cat << 'EOF' > "$BIN_DIR/agy-auto"
#!/usr/bin/env bash
exec agy --dangerously-skip-permissions "$@"
EOF
chmod +x "$BIN_DIR/agy-auto"
echo -e "${GREEN}[✓] Commande installée : $BIN_DIR/agy-auto${RESET}"

# agy-yolo (alias vers agy-auto)
cat << 'EOF' > "$BIN_DIR/agy-yolo"
#!/usr/bin/env bash
exec "$HOME/.local/bin/agy-auto" "$@"
EOF
chmod +x "$BIN_DIR/agy-yolo"
echo -e "${GREEN}[✓] Commande installée : $BIN_DIR/agy-yolo${RESET}"

# agy-enter (lance le script auto-enter)
cat << 'EOF' > "$BIN_DIR/agy-enter"
#!/usr/bin/env bash
SCRIPT="$HOME/.local/share/antigravity-auto/auto_enter_cli.py"
if [ ! -f "$SCRIPT" ]; then
    echo "[!] Script introuvable dans $SCRIPT"
    exit 1
fi
exec python3 "$SCRIPT" "$@"
EOF
chmod +x "$BIN_DIR/agy-enter"
echo -e "${GREEN}[✓] Commande installée : $BIN_DIR/agy-enter${RESET}"

# Désinstallation propre
cat << 'EOF' > "$BIN_DIR/agy-auto-uninstall"
#!/usr/bin/env bash
echo "Désinstallation d'Antigravity Auto..."
rm -f "$HOME/.local/bin/agy-auto" "$HOME/.local/bin/agy-yolo" "$HOME/.local/bin/agy-enter" "$HOME/.local/bin/auto-enter" "$HOME/.local/bin/agy-auto-uninstall"
rm -rf "$HOME/.local/share/antigravity-auto"
sed -i '/# Antigravity CLI Auto-Permissions/,+2d' "$HOME/.bashrc" 2>/dev/null || true
sed -i '/# Antigravity CLI Auto-Permissions/,+2d' "$HOME/.zshrc" 2>/dev/null || true
echo "Désinstallation terminée."
EOF
chmod +x "$BIN_DIR/agy-auto-uninstall"

# 4. Configuration de settings.json (toujours sans confirmation & workspace de confiance)
echo -e "${BOLD}[4/5] Configuration persistante de Antigravity CLI...${RESET}"
SETTINGS_DIR="$HOME/.gemini/antigravity-cli"
mkdir -p "$SETTINGS_DIR"
SETTINGS_FILE="$SETTINGS_DIR/settings.json"

if command -v python3 >/dev/null 2>&1; then
    python3 -c "
import json, os
path = '$SETTINGS_FILE'
data = {}
if os.path.exists(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        data = {}

data['toolPermission'] = 'always-proceed'
data['artifactReviewPolicy'] = 'always-proceed'

workspaces = data.get('trustedWorkspaces', [])
if not isinstance(workspaces, list):
    workspaces = []
home = os.path.expanduser('~')
if home not in workspaces:
    workspaces.append(home)
data['trustedWorkspaces'] = workspaces

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)
"
    echo -e "${GREEN}[✓] Options configurées dans $SETTINGS_FILE :${RESET}"
    echo "    - toolPermission: 'always-proceed'"
    echo "    - artifactReviewPolicy: 'always-proceed'"
    echo "    - trustedWorkspaces: inclut votre dossier personnel"
else
    echo -e "${YELLOW}[!] python3 non détecté, écriture directe de la configuration...${RESET}"
    cat << EOF > "$SETTINGS_FILE"
{
  "artifactReviewPolicy": "always-proceed",
  "toolPermission": "always-proceed",
  "trustedWorkspaces": [
    "$HOME"
  ]
}
EOF
fi

# 5. Configuration de l'environnement Shell (.bashrc / .zshrc)
echo -e "${BOLD}[5/5] Configuration du Shell (PATH & Alias)...${RESET}"

configure_shell_rc() {
    local rc_file="$1"
    local shell_name="$2"

    if [ -f "$rc_file" ] || [ "$shell_name" = "bash" ]; then
        touch "$rc_file"

        # Vérification du PATH
        if ! grep -q 'PATH=.*\.local/bin' "$rc_file" 2>/dev/null; then
            echo '' >> "$rc_file"
            echo '# Ajout de ~/.local/bin au PATH' >> "$rc_file"
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$rc_file"
        fi

        # Ajout des alias
        if ! grep -q "alias agy-auto" "$rc_file" 2>/dev/null; then
            cat << 'EOF' >> "$rc_file"

# Antigravity CLI Auto-Permissions
alias agy-auto="agy --dangerously-skip-permissions"
alias agy-yolo="agy --dangerously-skip-permissions"
EOF
            echo -e "${GREEN}[✓] Alias et PATH configurés dans $rc_file${RESET}"
        else
            echo -e "${GREEN}[✓] Alias déjà présents dans $rc_file${RESET}"
        fi
    fi
}

configure_shell_rc "$HOME/.bashrc" "bash"
if [ -f "$HOME/.zshrc" ]; then
    configure_shell_rc "$HOME/.zshrc" "zsh"
fi

# Détection optionnelle de xdotool pour la simulation de touche
if ! command -v xdotool >/dev/null 2>&1 && ! command -v ydotool >/dev/null 2>&1; then
    echo -e "${YELLOW}[i] Astuce : Si vous souhaitez utiliser le simulateur de touche Entrée ('agy-enter'),${RESET}"
    echo -e "${YELLOW}    installez xdotool : sudo apt install -y xdotool${RESET}"
fi

# Rendre exécutables les scripts du repo local s'ils existent
if [ -n "$CURRENT_DIR" ]; then
    chmod +x "$CURRENT_DIR/lancer_agy_sans_permissions.sh" 2>/dev/null || true
    chmod +x "$CURRENT_DIR/lancer_auto_enter_cli.sh" 2>/dev/null || true
    chmod +x "$CURRENT_DIR/setup_linux.sh" 2>/dev/null || true
    chmod +x "$CURRENT_DIR/install.sh" 2>/dev/null || true
fi

echo ""
echo -e "${CYAN}${BOLD}============================================================${RESET}"
echo -e "${GREEN}${BOLD}  ✨ Installation terminée avec succès en quelques secondes !${RESET}"
echo -e "${CYAN}${BOLD}============================================================${RESET}"
echo ""
echo -e "Vous pouvez utiliser immédiatement :"
echo -e "  ${BOLD}${GREEN}agy-auto${RESET}    : Lance Antigravity CLI avec validation automatique"
echo -e "  ${BOLD}${GREEN}agy-yolo${RESET}    : Raccourci équivalent à agy-auto"
echo -e "  ${BOLD}${GREEN}agy-enter${RESET}   : Lance le script console d'auto-validation par Entrée"
echo ""
echo -e "${YELLOW}Important : Pour que les alias soient pris en compte dans CE terminal :${RESET}"
echo -e "  ${CYAN}source ~/.bashrc${RESET}  (ou rouvrez simplement votre terminal)"
echo -e "${CYAN}============================================================${RESET}"
