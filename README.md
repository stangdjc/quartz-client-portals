# Quartz Client Portals

Publish notes from an Obsidian vault to a client-facing website. Each portal is scoped to a single client.

- Repo: `stangdjc/quartz-client-portals` (private)
- Site: `https://quartz-client-portals.stangdjc.workers.dev/` (Cloudflare Workers, static assets)
- Deploy branch: `v5` (Cloudflare builds and deploys on every push)
- Client scope: `client/SKN-Lab` (set in `quartz.config.yaml`, `clientTag`)

---

## TL;DR: publish in one step

In Obsidian, give the note these two properties:

```yaml
---
publish: true
tags:
  - client/SKN-Lab
---
```

Then run **one command** from anywhere (or press your Obsidian hotkey, see below):

```bash
bash ~/quartz-client-portals/scripts/publish.sh
```

The command:

1. switches to `v5` and pulls the latest (safe to use on both Macs)
2. exports every matching note, plus embedded images and PDFs
3. builds the site to catch errors
4. commits and pushes. Cloudflare deploys in about 1–2 minutes.

| Want to…                                      | Command                                                      |
| --------------------------------------------- | ------------------------------------------------------------ |
| Publish                                       | `bash ~/quartz-client-portals/scripts/publish.sh`            |
| Preview locally first (http://localhost:8080) | `bash ~/quartz-client-portals/scripts/publish.sh --preview`  |
| See what would change without committing      | `bash ~/quartz-client-portals/scripts/publish.sh --dry-run`  |
| Unpublish a note                              | Set `publish: false` (or remove the tag), then publish again |

> The export mirrors the vault. Notes that no longer qualify are removed from `content/exported/` on the next run.

### Hotkey publishing from Obsidian

1. Install the community plugin **Shell commands**.
2. Add the command: `bash ~/quartz-client-portals/scripts/publish.sh`
3. Assign a hotkey, for example `⌘⇧P`. Publishing now happens without leaving Obsidian.

Set `OBSIDIAN_VAULT_PATH` if the vault is not at `~/Obsidian-Vault-V2`.

---

## Publish rule (fail-closed)

A note goes live **only** when both are true:

1. `publish: true`
2. It carries this portal's client tag, either in `tags` or in one of `client:`, `clientTag:` or `clientPortal:`.

The rule is enforced twice: by `scripts/export_client_notes.py`, which decides what leaves the vault, and by `local-plugins/client-portal-filter` at build time, which catches anything placed in `content/` by hand.

Recommended Templater base: `Obsidian-Vault-V2/RESOURCE/Templates/Quartz Client Portal Note.md`

---

## Privacy model

| Layer                 | Who can see it                                                                       |
| --------------------- | ------------------------------------------------------------------------------------ |
| Vault                 | You only. Nothing leaves it without `publish: true` + client tag.                    |
| GitHub repo (private) | You and your collaborators: raw markdown with **all** frontmatter, plus full history |
| Site                  | Anyone with the URL, unless Cloudflare Access is on (recommended, see step 5 below)  |
| Single page           | Add `password: <secret>` to a note's frontmatter to encrypt that page in the browser |

The site only displays the `description`, `tags` and `aliases` properties. Other frontmatter such as `person:` is not shown on the site.

---

## Cloudflare setup (one time)

Do these steps **in order**. The old GitHub Pages site stays up until step 4, so there's no downtime.

**1. Connect the repo to Cloudflare**

- Cloudflare dashboard → **Workers & Pages → Create → Import a repository** → select `stangdjc/quartz-client-portals`
- Production branch: `v5`
- Build command: `npx quartz plugin install && npx quartz build`
- Deploy command: `npx wrangler deploy` (the default). It reads [`wrangler.jsonc`](./wrangler.jsonc).
- Build variable: `NODE_VERSION` = `22`

**2. Confirm the URL.** After the first deploy, open the `*.workers.dev` URL Cloudflare shows. If it differs from the `baseUrl` in `quartz.config.yaml` / `homepage` in `package.json`, update both and publish again. The base URL feeds the sitemap, RSS and social previews.

**3. Make the repo private.** GitHub → repo **Settings → General → Danger Zone → Change visibility → Private**. The Cloudflare integration keeps working.

**4. Turn off GitHub Pages.** GitHub → **Settings → Pages → Unpublish site** (on the free plan, making the repo private may already have done this). The old `stangdjc.github.io/quartz-client-portals` URL then stops working.

**5. (Recommended) Restrict the site to invited people with Cloudflare Access.** Worker → **Settings → Domains & Routes → workers.dev → Enable Cloudflare Access**, then allow specific client emails. Visitors get a one-time code by email. Access is free for up to 50 users.

---

## Spin up a portal for a new client

1. Create a new **private** GitHub repo (for example `quartz-acme-co`) and push a copy of this repo to it.
2. Update:

   | File                           | Change                                         |
   | ------------------------------ | ---------------------------------------------- |
   | `wrangler.jsonc`               | `name` (becomes the `*.workers.dev` subdomain) |
   | `quartz.config.yaml`           | `baseUrl`, `clientTag`, `pageTitle`            |
   | `package.json`                 | `homepage`, `repository.url`                   |
   | `content/index.md`             | Landing-page wording and "Start here" link     |
   | `content/verification-pass.md` | Positive test tag                              |
   | `README.md`                    | Header block above                             |

3. Follow **Cloudflare setup** steps 1, 2 and 5.
4. Tag notes `client/Acme-Co` and run `scripts/publish.sh` from the new repo.

Example base URL for a new portal:

```yaml
baseUrl: quartz-acme-co.stangdjc.workers.dev
```

Moving this repo to another GitHub org: see [`CASIL-MIGRATION.md`](./CASIL-MIGRATION.md).

---

## Verification checklist

- [ ] `quartz.config.yaml` has the right `clientTag`
- [ ] `content/verification-pass.md` builds and `content/verification-blocked.md` is filtered out (the build log says `Filtered out 1 files`)
- [ ] `scripts/publish.sh` finishes, and the Cloudflare deploy for that commit succeeds
- [ ] The live URL loads, and prompts for login if Access is on

## Key files

| File                                          | Role                                                         |
| --------------------------------------------- | ------------------------------------------------------------ |
| `scripts/publish.sh`                          | One-step sync → export → build → commit → push               |
| `scripts/export_client_notes.py`              | Copies only matching notes and their assets out of the vault |
| `scripts/run_export_universal.sh`             | Auto-finds the repo and vault, then runs the export          |
| `local-plugins/client-portal-filter/index.js` | Build-time fail-closed filter                                |
| `quartz.config.yaml`                          | Base URL, client tag, plugins, theme                         |
| `wrangler.jsonc`                              | Cloudflare Workers static-assets config                      |
| `docs/`                                       | Upstream Quartz docs (reference only, not published)         |

Upstream Quartz docs: https://quartz.jzhao.xyz/
