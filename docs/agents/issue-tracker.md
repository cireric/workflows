# Issue tracker: Local markdown

Issues and PRDs for this repo live as markdown files under `.scratch/<feature>/`. No remote issue tracker.

## Conventions

- **Create an issue**: Create a file at `.scratch/<feature>/<slug>.md` with a YAML front-matter block containing `status`, `labels` (a list), and any other metadata, followed by the issue body in markdown.
- **Read an issue**: Read the file at `.scratch/<feature>/<slug>.md`.
- **List issues**: Glob `.scratch/**/*.md` and parse front-matter. Filter by `status` and `labels` as needed.
- **Comment on an issue**: Append to the file's `## Comments` section (create it if absent).
- **Apply / remove labels**: Edit the `labels` list in the front-matter.
- **Close**: Set `status: closed` in the front-matter and optionally add a closing comment.

## Pull requests as a triage surface

Not applicable — no remote, no PRs.

## When a skill says "publish to the issue tracker"

Create a markdown file under `.scratch/<feature>/`.

## When a skill says "fetch the relevant ticket"

Read the corresponding `.scratch/<feature>/<slug>.md` file.
