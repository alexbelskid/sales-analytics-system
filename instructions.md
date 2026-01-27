# Environment preferences (macOS + zsh/bash)

- OS: macOS
- Primary shell/terminal: zsh (default on macOS) or bash

## How to respond

- When giving commands, use Unix/POSIX syntax (bash/zsh compatible).
- Use Unix-style paths (e.g., `/Users/username/path/to/file`) and quote paths with spaces.
- Prefer portable commands that work in both bash and zsh.

## Shell conventions

- Env vars: `export NAME="value"`
- Chain commands: use `&&` for dependent commands, `;` for independent
- Exit code: check `$?` when needed
- Common commands:
  - `ls` — list files
  - `cat` — read file contents
  - `rm -rf` — remove recursively
  - `cp` — copy files
  - `mv` — move/rename files
  - `mkdir -p` — create directories (with parents)
  - `chmod` / `chown` — change permissions/ownership
  - `brew` — Homebrew package manager
