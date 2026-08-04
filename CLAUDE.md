## Documentation lives in `/docs` (Wikidown wiki)

- The `/docs` folder is a Wikidown wiki — structured markdown with `.order`
  navigation files. Wiki tools address pages in title form (`/Getting-Started/Format`),
  but markdown links *inside* pages must be relative with `.md` extensions so GitHub
  renders them: `[Format](../Getting-Started/Format.md)`, images `![x](../.attachments/pic.png)`.
- A `wikidown-editor` subagent and a `wikidown` skill are configured for this
  repo. Use them for ANY read/write of `/docs/*.md`.
- Never edit `/docs/*.md` directly with `Write`/`Edit`. Use the `wiki_*` MCP
  tools so `.order` files stay consistent.
- When you ship a feature that changes user-visible behavior, ask whether the
  wiki should be updated, and (if yes) delegate to `wikidown-editor`.
