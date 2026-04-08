#!/usr/bin/env python3
"""
Génère une cheatsheet HTML stylée (thème notebook/pastel) à partir d'un markdown.

Format markdown attendu :
    # Titre
    Paragraphe d'intro...
    - **Titre du conseil** — corps du conseil avec `code` et *italique*.
    - **Autre conseil** — ...

Usage minimal :
    python build_cheatsheet.py input.md output.html

Avec sélecteur de langue :
    python build_cheatsheet.py optimiser-tokens.md index.html \\
        --lang fr --alt-lang en --alt-href en.html
    python build_cheatsheet.py optimize-tokens.md   en.html    \\
        --lang en --alt-lang fr --alt-href index.html
"""

import argparse
import html
import re
import sys
from pathlib import Path

BULLET_CHAR = "✓"

# Métadonnées par langue : drapeau emoji + libellé bouton PDF.
# L'ordre du dict détermine l'ordre d'affichage des pills (stable entre les pages).
LANG_META = {
    "fr": {"flag": "🇫🇷", "pdf_label": "Télécharger en PDF", "label": "Français"},
    "en": {"flag": "🇬🇧", "pdf_label": "Download as PDF",   "label": "English"},
}


# --- Parsing markdown ---------------------------------------------------------

def parse_markdown(md: str):
    """Retourne (title, intro, [bullets]) où bullet = (title_html, body_html)."""
    title = ""
    intro_lines = []
    bullets = []

    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("# "):
            title = line[2:].strip()
        elif line.lstrip().startswith("- "):
            bullets.append(line.lstrip()[2:].strip())
        elif not bullets:  # avant le premier bullet => intro
            intro_lines.append(line.strip())

    intro = " ".join(intro_lines)
    parsed_bullets = [split_bullet(b) for b in bullets]
    return title, intro, parsed_bullets


def split_bullet(bullet: str):
    """Sépare un bullet '**Titre** — corps' en (titre_html, corps_html)."""
    m = re.match(r"\*\*(.+?)\*\*\s*[—–-]\s*(.*)", bullet)
    if m:
        return inline_md(m.group(1)), inline_md(m.group(2))
    return "", inline_md(bullet)


def inline_md(text: str) -> str:
    """Convertit `code`, **bold**, *italic* en HTML. Échappe le reste."""
    placeholders = {}

    def stash(match):
        key = f"\x00{len(placeholders)}\x00"
        placeholders[key] = f"<code>{html.escape(match.group(1))}</code>"
        return key

    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)

    for key, value in placeholders.items():
        text = text.replace(key, value)
    return text


# --- Génération HTML ----------------------------------------------------------

