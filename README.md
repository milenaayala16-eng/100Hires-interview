# Development Environment Setup — Cursor IDE

This repository was created as part of a technical evaluation to demonstrate the installation, configuration, and troubleshooting of the **Cursor IDE** development environment, including the integration of AI extensions for software development.

Below are the tools installed, the steps completed, and the technical challenges encountered during the process.

---

## Tools Installed

1. **Cursor IDE** — A code editor based on a fork of VS Code, optimized for AI-assisted development workflows.
2. **Claude Code (add-on)** — Official Anthropic extension for code assistance using Claude models, including guided refactoring and task automation.
3. **Codex / ChatGPT (add-on)** — OpenAI extension for code generation, natural-language queries, and function optimization (`openai.chatgpt` in the marketplace).
4. **Git & GitHub** — Version control and public hosting for this repository.

**Background:** Prior experience with **Visual Studio Code**; first time using **Cursor**.

---

## Steps Completed

1. **Download and install the IDE** — Downloaded the official Cursor installer from [cursor.com](https://cursor.com/) and completed the standard installation on Windows.
2. **GitHub account setup** — Created and verified a GitHub profile, then created this public repository to store interview deliverables.
3. **Terminal / CLI configuration** — Added Cursor to the system `PATH` so it can be launched from the terminal.
4. **Extension installation via CLI** — Installed the required add-ons using the Cursor CLI and package identifiers (see [Issues and solutions](#issues-encountered-and-solutions-applied)).
5. **GitHub authentication** — Signed in to GitHub in the local environment (`gh auth login` as `milenaayala16-eng`) and configured Git to use GitHub CLI for HTTPS pushes.
6. **Open repository and verify** — Opened the project from the terminal with `cursor ./` to load the workspace and confirm extensions were active in the session.
7. **Version control** — Documented the process in this `README.md`, committed changes (`git commit`), and published to the remote (`git push`).

---

## Issues Encountered and Solutions Applied

During setup, several technical issues required research and troubleshooting.

### 1. Extensions not visible in the marketplace

- **Problem:** Searching for `"Claude Code"` and `"Codex"` in the Extensions marketplace inside Cursor returned no results or did not list the add-ons directly.
- **Investigation:** Because Cursor is compatible with the VS Code extension architecture, I looked into installing extensions from the command line, similar to `code --install-extension` in VS Code.
- **Solution:**
  - Configured the system `PATH` so the terminal recognizes the Cursor binary globally.
  - Installed the extensions via CLI using their package IDs:

```bash
cursor --install-extension anthropic.claude-code
cursor --install-extension openai.chatgpt
```

- **Verification:** Ran `cursor --list-extensions` to confirm both extensions were installed.

### 2. Workspace context and extension visibility

- **Problem:** Opening Cursor from the desktop shortcut sometimes started with an empty workspace, and extensions installed from the terminal did not always appear immediately in the UI.
- **Finding:** Launching the IDE from the repository folder with:

```bash
cursor ./
```

loads the correct working directory context. This made it possible to confirm in the sidebar that both extensions were installed and active for the session.

### 3. Git push authentication (403)

- **Problem:** `git push` failed with `Permission denied to LucasOlivera-andreani` because Windows Credential Manager was using a different GitHub account than the repository owner (`milenaayala16-eng`).
- **Solution:**
  - Signed in with GitHub CLI: `gh auth login` (account `milenaayala16-eng`).
  - Ran `gh auth setup-git` so Git uses `gh` for GitHub credentials.
  - Removed stale `git:https://github.com` credentials for the other account from Windows Credential Manager, then pushed again successfully as Milena.

---

## Evidence

Claude Code extension installed and visible in Cursor:

![Claude Code add-on](./img/claude-code-addon.png)

Codex / ChatGPT extension installed and visible in Cursor:

![Codex add-on](./img/codex-addon.png)
