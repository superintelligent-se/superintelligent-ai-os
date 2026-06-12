---
name: nightly-github-sync
description: Nattlig GitHub-synk för superintelligent-ai-os — pullar senaste från GitHub, pushar lokala ändringar kl. 02:00.
---

You are performing an automated nightly sync of the superintelligent-ai-os repository to GitHub.

Repository path: /Users/miniautomation/Github/Superintelligent/superintelligent-ai-os

Steps:
1. Run `git pull --rebase origin main` to get any changes from the laptop or other sources. If this fails due to conflicts, stop and report — do not proceed.
2. Run `git status --porcelain`. If the output is empty (no local changes), stop here — nothing to commit.
3. If there are local changes, run `scripts/safety-check.sh`. If it fails or returns errors about private data, stop and do NOT commit.
4. Inspect changed files with `git diff --name-only HEAD`.
5. Generate a concise commit message:
   - First line: "chore: nightly sync [YYYY-MM-DD]"
   - Body: bullet list of what changed
6. Run: `git add -A && git commit -m "<your message>" && git push`
7. Report what was pulled, committed, and pushed — or why nothing was done.

Important rules:
- Always pull before pushing.
- Never commit if safety-check.sh fails.
- Never commit files containing email addresses, API keys, tokens, passwords, or personal data.
- Never force-push.
- If push fails due to diverged history, report the error — do not attempt to resolve manually.
