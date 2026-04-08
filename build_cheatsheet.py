#!/usr/bin/env python3
"""
Génère un shell HTML statique (`docs/index.html`) qui charge dynamiquement
`fr.md` et `en.md` côté navigateur pour rendre la cheatsheet.

Le sélecteur de langue (pills 🇫🇷 / 🇬🇧) bascule le contenu sans rechargement
de page. Le bouton « Télécharger en PDF » utilise `window.print()`.

Usage :
    python3 build_cheatsheet.py
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
SOURCES = ["fr.md", "en.md"]


# --- CSS (inchangé hormis quelques ajustements) -------------------------------

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
  .lang-switch button {
    display: inline-flex; align-items: center; justify-content: center;
    width: 38px; height: 38px; border-radius: 50%;
    background: transparent; border: none; cursor: pointer;
    font-size: 22px; line-height: 1; padding: 0;
    filter: grayscale(0.55); opacity: 0.55;
    transition: filter 0.15s ease, opacity 0.15s ease, background 0.15s ease;
  }
  .lang-switch button:hover { filter: grayscale(0); opacity: 1; }
  .lang-switch button.active {
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
  /* État de chargement / erreur */
  .cs-loading, .cs-error {
    text-align: center; padding: 40px 20px;
    font-family: "Caveat", cursive; font-size: 24px; color: var(--ink-soft);
  }
  .cs-error { color: #b85c3a; }
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
    .lang-switch button { width: 32px; height: 32px; font-size: 18px; }
  }
"""


# --- JS : parsing markdown + rendu + lang switch ------------------------------

