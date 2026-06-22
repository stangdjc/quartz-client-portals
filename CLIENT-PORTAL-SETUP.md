# Client Portal Setup

This Quartz repo is currently configured for the **SKN-Lab** portal.

## Current client scope
- Client tag: `client/SKN-Lab`
- Publish rule: notes must have `publish: true`
- Additional filter: notes must also carry the configured client tag (or an equivalent client field)
- Destination branch: `v5`

## Vault note requirements
A note must include both:

```yaml
publish: true
tags:
  - client/SKN-Lab
```

You can also scope a note with one of these frontmatter fields instead of `tags`:
- `client: client/SKN-Lab`
- `clientTag: client/SKN-Lab`
- `clientPortal: client/SKN-Lab`

## Export workflow
From the repo root:

```bash
python3 scripts/export_client_notes.py --source-root "$OBSIDIAN_VAULT_PATH"
```

Or via npm:

```bash
npm run export:client -- --source-root "$OBSIDIAN_VAULT_PATH"
```

What it does:
- scans the source vault for markdown notes
- selects only notes with `publish: true`
- keeps only notes scoped to `client/SKN-Lab`
- copies those notes into `content/exported/`
- copies linked local assets referenced by those exported notes when they can be resolved

## Publish loop
1. Add or update scoped notes in the Obsidian vault.
2. Run the export script.
3. Review the repo diff.
4. Commit and push to `v5`.
5. GitHub Pages publishes automatically.

## Cloning for the next client
When cloning this portal for another client:
1. duplicate the repo
2. change `client/SKN-Lab` in `quartz.config.yaml`
3. update `content/verification-pass.md`
4. update the GitHub repo URL, Pages URL, and branding as needed
5. run the export script against the new client tag