CSS = r"""
  :root {
    --paper: #fdfbf5;
    --paper-line: #e8e2d0;
    --ink: #3a3530;
    --ink-soft: #6b645c;
    --pencil: #5d6470;
    --accent-yellow: #fff3b0;
    --accent-pink: #ffd6e0;
    --accent-blue: #cfe6f7;
    --accent-purple: #e3d4f5;
    --border-soft: #e0d8c5;
  }
  * { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0;
    background: radial-gradient(ellipse at top, #faf6ea 0%, #f3ecd9 100%);
    color: var(--ink);
    font-family: "Patrick Hand", "Inter", -apple-system, sans-serif;
    line-height: 1.6; font-size: 18px;
    -webkit-font-smoothing: antialiased;
  }

  /* --- Barre flottante haut-droite (lang switch + bouton PDF) --- */
  .top-bar {
    position: fixed; top: 22px; right: 22px; z-index: 1000;
    display: inline-flex; align-items: center; gap: 12px;
  }

  /* --- Sélecteur de langue --- */
  .lang-switch {
    display: inline-flex; align-items: center; gap: 4px;
    background: var(--paper); border: 2px solid var(--ink);
    border-radius: 32px 28px 30px 26px / 28px 32px 26px 30px;
    padding: 5px; box-shadow: 3px 3px 0 var(--ink);
    transform: rotate(2deg);
  }
  .lang-switch a {
    display: inline-flex; align-items: center; justify-content: center;
    width: 38px; height: 38px; border-radius: 50%;
    text-decoration: none; font-size: 22px; line-height: 1;
    filter: grayscale(0.55); opacity: 0.55;
    transition: filter 0.15s ease, opacity 0.15s ease, background 0.15s ease;
  }
  .lang-switch a:hover { filter: grayscale(0); opacity: 1; }
  .lang-switch a.active {
    filter: grayscale(0); opacity: 1;
    background: var(--accent-yellow);
    box-shadow: inset 0 0 0 1.5px var(--ink);
  }

  /* --- Bouton PDF --- */
  .download-btn {
    background: var(--accent-yellow); color: var(--ink);
    border: 2px solid var(--ink); padding: 11px 20px;
    border-radius: 30px 28px 32px 26px / 28px 32px 26px 30px;
    font-family: "Caveat", cursive; font-size: 20px; font-weight: 700;
    cursor: pointer; box-shadow: 3px 3px 0 var(--ink);
    transition: transform 0.12s ease, box-shadow 0.12s ease;
    display: inline-flex; align-items: center; gap: 8px;
    transform: rotate(-2deg);
  }
  .download-btn:hover { transform: rotate(-2deg) translate(-1px, -1px); box-shadow: 5px 5px 0 var(--ink); }
  .download-btn:active { transform: rotate(-2deg) translate(2px, 2px); box-shadow: 1px 1px 0 var(--ink); }
  .download-btn svg { width: 18px; height: 18px; }

  .container {
    max-width: 820px; margin: 0 auto; padding: 90px 50px 80px;
    background: var(--paper);
    background-image: repeating-linear-gradient(to bottom, transparent 0, transparent 31px, var(--paper-line) 31px, var(--paper-line) 32px);
    border-left: 2px solid #f0c4c4; border-right: 1px solid var(--border-soft);
    box-shadow: 0 0 0 1px var(--border-soft), 0 30px 60px rgba(80, 60, 30, 0.08);
    position: relative; min-height: 100vh;
  }
  .container::before { content: ""; position: absolute; left: 60px; top: 0; bottom: 0; width: 2px; background: #f0c4c4; opacity: 0.7; }
  header { text-align: left; margin-bottom: 40px; padding-left: 20px; padding-bottom: 22px; border-bottom: 2px dashed var(--border-soft); }
  .badge {
    display: inline-block; background: var(--accent-pink); color: var(--ink);
    border: 1.5px solid var(--ink); padding: 3px 14px;
    border-radius: 20px 18px 22px 16px;
    font-family: "Caveat", cursive; font-size: 19px; font-weight: 700;
    margin-bottom: 14px; transform: rotate(-1.5deg);
    box-shadow: 2px 2px 0 rgba(58, 53, 48, 0.2);
  }
  h1 { font-family: "Caveat", cursive; font-size: 44px; margin: 0 0 10px; font-weight: 700; line-height: 1.1; }
  .subtitle { color: var(--ink-soft); font-family: "Patrick Hand", cursive; font-size: 19px; margin: 0; max-width: 640px; }
  .section { margin-bottom: 38px; padding-left: 20px; }
  .tip { display: flex; align-items: flex-start; gap: 14px; padding: 8px 4px; margin-bottom: 4px; border-radius: 6px; transition: background 0.15s ease; }
  .tip:hover { background: rgba(255, 243, 176, 0.25); }
  .tip-bullet { flex-shrink: 0; width: 22px; height: 22px; margin-top: 3px; display: flex; align-items: center; justify-content: center; font-family: "Caveat", cursive; font-size: 22px; color: var(--pencil); font-weight: 700; }
  .tip-content { flex: 1; font-family: "Patrick Hand", cursive; font-size: 19px; line-height: 1.45; }
  .tip-title { font-weight: 700; position: relative; display: inline; background-image: linear-gradient(transparent 70%, var(--accent-yellow) 70%); padding: 0 2px; }
  code { background: var(--paper); color: #b85c3a; padding: 1px 7px; border-radius: 4px; font-family: "JetBrains Mono", "SF Mono", Menlo, Consolas, monospace; font-size: 14px; border: 1px dashed #d4b8a8; }
  em { font-style: italic; font-weight: 500; }
  footer { text-align: center; color: var(--ink-soft); font-family: "Caveat", cursive; font-size: 20px; margin-top: 50px; padding-top: 20px; border-top: 2px dashed var(--border-soft); }
  /* Impression / export PDF via window.print() */
  @media print {
    @page { size: A4; margin: 12mm 10mm; }
    html, body {
      background: var(--paper) !important;
      font-size: 13pt;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
    .top-bar { display: none !important; }
    .container {
      max-width: 100%;
      margin: 0;
      padding: 0 10px;
      min-height: auto;
      box-shadow: none;
      border: none;
      background-image: none; /* on retire les lignes de cahier en print */
    }
    .container::before { display: none; }
    header { margin-bottom: 18px; padding-bottom: 12px; }
    h1 { font-size: 30pt; }
    .badge { font-size: 12pt; }
    .subtitle { font-size: 12pt; }
    .section { margin-bottom: 14px; padding-left: 8px; }
    .tip { padding: 4px 0; margin-bottom: 0; page-break-inside: avoid; break-inside: avoid; }
    .tip-content { font-size: 12pt; line-height: 1.35; }
    .tip-bullet { font-size: 14pt; }
    code { font-size: 10pt; }
    footer { margin-top: 20px; padding-top: 10px; font-size: 11pt; }
  }
  @media (max-width: 700px) {
    .container { padding: 110px 28px 40px; }
    .container::before { left: 40px; }
    h1 { font-size: 34px; }
    .tip-content { font-size: 17px; }
    .download-btn { padding: 9px 16px; font-size: 17px; }
    .lang-switch a { width: 32px; height: 32px; font-size: 18px; }
  }
"""

