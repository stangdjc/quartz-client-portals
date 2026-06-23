# CASIL Migration Prep

This repo is live today at:
- Repo: `https://github.com/stangdjc/quartz-client-portals`
- Pages: `https://stangdjc.github.io/quartz-client-portals/`
- Deploy branch: `v5`

Target state:
- Repo: `https://github.com/CASIL/quartz-client-portals`
- Pages: `https://casil.github.io/quartz-client-portals/`
- Deploy branch: `v5`

## What is already prepared
- `scripts/rehome_github_owner.py` can update the owner-specific URLs after transfer.
- The Quartz repo already deploys through GitHub Actions from `v5`.
- Export/publish flow is working for the SKN-Lab note set.

## Prerequisites
- You can transfer the repo into the `CASIL` org.
- The target org can host GitHub Pages.
- Local checkout has `gh` authenticated and git push access.

Optional but useful for org-verification work:
```bash
gh auth refresh -h github.com -s admin:org
```

## Safe migration sequence

### 1) Transfer the repo to CASIL
Safest path: GitHub web UI
- open `https://github.com/stangdjc/quartz-client-portals/settings`
- go to **General**
- use **Transfer ownership**
- transfer to `CASIL`

### 2) Update the local remote
```bash
cd ~/quartz-client-portals
git remote set-url origin https://github.com/CASIL/quartz-client-portals.git
git remote -v
```

### 3) Re-home owner-specific URLs
Dry run:
```bash
cd ~/quartz-client-portals
python3 scripts/rehome_github_owner.py --owner CASIL
```

Apply:
```bash
cd ~/quartz-client-portals
python3 scripts/rehome_github_owner.py --owner CASIL --apply
```

### 4) Rebuild locally
```bash
cd ~/quartz-client-portals
npm ci
npx quartz build
```

### 5) Commit and push the re-home patch
```bash
cd ~/quartz-client-portals
git add quartz.config.yaml package.json README.md ReadMe-Quartz.md
git commit -m "chore: rehome Quartz portal to CASIL org"
git push origin v5
```

### 6) Verify Pages in the transferred repo
In GitHub repo settings:
- **Pages** source should remain **GitHub Actions**
- Actions should still be enabled for the repo
- wait for the deploy workflow on branch `v5` to complete

### 7) Live verification
```bash
curl -I -L -s https://casil.github.io/quartz-client-portals/ | sed -n '1,10p'
curl -I -L -s https://casil.github.io/quartz-client-portals/exported/skn-lab-data-portal | sed -n '1,10p'
```

## Files the re-home helper updates
- `quartz.config.yaml`
  - `baseUrl`
  - footer GitHub repo link
- `package.json`
  - `homepage`
  - `repository.url`
- `README.md`
  - current repo URL
  - current Pages URL
- `ReadMe-Quartz.md`
  - repo URL
  - live site URL
  - example client repo base URL

## Known unknowns
- I have confirmed the `CASIL` org exists.
- I have **not** yet verified org admin rights from the current token, because that needs broader org scope.
- The current live site under `stangdjc` is healthy, so do the transfer first, then run the re-home helper.
