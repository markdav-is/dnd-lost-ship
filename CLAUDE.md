## Local-only — no cloud sessions

This repo is worked on from the owner's local machine only, never from a
Claude Code cloud/remote session (claude.ai/code web, mobile, Slack, or a
GitHub Action trigger). If you find yourself running in a managed remote
execution environment (a fresh container cloned from GitHub, no access to
the owner's actual local filesystem) on this repo: stop, tell the user this
looks like a cloud session, and ask them to instead run Claude Code locally
(the `claude` CLI, invoked from a terminal inside their real local clone)
before doing any work.

## Documentation lives in `/docs` (Wikidown wiki)

- The `/docs` folder is a Wikidown wiki — structured markdown with `.order`
  navigation files. CLI commands address pages in title form (`/Getting-Started/Format`),
  but markdown links *inside* pages must be relative with `.md` extensions so GitHub
  renders them: `[Format](../Getting-Started/Format.md)`, images `![x](../.attachments/pic.png)`.
- **Use the `wikidown` CLI, never an MCP server.** There is no wikidown MCP
  in this repo. Run title-path commands from PowerShell: Git Bash rewrites
  `/Some/Page` arguments into Windows paths.
- A `wikidown-editor` subagent and a `wikidown` skill (both CLI-based) are
  configured for this repo. Prefer them for reading and writing `/docs/*.md`.
- **Use the CLI for anything structural** (`wikidown new`, `move`, `delete`,
  `reorder`) so `.order` files, breadcrumbs, and inbound links stay
  consistent.
- **The tools are a convenience, not a rule.** When they get in the way — a
  bulk rename, a mechanical substitution across many pages, anything where
  running the tools costs more tokens than editing the files — edit
  `/docs/*.md` directly. Keep UTF-8 and line endings, and never hand-edit a
  page's `<!-- wikidown:breadcrumb -->` first line or a `.order` file.
- **Either way, finish by running the CLI to check the result:**
  `wikidown check-links` (and fix what it finds) before calling the work done.
  Its "outside the wiki; run check-links --fix" findings for `../../assets`
  sourcebook links are known; don't run `--fix` without asking.
- When you ship a feature that changes user-visible behavior, ask whether the
  wiki should be updated, and (if yes) delegate to `wikidown-editor`.