PDF_SCRIPT = r"""
  function downloadPDF() { window.print(); }
"""


def render_lang_switch(lang: str, alt_lang: str | None, alt_href: str | None) -> str:
    """Construit le bloc HTML du sélecteur de langue, ou chaîne vide si pas d'alt.

    L'ordre des pills suit LANG_META (stable entre les pages) — seul le href
    et la classe `.active` changent selon la langue courante.
    """
    if not (alt_lang and alt_href):
        return ""

    hrefs = {alt_lang: alt_href}  # langue alternative → lien
    items = []
    for code, meta in LANG_META.items():
        if code == lang:
            items.append(
                f'  <a class="active" aria-current="page" title="{html.escape(meta["label"])}">{meta["flag"]}</a>'
            )
        elif code in hrefs:
            items.append(
                f'  <a href="{html.escape(hrefs[code])}" title="{html.escape(meta["label"])}">{meta["flag"]}</a>'
            )

    return (
        '<nav class="lang-switch" aria-label="Language">\n'
        + "\n".join(items)
        + '\n</nav>\n'
    )


def render_html(title: str, intro: str, bullets: list,
                lang: str, alt_lang: str | None, alt_href: str | None) -> str:
    tips_html = []
    for tip_title, tip_body in bullets:
        title_html = f'<span class="tip-title">{tip_title}</span> — ' if tip_title else ""
        tips_html.append(
            f'    <div class="tip">\n'
            f'      <div class="tip-bullet">{BULLET_CHAR}</div>\n'
            f'      <div class="tip-content">{title_html}{tip_body}</div>\n'
            f'    </div>'
        )
    tips_block = (
        '  <section class="section">\n'
        + "\n".join(tips_html)
        + "\n  </section>"
    )

    pdf_label = LANG_META.get(lang, {}).get("pdf_label", "Download as PDF")
    lang_switch = render_lang_switch(lang, alt_lang, alt_href)

    return f"""<!DOCTYPE html>
<html lang="{html.escape(lang)}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cheatsheet — {html.escape(title)}</title>
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@500;700&family=Patrick+Hand&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<div class="top-bar">
{lang_switch}<button class="download-btn" onclick="downloadPDF()">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="7 10 12 15 17 10"/>
    <line x1="12" y1="15" x2="12" y2="3"/>
  </svg>
  {html.escape(pdf_label)}
</button>
</div>

<div class="container" id="cheatsheet">

  <header>
    <div class="badge">✦ Cheatsheet ✦</div>
    <h1>{html.escape(title)}</h1>
    <p class="subtitle">{html.escape(intro)}</p>
  </header>

{tips_block}

  <footer>
    ✦ {html.escape(title)} ✦
  </footer>

</div>

<script>{PDF_SCRIPT}</script>

</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description="Génère une cheatsheet HTML à partir d'un markdown.")
    parser.add_argument("input", help="Fichier markdown source")
    parser.add_argument("output", nargs="?", help="Fichier HTML de sortie (défaut: input.html)")
    parser.add_argument("--lang", default="fr", help="Code langue de la page (défaut: fr)")
    parser.add_argument("--alt-lang", help="Code langue alternative pour le sélecteur (ex: en)")
    parser.add_argument("--alt-href", help="Lien vers la page alternative (ex: en.html)")
    args = parser.parse_args()

    src = Path(args.input)
    dst = Path(args.output) if args.output else src.with_suffix(".html")

    md = src.read_text(encoding="utf-8")
    title, intro, bullets = parse_markdown(md)
    html_out = render_html(title, intro, bullets, args.lang, args.alt_lang, args.alt_href)
    dst.write_text(html_out, encoding="utf-8")
    print(f"✓ {dst} généré ({len(bullets)} conseils)")


if __name__ == "__main__":
    main()
