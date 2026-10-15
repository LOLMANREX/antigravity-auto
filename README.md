# Antigravity CLI - Automatisation Totale des Permissions & Touche Entrée

Ce projet permet à l'agent Antigravity CLI (`agy`) d'exécuter l'ensemble de ses outils et commandes **sans demander de validation manuelle** ou en **validant automatiquement par la touche Entrée**. Compatible **Linux** et **Windows**.

---

## ⚡ Installation Rapide sur Linux

Deux options ultra-rapides pour rendre le script 100% opérationnel :

### Option 1 : En 1 seule commande (Recommandé)
Pas besoin de cloner manuellement le repo. Ouvrez votre terminal et exécutez :

```bash
curl -fsSL https://raw.githubusercontent.com/LOLMANREX/antigravity-auto/main/install.sh | bash
```

### Option 2 : En 2/3 commandes (via Git)
Si vous préférez cloner le dépôt :

```bash
git clone https://github.com/LOLMANREX/antigravity-auto.git
cd antigravity-auto
./install.sh
```

*(Ou `./setup_linux.sh`)*

---

### 💡 Que fait l'installation automatique ?
1. **Vérifie et installe Antigravity CLI (`agy`)** si absent.
2. **Installe les commandes globales** dans `~/.local/bin/` :
   - `agy-auto` : Lance Antigravity CLI sans aucune demande de permission.
   - `agy-yolo` : Raccourci équivalent à `agy-auto`.
   - `agy-enter` : Lance le script d'appui automatique sur la touche Entrée depuis n'importe quel dossier.
3. **Configure `settings.json`** de façon permanente :
   - Active `toolPermission: "always-proceed"`.
   - Active `artifactReviewPolicy: "always-proceed"`.
   - Ajoute votre répertoire utilisateur à `trustedWorkspaces` (aucun avertissement de workspace).
4. **Configure votre shell** (`.bashrc` et `.zshrc`) pour intégrer `~/.local/bin` au `PATH` et créer les alias.

> [!NOTE]
> Après l'installation, tapez `source ~/.bashrc` (ou rouvrez votre terminal) pour recharger immédiatement vos alias.

---

## 🚀 Utilisation au quotidien

### 1. Mode Sans Permission Direct (Recommandé)
Depuis **n'importe quel terminal et n'importe quel dossier** :

```bash
# Lancement direct sans aucune demande de permission
agy-auto

# Ou version rapide :
agy-yolo
```

Toutes les options habituelles de `agy` sont supportées :
```bash
agy-auto -c
agy-auto --model "gemini-2.5-pro"
```

### 2. Simulation de la Touche Entrée (`agy-enter`)
Si vous préférez simuler automatiquement des appuis sur [Entrée] (par exemple si un prompt interactif attend une touche) :

```bash
# Accessible partout en ligne de commande :
agy-enter

# Avec options personnalisées :
agy-enter --interval 0.5 --delay 3
```

*(Sous Linux, nécessite `xdotool` : `sudo apt install -y xdotool`)*

---

## 🪟 Installation & Utilisation sous Windows (Sans commande)

Sur Windows, aucune ligne de commande n'est nécessaire :

### 1. Installation 1-Clic
Double-cliquez simplement sur :
- **`Setup.exe`** : Installateur graphique Windows officiel autonome.
*(Ou sur **`Setup_Windows.bat`** si vous préférez exécuter le script batch).*

L'installateur :
1. Crée les commandes globales `agy-auto.bat` et `agy-yolo.bat` dans votre dossier local (`%LOCALAPPDATA%\agy\bin`).
2. Ajoute automatiquement ce dossier à votre variable d'environnement `PATH` Windows.
3. Configure `settings.json` avec `toolPermission: always-proceed` et ajoute votre dossier utilisateur dans `trustedWorkspaces`.
4. Crée un raccourci direct sur votre Bureau.

### 2. Lanceurs rapides
- **`Lancer_Agy_Sans_Permissions.bat`** : Démarre le CLI avec auto-approbation.
- **`Lancer_Auto_Enter_CLI.bat`** : Lance le script auto-enter dans la console.
- **`Lancer_Auto_Enter_GUI.bat`** : Ouvre la petite interface graphique Tkinter (avec raccourci F8 pour Pause/Reprise).

---

## 🗑️ Désinstallation propre (Linux)

Pour retirer les commandes et restaurer vos alias :
```bash
agy-auto-uninstall
```
