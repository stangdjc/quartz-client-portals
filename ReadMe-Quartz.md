# ReadMe-Quartz

Quick reference for running the **Quartz client portal** repo at `/Users/dc-ai-lab/quartz-client-portals`.

## What this repo is
- **Repo:** `https://github.com/stangdjc/quartz-client-portals`
- **Live site:** `https://stangdjc.github.io/quartz-client-portals/`
- **Deploy branch:** `v5`
- **Current client scope:** `client/SKN-Lab`

## Publish rule
This repo is **fail-closed**.
A note publishes only when it has:

1. `publish: true`
2. the configured client scope, currently `client/SKN-Lab`

## Add a new note to this portal
Recommended Templater base:
- `/Users/dc-ai-lab/Obsidian-Vault-V2/RESOURCE/Templates/Quartz Client Portal Note.md`

Add frontmatter like this in the Obsidian note:

```yaml
---
publish: true
tags:
  - client/SKN-Lab
---
```

You can also scope the note with one of these instead of `tags`:

```yaml
client: client/SKN-Lab
```

```yaml
clientTag: client/SKN-Lab
```

```yaml
clientPortal: client/SKN-Lab
```

## Export notes from Obsidian into this repo
### Option A — direct path
```bash
cd /Users/dc-ai-lab/quartz-client-portals
python3 scripts/export_client_notes.py --source-root /Users/dc-ai-lab/Obsidian-Vault-V2
```

### Option B — env var + npm script
```bash
export OBSIDIAN_VAULT_PATH=/Users/dc-ai-lab/Obsidian-Vault-V2
cd /Users/dc-ai-lab/quartz-client-portals
npm run export:client
```

## Build locally
```bash
cd /Users/dc-ai-lab/quartz-client-portals
npm ci
npx quartz build
```

## Preview locally
```bash
cd /Users/dc-ai-lab/quartz-client-portals
python3 -m http.server 8000 -d public
```

Then open:
- `http://127.0.0.1:8000`

## Publish updated content
```bash
cd /Users/dc-ai-lab/quartz-client-portals
git status
git add .
git commit -m "docs: update client portal content"
git push origin v5
```

GitHub Pages deploys automatically from `v5`.

## Add a new client portal
Use this repo as the baseline, then clone it into a **new repo per client**.

### 1) Duplicate the repo
- create a new GitHub repo
- clone this repo into a new local folder
- point `origin` to the new repo

### 2) Change the client scope
Update these files:

| File | What to change |
|---|---|
| `quartz.config.yaml` | `baseUrl` and `clientTag` |
| `package.json` | `homepage` and `repository.url` |
| `content/index.md` | landing-page wording |
| `content/verification-pass.md` | positive test tag |
| `CLIENT-PORTAL-SETUP.md` | client tag, repo URL, Pages URL |
| `ReadMe-Quartz.md` | client tag, repo path, live URL |

### 3) Example new client swap
If the new client is `client/Acme-Co`, update:

```yaml
clientTag: client/Acme-Co
```

and set the Pages base URL to the new repo path, for example:

```yaml
baseUrl: stangdjc.github.io/quartz-acme-co
```

## Verification checklist
After any major change, verify:

- [ ] `quartz.config.yaml` has the right `clientTag`
- [ ] a note with `publish: true` and the right client tag is included
- [ ] a note for another client is excluded
- [ ] local build succeeds
- [ ] live site returns HTTP 200 after push

## Important files
- `quartz.config.yaml` — base URL + client filter config
- `local-plugins/client-portal-filter/index.js` — fail-closed client filter
- `scripts/export_client_notes.py` — export only matching notes/assets
- `CLIENT-PORTAL-SETUP.md` — operator notes
- `content/index.md` — landing page
- `content/verification-pass.md` — positive test page
- `content/verification-blocked.md` — negative test page

## Current working truth
This repo is the durable top-level working copy. The old Kanban workspace copy was promoted out of:
- `/Users/dc-ai-lab/.hermes/kanban/boards/medtronic-product-docs/workspaces/t_dba1bc2b/quartz-src`

Use the top-level repo for future edits:
- `/Users/dc-ai-lab/quartz-client-portals`
