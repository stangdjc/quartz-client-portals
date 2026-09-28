# CASIL Migration Prep

Move the repo from `stangdjc` to the `CASIL` GitHub org.

Hosting is on Cloudflare, so **the site URL does not change** when the repo moves. Only the repo references and the Cloudflare Git connection need updating.

|        | Today                                | Target                        |
| ------ | ------------------------------------ | ----------------------------- |
| Repo   | `stangdjc/quartz-client-portals`     | `CASIL/quartz-client-portals` |
| Site   | unchanged (Cloudflare `workers.dev`) | unchanged                     |
| Branch | `v5`                                 | `v5`                          |

## Prerequisites

- You can transfer repos into the `CASIL` org.
- The Cloudflare GitHub app can be installed on the `CASIL` org, or the org grants it access.

## Steps

### 1) Transfer the repo

GitHub → `stangdjc/quartz-client-portals` → **Settings → General → Transfer ownership** → `CASIL`.

### 2) Update the local remote (on each Mac)

```bash
git -C ~/quartz-client-portals remote set-url origin https://github.com/CASIL/quartz-client-portals.git
```

### 3) Re-home repo references

```bash
cd ~/quartz-client-portals
python3 scripts/rehome_github_owner.py --owner CASIL          # dry run
python3 scripts/rehome_github_owner.py --owner CASIL --apply
git add README.md package.json
git commit -m "chore: rehome Quartz portal to CASIL org"
git push origin v5
```

### 4) Reconnect Cloudflare

Cloudflare dashboard → Worker → **Settings → Build → Git repository** → reconnect it to `CASIL/quartz-client-portals` (branch `v5`). Install the Cloudflare GitHub app on `CASIL` if you're prompted.

### 5) Verify

- Cloudflare shows a successful build for the push from step 3.
- The site loads and prompts for Access login if Access is on.
- `bash ~/quartz-client-portals/scripts/publish.sh --dry-run` runs cleanly.

## Files the re-home helper updates

- `README.md`: the `Repo:` line
- `package.json`: `repository.url`
