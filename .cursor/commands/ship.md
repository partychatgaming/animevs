# Commit and push with a changelog

Commit the current work and push it to GitHub. Do this only when this command is run.

## Inspect

Run these in parallel from the repo root:

- `git status`
- `git diff` and `git diff --staged`
- `git log -8 --oneline`
- `git rev-parse --abbrev-ref HEAD` and `git status -sb` so you know the branch and whether it tracks `origin`

Read the diff. Group the changes by what a player or editor would notice, not by file name.

## Commit message

Write a changelog, not a file list. Match the tone of recent commits.

- Subject: one sentence, about 50–72 characters, saying why the change exists.
- Body: a short paragraph, then 3–6 bullets. Each bullet is a user-facing change.
- Leave out secrets, tokens, passwords, and raw `.env` values.

Example:

```
Add a local editor for live card data

Players still battle the same records. This gives us a safe way to change them.

- Edit cards, titles, arms, summons, universes, bosses, and scenarios
- Pick elements from chips instead of typing them
- Reorder tale and dungeon fights by dragging
- Use one card image for focus and resolve
```

## Safety

- Do not change git config.
- Do not skip hooks, do not use `--no-verify`, and do not force-push.
- Do not commit `.env`, credentials, keys, or token files. If they are part of the change, leave them out and say so.
- If there is nothing to commit, do not create an empty commit. If the branch is ahead of `origin`, push the existing commits.
- Stage only the files that belong in this changelog.

## Commit and push

1. `git add` the relevant files.
2. Commit with a heredoc so the changelog keeps its line breaks:

```bash
git commit -m "$(cat <<'EOF'
Subject line here.

Why, in one or two sentences.

- Change
- Change

EOF
)"
```

3. If the commit fails because a hook rejected it, fix the problem and make a new commit. Do not amend.
4. Push the current branch: `git push -u origin HEAD` when it has no upstream, otherwise `git push`. Request permission for the network. If the push is rejected, stop and report the error. Do not force it.
5. Run `git status` after the push.

## Reply

Show the changelog you committed, the commit hash, the branch, and the GitHub URL for that commit (`https://github.com/partychatgaming/animevs/commit/<hash>`). If the push did not happen, say why.
