#!/usr/bin/env bash
set -e

echo "============================================================"
echo "  Installation d'Antigravity Auto pour Linux"
echo "============================================================"

# 1. Vérifier si agy est disponible
AGY_BIN="$(which agy 2>/dev/null || echo "$HOME/.local/bin/agy")"
if [ ! -x "$AGY_BIN" ]; then
    echo "[!] Avertissement : binaire 'agy' introuvable dans PATH ou ~/.local/bin/agy."
else
    echo "[✓] Binaire agy détecté : $AGY_BIN"
fi

# 2. Créer les commandes globales agy-auto et agy-yolo dans ~/.local/bin
mkdir -p "$HOME/.local/bin"

cat << 'EOF' > "$HOME/.local/bin/agy-auto"
#!/usr/bin/env bash
exec agy --dangerously-skip-permissions "$@"
EOF
chmod +x "$HOME/.local/bin/agy-auto"
echo "[✓] Commande installée : ~/.local/bin/agy-auto"

cat << 'EOF' > "$HOME/.local/bin/agy-yolo"
#!/usr/bin/env bash
exec agy --dangerously-skip-permissions "$@"
EOF
chmod +x "$HOME/.local/bin/agy-yolo"
echo "[✓] Commande installée : ~/.local/bin/agy-yolo"

# 3. Configurer ~/.bashrc pour les alias
if ! grep -q "alias agy-auto" "$HOME/.bashrc" 2>/dev/null; then
    cat << 'EOF' >> "$HOME/.bashrc"

# Antigravity CLI Auto-Permissions
alias agy-auto="agy --dangerously-skip-permissions"
alias agy-yolo="agy --dangerously-skip-permissions"
EOF
    echo "[✓] Alias ajoutés à ~/.bashrc"
else
    echo "[✓] Alias déjà présents dans ~/.bashrc"
fi

# 4. Mettre à jour settings.json
SETTINGS_FILE="$HOME/.gemini/antigravity-cli/settings.json"
if [ -d "$(dirname "$SETTINGS_FILE")" ]; then
    python3 -c "
import json, os
path = '$SETTINGS_FILE'
data = {}
if os.path.exists(path):
    try:
        with open(path, 'r') as f:
            data = json.load(f)
    except Exception:
        pass
data['toolPermission'] = 'always-proceed'
data['artifactReviewPolicy'] = 'always-proceed'
with open(path, 'w') as f:
    json.dump(data, f, indent=2)
print('[✓] Configuration mise à jour dans ~/.gemini/antigravity-cli/settings.json')
"
fi

# 5. Rendre les scripts locaux exécutables
chmod +x "$(dirname "$0")/lancer_agy_sans_permissions.sh" 2>/dev/null || true
chmod +x "$(dirname "$0")/lancer_auto_enter_cli.sh" 2>/dev/null || true
chmod +x "$(dirname "$0")/auto_enter_cli.py" 2>/dev/null || true

echo "============================================================"
echo "  Installation terminée avec succès !"
echo "  Vous pouvez maintenant taper :"
echo "    agy-auto     (ou agy-yolo)"
echo "  depuis n'importe quel terminal."
echo "============================================================"
