# Experimental LLM Wiki Starter

This is a minimal content scaffold for a new LLM wiki. It shows the reusable project shape without copying the full website engine.

For a complete standalone project, run this from the repository root:

```bash
python3 scripts/create_wiki_project.py ../my-experimental-wiki --title "My Experimental Wiki" --topic "the domain I want to study"
```

The generated project includes the Vite website, wiki maintenance scripts, Cognee-ready session memory defaults, and seed markdown files.

## Included Here

```text
AGENTS.md
raw/sources/seed.md
wiki/index.md
wiki/how-to-use.md
wiki/log.md
wiki/source-notes/seed.md
```

Copy this folder when you only need the content schema. Use the script when you want a runnable website.
