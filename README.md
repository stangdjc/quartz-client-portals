# Quartz Client Portals

Publish notes from an Obsidian vault to a client-facing website. Each portal is scoped to a single client.

- Repo: `stangdjc/quartz-client-portals`
- Pages: `https://stangdjc.github.io/quartz-client-portals/`
- Deploy branch: `v5` (GitHub Pages deploys on every push)
- Client scope: `client/SKN-Lab` (set in `quartz.config.yaml`, `clientTag`)

---

## TL;DR: publish in 2 steps

**1. In Obsidian, add two properties to the note:**

```yaml
---
publish: true
tags:
  - client/SKN-Lab
---
```

**2. Run one command:**

```bash
cd ~/quartz-client-portals && git checkout v5 && npm run publish:portal
```

That exports every matching note (plus embedded images/PDFs), builds the site, commits, and pushes. The site updates in about 1–2 minutes.

| Want to…                                      | Command                                                      |
| --------------------------------------------- | ------------------------------------------------------------ |
| Publish                                       | `npm run publish:portal`                                     |
| Preview locally first (http://localhost:8080) | `npm run preview:portal`                                     |
| See what would change without committing      | `bash scripts/publish.sh --dry-run`                          |
| Unpublish a note                              | Set `publish: false` (or remove the tag), then publish again |

> The export mirrors the vault. Notes that no longer qualify are removed from `content/exported/` on the next run.

---

## Publish rule (fail-closed)

A note goes live **only** when both are true:

1. `publish: true`
2. It carries this portal's client tag, either in `tags` or in one of `client:`, `clientTag:` or `clientPortal:`.

The rule is enforced twice: by `scripts/export_client_notes.py`, which decides what leaves the vault, and by `local-plugins/client-portal-filter` at build time, which catches anything placed in `content/` by hand.

Recommended Templater base: `Obsidian-Vault-V2/RESOURCE/Templates/Quartz Client Portal Note.md`

---

## ⚠️ Privacy: what's public

This GitHub repo is **public**. Anyone can read what's committed, including:

- the **full raw markdown** of every exported note, with **all frontmatter** (for example `person:`, `priority:`, `roi:`), even though the site only displays `description`, `tags` and `aliases`
- git history. Unpublishing removes a note from the site, but old commits still contain it.

Implications:

- Treat anything with `publish: true` + client tag as world-readable.
- The `encrypted-pages` plugin (`password:` frontmatter) is **not** real protection here, because the plaintext source sits in the public repo.
- For confidential client material, make the repo private and host the site on Cloudflare Pages or Netlify (both support private repos and access control), or keep that material out of the portal.

---

## One-click publishing from Obsidian (optional)

1. Install the community plugin **Shell commands**.
2. Add the command: `cd ~/quartz-client-portals && npm run publish:portal`
3. Assign a hotkey or add it to the command palette. Publishing then happens from inside Obsidian.

Set `OBSIDIAN_VAULT_PATH` if the vault is not at `~/Obsidian-Vault-V2`.

---

## Spin up a portal for a new client

1. Create a new GitHub repo (for example `quartz-acme-co`) and push a copy of this repo to it.
2. Update:

   | File                           | Change                                                                                                    |
   | ------------------------------ | --------------------------------------------------------------------------------------------------------- |
   | `quartz.config.yaml`           | `baseUrl` (for example `stangdjc.github.io/quartz-acme-co`), `clientTag`, `pageTitle`, footer GitHub link |
   | `package.json`                 | `homepage`, `repository.url`                                                                              |
   | `content/index.md`             | Landing-page wording                                                                                      |
   | `content/verification-pass.md` | Positive test tag                                                                                         |
   | `README.md`                    | Header block above                                                                                        |

3. In the new repo, set **Settings → Pages → Source: GitHub Actions**.
4. Tag notes `client/Acme-Co` and run `npm run publish:portal`.

Example base URL for a new portal:

```yaml
baseUrl: stangdjc.github.io/quartz-acme-co
```

Moving this repo to another GitHub org: see [`CASIL-MIGRATION.md`](./CASIL-MIGRATION.md).

---

## Verification checklist

- [ ] `quartz.config.yaml` has the right `clientTag`
- [ ] `content/verification-pass.md` builds and `content/verification-blocked.md` is filtered out (the build log says `Filtered out 1 files`)
- [ ] `npm run publish:portal` finishes, and the live URL returns HTTP 200

## Key files

| File                                          | Role                                                         |
| --------------------------------------------- | ------------------------------------------------------------ |
| `scripts/publish.sh`                          | One-command export → build → commit → push                   |
| `scripts/export_client_notes.py`              | Copies only matching notes and their assets out of the vault |
| `scripts/run_export_universal.sh`             | Auto-finds the repo and vault, then runs the export          |
| `local-plugins/client-portal-filter/index.js` | Build-time fail-closed filter                                |
| `quartz.config.yaml`                          | Base URL, client tag, plugins, theme                         |
| `.github/workflows/deploy.yml`                | GitHub Pages deploy on push to `v5`                          |
| `docs/`                                       | Upstream Quartz docs (reference only, not published)         |

Upstream Quartz docs: https://quartz.jzhao.xyz/
