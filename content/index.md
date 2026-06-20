---
title: Quartz Client Portals
publish: true
---

# Quartz Client Portals

This is the shared Quartz deployment template for client-specific portals.

## How it works

- Keep the source vault in Obsidian.
- Sync only the notes tagged for a specific client into this repo's `content/` folder.
- Build and deploy the site from this repo so each client gets a separate publish surface.

## Baseline workflow

1. Set the portal tag in `quartz.config.yaml` (replace `client/template` with the real client tag).
2. Add `publish: true` plus that client tag to every note meant for this portal.
3. Copy or sync only those notes into this repo.
4. Commit and push to `v5`.
5. GitHub Pages publishes the site automatically.

## Notes

- This repo is meant to be cloned per client.
- Quartz now fails closed: only notes with `publish: true` and the configured client tag are published.
- Replace `client/template` in `quartz.config.yaml` before using a cloned portal.
- Keep client repositories isolated so content never bleeds between sites.