JS = r"""
(() => {
  const LANG_META = {
    fr: { flag: "🇫🇷", label: "Français", pdfLabel: "Télécharger en PDF", file: "fr.md" },
    en: { flag: "🇬🇧", label: "English",  pdfLabel: "Download as PDF",   file: "en.md" },
  };
  const DEFAULT_LANG = "fr";
  const STORAGE_KEY = "cheatsheet-lang";

  const cache = {}; // lang -> parsed object

  // --- Markdown parsing -------------------------------------------------------

  function escapeHtml(s) {
    return s
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function inlineMd(text) {
    const placeholders = [];
    text = text.replace(/`([^`]+)`/g, (_, code) => {
      placeholders.push(`<code>${escapeHtml(code)}</code>`);
      return `\u0000${placeholders.length - 1}\u0000`;
    });
    text = escapeHtml(text);
    text = text.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    text = text.replace(/(^|[^*])\*([^*]+)\*(?!\*)/g, "$1<em>$2</em>");
    text = text.replace(/\u0000(\d+)\u0000/g, (_, i) => placeholders[+i]);
    return text;
  }

  function splitBullet(b) {
    const m = b.match(/^\*\*(.+?)\*\*\s*[—–-]\s*(.*)$/);
    if (m) return { title: inlineMd(m[1]), body: inlineMd(m[2]) };
    return { title: "", body: inlineMd(b) };
  }

  function parseMarkdown(md) {
    let title = "";
    const introLines = [];
    const bullets = [];
    for (const raw of md.split("\n")) {
      const line = raw.replace(/\s+$/, "");
      if (!line.trim()) continue;
      if (line.startsWith("# ")) {
        title = line.slice(2).trim();
      } else if (line.trimStart().startsWith("- ")) {
        bullets.push(line.trimStart().slice(2).trim());
      } else if (bullets.length === 0) {
        introLines.push(line.trim());
      }
    }
    return {
      title,
      intro: introLines.join(" "),
      bullets: bullets.map(splitBullet),
    };
  }

  // --- Rendu ------------------------------------------------------------------

  function render(parsed, lang) {
    document.documentElement.lang = lang;
    document.title = `Cheatsheet — ${parsed.title}`;

    document.getElementById("cs-title").textContent = parsed.title;
    document.getElementById("cs-subtitle").textContent = parsed.intro;
    document.getElementById("cs-footer").textContent = `✦ ${parsed.title} ✦`;
    document.getElementById("pdf-label").textContent = LANG_META[lang].pdfLabel;

    const section = document.getElementById("cs-section");
    section.innerHTML = parsed.bullets
      .map(({ title, body }) => {
        const titleHtml = title ? `<span class="tip-title">${title}</span> — ` : "";
        return (
          `<div class="tip">` +
          `<div class="tip-bullet">✓</div>` +
          `<div class="tip-content">${titleHtml}${body}</div>` +
          `</div>`
        );
      })
      .join("\n");

    // Met à jour les pills (active state)
    document.querySelectorAll(".lang-switch button").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.lang === lang);
      if (btn.dataset.lang === lang) btn.setAttribute("aria-current", "page");
      else btn.removeAttribute("aria-current");
    });
  }

  function showError(msg) {
    const section = document.getElementById("cs-section");
    section.innerHTML = `<div class="cs-error">${escapeHtml(msg)}</div>`;
  }

  // --- Chargement -------------------------------------------------------------

  async function loadLang(lang) {
    if (cache[lang]) return cache[lang];
    const res = await fetch(LANG_META[lang].file, { cache: "no-cache" });
    if (!res.ok) throw new Error(`HTTP ${res.status} on ${LANG_META[lang].file}`);
    const md = await res.text();
    const parsed = parseMarkdown(md);
    cache[lang] = parsed;
    return parsed;
  }

  async function setLang(lang) {
    if (!LANG_META[lang]) lang = DEFAULT_LANG;
    try {
      const parsed = await loadLang(lang);
      render(parsed, lang);
      try { localStorage.setItem(STORAGE_KEY, lang); } catch (_) {}
      const url = new URL(window.location.href);
      url.searchParams.set("lang", lang);
      history.replaceState(null, "", url);
    } catch (e) {
      console.error(e);
      showError(`Impossible de charger ${LANG_META[lang].file} — ${e.message}`);
    }
  }

  function initialLang() {
    const params = new URLSearchParams(window.location.search);
    const fromUrl = params.get("lang");
    if (fromUrl && LANG_META[fromUrl]) return fromUrl;
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored && LANG_META[stored]) return stored;
    } catch (_) {}
    const nav = (navigator.language || "").slice(0, 2);
    if (LANG_META[nav]) return nav;
    return DEFAULT_LANG;
  }

  window.downloadPDF = () => window.print();

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".lang-switch button").forEach((btn) => {
      btn.addEventListener("click", () => setLang(btn.dataset.lang));
    });
    setLang(initialLang());
  });
})();
"""


# --- HTML shell ---------------------------------------------------------------

HTML = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cheatsheet</title>
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@500;700&family=Patrick+Hand&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<div class="top-bar">
  <nav class="lang-switch" aria-label="Language">
    <button type="button" data-lang="fr" title="Français">🇫🇷</button>
    <button type="button" data-lang="en" title="English">🇬🇧</button>
  </nav>
  <button class="download-btn" onclick="downloadPDF()">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
      <polyline points="7 10 12 15 17 10"/>
      <line x1="12" y1="15" x2="12" y2="3"/>
    </svg>
    <span id="pdf-label">Télécharger en PDF</span>
  </button>
</div>

<div class="container" id="cheatsheet">

  <header>
    <div class="badge">✦ Cheatsheet ✦</div>
    <h1 id="cs-title">…</h1>
    <p class="subtitle" id="cs-subtitle"></p>
  </header>

  <section class="section" id="cs-section">
    <div class="cs-loading">Chargement…</div>
  </section>

  <footer id="cs-footer">✦</footer>

</div>

<script>{JS}</script>

</body>
</html>
"""


def main():
    DOCS.mkdir(exist_ok=True)
    (DOCS / "index.html").write_text(HTML, encoding="utf-8")
    print(f"✓ {DOCS / 'index.html'} généré")

    for name in SOURCES:
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, DOCS / name)
            print(f"✓ {DOCS / name} copié")
        else:
            print(f"⚠ {src} introuvable, ignoré")


if __name__ == "__main__":
    main()
