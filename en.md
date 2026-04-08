# Optimizing token usage with Claude Code

A roundup of tricks to cut token consumption and better control your costs on Claude Code, sorted by difficulty.


- **Fresh sessions** — `/clear` between unrelated tasks.
- **Disconnect unused MCPs** — a single server can cost ~18,000 tokens/message. Prefer CLIs (e.g. Google Workspace CLI vs MCP Google Calendar).
- **Batch your prompts** — 3 separate messages = 3× more expensive than one combined message. Edit/regenerate instead of correcting in a follow-up.
- **Plan mode first** — keeps Claude from heading in the wrong direction. Add to `CLAUDE.md`: *"Don't make any changes until you're 95% confident"*.
- **`/context` and `/cost`** — see what's eating tokens (history, MCP, files). `/usage` in subscription mode.
- **Status line** — shows model, % context used, and rate limit live in the terminal.
- **Cloud dashboard** — check your usage every 20-30 min on *claude.ai > Settings > Usage*.
- **Be precise about what you paste** — don't dump a whole file when only one function is relevant.
- **Watch Claude** — stop it if it loops or heads the wrong way; this saves thousands of tokens.
- **Lean `CLAUDE.md` (<200 lines)** — treat it as an index with references to files, not the content itself.
- **Surgical references** — `@file.ts` + precise function name, don't say *"find the bug in my repo"*.
- **Compact at 60%** — autocompact triggers at 95% (too late). After 3-4 compacts, write a summary → `/clear` → resend the summary.
- **Mind the breaks** — the prompt cache expires after 5 min. Run `/compact` before stepping away.
- **Command outputs** — a `git log` can inject hundreds of lines into context. Use tools like RTK to summarize outputs.
- **Pick the right model** — Sonnet by default (80% of cases), Haiku for sub-agents/simple tasks, Opus for complex architecture/planning.
- **Sub-agent cost** — 7-10× more tokens than a standard session. Delegate simple tasks to Haiku.
- **Peak vs off-peak** — Peak = 2pm-8pm (FR time) on weekdays. Off-peak = after 8pm + weekends. Run heavy tasks off-peak. Before a reset, fire parallel agents to burn through what's left.
- **`CLAUDE.md` as source of truth** — store decisions, not conversations. Put your operating rules there (e.g. default model for sub-agents).
- **`--allowedTools` at launch** — restrict available tools and reduce system overhead.
- **Git worktrees to split work** — each subtask in its own branch/session, minimal context.
- **English prompts** — ~30% fewer tokens than French for the same content (more efficient tokenization).
- **Line limits in instructions** — e.g. *"summarize in 10 lines max"* to keep responses under control.
- **`--model` as a flag** — switch models on the fly without changing the global config.
