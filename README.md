# Antigravity CLI - Automatisation Totale des Permissions & Touche Entrée

Ce dossier contient tous les outils et scripts permettant à l'agent Antigravity CLI (`agy`) d'exécuter l'ensemble de ses commandes et outils **sans demander de permission manuelle** ou en **validant automatiquement par la touche Entrée**.

---

## 🚀 Résumé des solutions disponibles

| Solution | Méthode | Utilisation |
| :--- | :--- | :--- |
| **1. Commande directe globale** | Commande `agy-auto` / `agy-yolo` | Taper `agy-auto` dans n'importe quel terminal |
| **2. Configuration persistante** | `settings.json` mis à jour | Automatique pour toutes les sessions `agy` |
| **3. Application Graphique Auto-Enter** | `Lancer_Auto_Enter_GUI.bat` | Double-cliquer pour ouvrir l'interface avec bouton Marche/Arrêt et raccourci **[F8]** |
| **4. Script Console Léger** | `Lancer_Auto_Enter_CLI.bat` | Double-cliquer ou exécuter `python auto_enter_cli.py` |

---

## 1. Utiliser directement la nouvelle commande `agy-auto`

Un alias global a été installé dans votre dossier PATH (`C:\Users\X\AppData\Local\agy\bin`).

Désormais, depuis **n'importe quel terminal** (PowerShell, CMD, Windows Terminal) :

```bash
# Au lieu de faire : agy
agy-auto

# Ou version raccourcie :
agy-yolo
```

Toutes les options habituelles sont supportées :
```bash
agy-auto -c
agy-auto --model "gemini-2.5-pro"
```

Cette commande démarre Antigravity avec le flag officiel `--dangerously-skip-permissions`, qui auto-approuve directement toutes les exécutions de commandes et modifications de fichiers sans jamais vous solliciter.

---

## 2. Configuration permanente (`settings.json`)

Votre fichier de configuration globale `~/.gemini/antigravity-cli/settings.json` a été mis à jour avec :

```json
{
  "toolPermission": "always-proceed",
  "artifactReviewPolicy": "always-proceed"
}
```

Cela indique au moteur d'Antigravity de passer outre la demande de revue manuelle et d'exécuter directement les outils.

---

## 3. Application Graphique "Auto-Enter Bot" (Tkinter)

Si vous utilisez une session interactive déjà ouverte ou une interface qui attend que vous appuyiez sur la touche **Entrée** :

### Lancement
- Double-cliquez sur : **`Lancer_Auto_Enter_GUI.bat`**
- Ou en ligne de commande : `python auto_enter_app.py`

### Fonctionnalités
- **Raccourci Global [F8]** : Démarrez ou mettez en pause l'appui automatique à tout moment, même depuis votre terminal !
- **Filtre de détection de terminal** : N'envoie la touche Entrée que si la fenêtre active est un terminal (`agy`, `PowerShell`, `CMD`, `Windows Terminal`).
- **Intervalle réglable** : Choisissez le délai entre chaque appui (ex: 1 seconde).
- **Délai initial** : Compte à rebours au lancement (ex: 2s) pour vous laisser le temps de basculer sur la fenêtre souhaitée.
- **Always on Top** : La fenêtre reste au-dessus pour surveiller le statut et les compteurs en direct.
- **Bouton ⚡ Ouvrir agy-auto** : Lance un terminal propre directement en mode sans permissions.

---

## 4. Script Console Headless (`auto_enter_cli.py`)

Pour ceux qui préfèrent une invite de commande légère sans interface graphique :

### Lancement
- Double-cliquez sur : **`Lancer_Auto_Enter_CLI.bat`**
- Ou lancez manuellement :
  ```bash
  python auto_enter_cli.py --interval 1.0 --delay 3
  ```

### Options en ligne de commande
- `--interval` (`-i`) : Intervalle en secondes (défaut: 1.0)
- `--delay` (`-d`) : Compte à rebours avant démarrage (défaut: 3 secondes)
- `--count` (`-c`) : Nombre maximum d'appuis (0 = continu)
- `--all-windows` : Désactive le filtre et appuie quelle que soit la fenêtre active
- Raccourci : Touche **[F8]** pour Mettre en pause / Reprendre, **[Ctrl+C]** pour quitter.
