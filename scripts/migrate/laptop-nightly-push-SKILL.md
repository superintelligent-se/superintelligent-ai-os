---
name: laptop-nightly-push
description: Nattlig push från laptopen till GitHub kl. 22:45 — pushar dagens ändringar innan Mac Minis nattsynk.
---

You are performing an automated nightly push of the superintelligent-ai-os repository from the laptop to GitHub.

Repository path: /Users/thomasdalebring/Github/Superintelligent/superintelligent-ai-os

Steps:
1. Run `git pull --rebase origin main` to get any remote changes first. If this fails due to conflicts, stop and report — do not proceed.
2. Run `git status --porcelain`. If empty, stop — nothing to push.
3. Run `scripts/safety-check.sh`. If it fails, stop and do NOT commit.
4. Inspect changed files with `git diff --name-only HEAD`.
5. Generate a concise commit message:
   - First line: "chore: laptop sync [YYYY-MM-DD]"
   - Body: bullet list of what changed
6. Run: `git add -A && git commit -m "<your message>" && git push`
7. Report what was committed and pushed, or why nothing was done.

Important rules:
- Always pull before pushing.
- Never commit if safety-check.sh fails.
- Never commit files containing email addresses, API keys, tokens, passwords, or personal data.
- Never force-push.
- If push fails, report — do not attempt to resolve manually.
