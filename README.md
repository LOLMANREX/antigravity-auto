# Antigravity CLI - Automatisation Totale des Permissions & Touche Entrée

Ce dossier contient tous les outils et scripts permettant à l'agent Antigravity CLI (`agy`) d'exécuter l'ensemble de ses commandes et outils **sans demander de permission manuelle** ou en **validant automatiquement par la touche Entrée**. Compatible **Linux** et **Windows**.

---

## 🚀 Résumé des solutions disponibles

| Solution | Méthode | Linux | Windows |
| :--- | :--- | :--- | :--- |
| **1. Commande directe globale** | Commande `agy-auto` / `agy-yolo` | `~/.local/bin/agy-auto` ou alias bash | `C:\Users\...\agy\bin\agy-auto.bat` |
| **2. Configuration persistante** | `settings.json` mis à jour | Automatique pour toutes les sessions `agy` | Automatique pour toutes les sessions `agy` |
| **3. Script Console Léger** | `auto_enter_cli.py` / `.sh` / `.bat` | `./lancer_auto_enter_cli.sh` | Double-clic sur `Lancer_Auto_Enter_CLI.bat` |
| **4. Application Graphique Auto-Enter** | `auto_enter_app.py` / `.bat` | N/A (headless/serveur) | Double-clic sur `Lancer_Auto_Enter_GUI.bat` |

---

## 1. Utiliser directement la commande globale `agy-auto`

La commande globale a été configurée dans votre PATH (`~/.local/bin/agy-auto` sur Linux ou dans l'équivalent Windows).

Désormais, depuis **n'importe quel terminal** :

```bash
# Au lieu de faire : agy
agy-auto

# Ou version courte :
agy-yolo
```

Toutes les options habituelles sont supportées :
```bash
agy-auto -c
agy-auto --model "gemini-2.5-pro"
```

Cette commande démarre Antigravity avec le flag officiel `--dangerously-skip-permissions`, qui auto-approuve directement toutes les exécutions d'outils et commandes sans interruption.

---

## 2. Configuration permanente (`settings.json`)

Votre fichier de configuration globale `~/.gemini/antigravity-cli/settings.json` a été configuré avec :

```json
{
  "trustedWorkspaces": [
    "/home/louis"
  ],
  "toolPermission": "always-proceed",
  "artifactReviewPolicy": "always-proceed"
}
```

Cela indique au moteur Antigravity d'exécuter directement les outils et passer outre les demandes de validation manuelle pour vos sessions standards.

---

## 3. Scripts de lancement rapide dans ce dossier

### Sur Linux :
- **`./setup_linux.sh`** : Réinstalle ou vérifie l'installation des commandes globales et des alias.
- **`./lancer_agy_sans_permissions.sh`** : Lance Antigravity CLI directement en mode sans permissions.
- **`./lancer_auto_enter_cli.sh`** : Lance le script console Auto-Enter.

### Sur Windows :
- **`Lancer_Agy_Sans_Permissions.bat`** : Lance le CLI en mode sans permissions.
- **`Lancer_Auto_Enter_CLI.bat`** : Lance l'auto-enter en mode console.
- **`Lancer_Auto_Enter_GUI.bat`** : Ouvre l'interface graphique Tkinter avec le raccourci F8.

---

## 4. Script Console Headless (`auto_enter_cli.py`)

Pour simuler automatiquement des appuis sur Entrée dans une session existante :

```bash
python3 auto_enter_cli.py --interval 1.0 --delay 3
```

### Options en ligne de commande :
- `--interval` (`-i`) : Intervalle en secondes (défaut: 1.0)
- `--delay` (`-d`) : Compte à rebours avant démarrage (défaut: 3 secondes)
- `--count` (`-c`) : Nombre maximum d'appuis (0 = continu)
- `--all-windows` : Désactive le filtre de fenêtre
- Arrêt : `Ctrl + C` (ou touche `[F8]` sous Windows pour Pause/Reprise)
