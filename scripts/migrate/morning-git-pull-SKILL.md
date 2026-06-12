---
name: morning-git-pull
description: Morgonpull från GitHub kl. 07:05 — hämtar Mac Minis nattsynk innan arbetsdagen börjar.
---

You are performing an automated morning pull of the superintelligent-ai-os repository.

Repository path: /Users/thomasdalebring/Github/Superintelligent/superintelligent-ai-os

Steps:
1. Run `git pull --rebase origin main`.
2. If it succeeds with changes: report what was pulled (file names and commit messages).
3. If already up to date: report "Redan uppdaterat — inga nya ändringar."
4. If it fails due to conflicts or errors: report the exact error so the user can handle it manually.

Important rules:
- Never commit or push anything — this task only pulls.
- If there are local uncommitted changes that block the pull, report them — do not stash or discard automatically.
