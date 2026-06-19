# 100Hires - junior growth marketing specialist

# Part 2

## Why I Chose These 10 Experts

When building this list, I tried to avoid sticking only to the first Google search results or "gurus" who just sell courses. I wanted to learn from people who are actually working on this every day in large companies or deeply researching how AI is changing everything.

Here is why I chose each of them:

**To understand the business and product:**
- **Kevin Indig**: Worked at Shopify and G2. I chose him because he clearly explains how SEO should serve to grow the company and not just bring empty traffic.
- **Eli Schwartz**: Author of the book *Product-Led SEO*. I found his approach of thinking about content from the product perspective incredibly useful.

**For content quality and avoiding penalties:**
- **Ryan Law**: Works at Ahrefs. His blog is exactly what I would like to achieve someday in a SaaS project, so reading what he does felt key.
- **Lily Ray**: Currently, she is the top expert on E-E-A-T. Since there is a lot of AI-generated spam content right now, researching what she says seemed super important to do things the right way.

**For mixing AI with SEO:**
- **Aleyda Solis**: She is a world-class expert and is publishing a lot on how to optimize for ChatGPT and new AI search engines.
- **Tomasz Niezgoda**: He is at Surfer (an AI tool for SEO). He is great for understanding how to use Artificial Intelligence tools to write faster while maintaining quality.

**For the technical and optimization side:**
- **Patrick Stox & Cyrus Shepard**: I added Patrick (from Ahrefs) and Cyrus (ex-Moz) because they explain the technical part of SEO in an easy-to-understand way, and I wanted to ensure the strategy had a solid on-page foundation.

**To build authority and stay organized:**
- **Jeremy Moser**: Talks a lot about link building (which always seemed really difficult to me) but focused on B2B companies.
- **Nathan Gotch**: I chose him because he explains very well how to build processes and systems step-by-step. He is great for learning how to be more methodical and not rush things.

**In summary:** I looked for people from whom I could learn practical things that work today, and I think the information I gathered from them is extremely valuable for putting together a future plan.

> **Note:** Initially, I attempted to scrape the profiles to automate data collection, but it wasn't possible due to rate limits on the Apify API, and additionally, the profiles were set to private.

---

# Part 1
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


## Evidence

Claude Code extension installed and visible in Cursor:

![Claude Code add-on](./img/claude-code-addon.png)

Codex / ChatGPT extension installed and visible in Cursor:

![Codex add-on](./img/codex-addon.png)
