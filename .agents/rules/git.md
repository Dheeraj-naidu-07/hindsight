---
trigger: always_on
---

# Git Rules

- **Branching**: Use feature branches. Never push directly to `main` or `master`.
- **Focused commits**: Commits should represent a single logical change. Write descriptive commit messages.
- **Pull requests**: All code must go through a pull request (PR) and be reviewed before merging.
- **Code review**: Review code thoroughly according to the `code-review.md` guidelines.
- **Merge conflicts**: Resolve conflicts carefully. Communicate with the author of the conflicting changes if unsure.
- **Protected main branches**: `main` must be protected, requiring status checks (tests/linting) to pass before merging.
- **No secrets**: Never commit secrets or `.env` files containing sensitive data. Use `.gitignore`.
- **No unnecessary force pushes**: Do not force push to shared branches unless you are the only one working on them.
- **Safe collaboration**: Pull frequently to stay up to date. Communicate breaking changes to the team.
