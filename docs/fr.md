# Optimiser sa consommation de tokens avec Claude Code

Récapitulatif de hacks pour réduire la consommation de tokens et mieux contrôler ses coûts sur Claude Code, classés par niveau de difficulté.


- **Nouvelles sessions** — `/clear` entre tâches sans rapport.
- **Déconnecter les MCP inutiles** — un seul serveur peut coûter ~18 000 tokens/message. Préférer les CLI (ex: Google Workspace CLI vs MCP Google Calendar).
- **Regrouper les prompts** — 3 messages séparés = 3x plus cher qu'un seul combiné. Éditer/régénérer plutôt que corriger en follow-up.
- **Plan mode d'abord** — évite que Claude parte dans la mauvaise direction. Ajouter dans `CLAUDE.md` : *"Ne fais aucun changement tant que tu n'as pas 95% de confiance"*.
- **`/context` et `/cost`** — voir ce qui consomme (historique, MCP, fichiers). `/usage` en mode subscription.
- **`/statusline`** — affiche modèle, % contexte utilisé, rate limit en temps réel dans le terminal.
- **Dashboard cloud** — checker sa conso toutes les 20-30 min sur *claude.ai > Settings > Usage*.
- **Être précis dans ce qu'on colle** — ne pas balancer un fichier entier si seule une fonction est concernée.
- **Surveiller Claude** — l'arrêter s'il boucle ou part dans la mauvaise direction, ça économise des milliers de tokens.
- **`CLAUDE.md` léger (<200 lignes)** — le traiter comme un index avec des références vers les fichiers, pas le contenu lui-même.
- **Références chirurgicales** — `@fichier.ts` + nom de fonction précis, ne pas dire *"trouve le bug dans mon repo"*.
- **Compacter à 60%** — l'autocompact se déclenche à 95% (trop tard). Après 3-4 compacts, faire un résumé → `/clear` → renvoyer le résumé.
- **Attention aux pauses** — le prompt cache expire après 5 min. Faire `/compact` avant de s'absenter.
- **Outputs de commandes** — un `git log` peut injecter des centaines de lignes dans le contexte. Utiliser des outils comme RTK pour résumer les outputs.
- **Choisir le bon modèle** — Sonnet par défaut (80% des cas), Haiku pour sous-agents/tâches simples, Opus pour architecture/planification complexe.
- **Coût des sub-agents** — 7-10x plus de tokens qu'une session standard. Déléguer les tâches simples à Haiku.
- **Peak vs Off-peak** — Peak = 14h-20h (heure FR) en semaine. Off-peak = après 20h + weekends. Lancer les grosses tâches en off-peak. Avant un reset, lancer des agents en parallèle pour consommer le reste.
- **`CLAUDE.md` comme source de vérité** — stocker des décisions, pas des conversations. Y mettre les règles de gestion (ex: modèle par défaut des sub-agents).
- **`--allowedTools` au lancement** — restreindre les outils disponibles et réduire l'overhead système.
- **Worktrees git pour découper** — chaque sous-tâche dans une branche/session isolée, contexte minimal.
- **Prompts en anglais** — ~30% moins de tokens qu'en français pour le même contenu (tokenisation plus efficace).
- **Limites de lignes dans les instructions** — ex: *"résume en 10 lignes max"* pour contrôler la taille des réponses.
- **`--model` en flag** — switcher de modèle ponctuellement sans changer la config globale.
