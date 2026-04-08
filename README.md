# Cheatsheet Generator

Petit générateur Python qui transforme un markdown en cheatsheet HTML stylée (thème notebook / pastel) avec bouton d'export PDF intégré.

## Aperçu

- **Thème papier** : fond crème, lignes de cahier, marge rouge, polices manuscrites (Caveat + Patrick Hand)
- **Surligneurs pastel** par niveau de difficulté (jaune / bleu / violet)
- **Un conseil par ligne** pour une lecture rapide façon prise de notes
- **Bouton "Télécharger en PDF"** sticky qui utilise `html2pdf.js` côté client
- **Zéro dépendance** : uniquement la stdlib Python

## Usage

```bash
python3 build_cheatsheet.py input.md              # → input.html
python3 build_cheatsheet.py input.md output.html  # chemin custom
```

Ouvrir le HTML généré dans un navigateur, puis cliquer sur le bouton en haut à droite pour récupérer le PDF.

## Format markdown attendu

```markdown
# Titre de la cheatsheet

Paragraphe d'introduction qui sert de sous-titre.

- **Titre du conseil** — corps du conseil avec `code` et *italique*.
- **Autre conseil** — ...
```

Le parser reconnaît :
- `# Titre` pour le titre principal
- Le texte avant le premier bullet pour l'intro
- `- **Titre** — corps` pour chaque conseil
- Inline : `` `code` ``, `**bold**`, `*italic*`

## Fichiers

- `build_cheatsheet.py` — le générateur
- `optimiser-tokens-claude-code.md` — exemple de markdown source
- `optimiser-tokens-claude-code.html` — sortie générée
