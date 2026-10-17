<div align="center">

# 🛡️ LabsTutorialNotes

**Web Security Labs · Source Code Analysis · Reproducible Notes**

Practical notes covering lab setup, request analysis, vulnerability mechanics, troubleshooting, and remediation.

[![License](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Docsify](https://img.shields.io/badge/Docs-Docsify-00e5ff.svg)](https://hacker369.github.io/LabsTutorialNotes/)
[![CI](https://github.com/hacker369/LabsTutorialNotes/actions/workflows/ci.yml/badge.svg)](https://github.com/hacker369/LabsTutorialNotes/actions/workflows/ci.yml)

**[Read Online](https://hacker369.github.io/LabsTutorialNotes/)** · **[Lab Index](#lab-index)** · **[Report an Issue](https://github.com/hacker369/LabsTutorialNotes/issues/new/choose)**

</div>

```text
root@LabsTutorialNotes:~$ cat project.info
scope     : web security training labs
approach  : reproduce -> inspect -> understand -> remediate
theme     : dark terminal / neon green / cyan
```

## Project Overview

LabsTutorialNotes is a collection of practical notes for local security labs and explicitly authorized training environments. The goal is to explain not only test inputs, but also environment versions, source-code behavior, observed requests and responses, troubleshooting, and defensive fixes.

## Lab Index

| Lab | Main Topics | Approx. Lessons* | Index and Existing Notes |
|---|---|:---:|---|
| 💉 **SQLi-Labs** | SQL injection, blind injection, query context and filtering | 65 | [Chapter index](./notes/sqli-labs/README.md) · [Existing full notes](./sqli-labs靶场通关笔记.md) |
| ⚡ **XSS-Labs** | Output context, reflected XSS, encoding and filters | 20 | [Lab index](./notes/xss-labs/README.md) · [Existing full notes](./xss-labs靶场通关笔记.md) |
| 📤 **Upload-Labs** | Upload validation, parser differences and race conditions | 21 | [Lab index](./notes/upload-labs/README.md) · [Existing full notes](./upload-labs靶场通关笔记.md) |
| 🎯 **Google XSS Game** | Browser context and DOM behavior | 6 | [Lab index](./notes/google-xss-game/README.md) · [Existing full notes](./GoogleXSSGame靶场通关笔记.md) |

<sub>*Lesson counts reflect the current notes and may differ across lab versions or forks. Verify against the source used for your environment.</sub>

For notes on vulnerable components and CVE-based environments, see the related project: [VulhubTutorialNotes](https://github.com/hacker369/VulhubTutorialNotes.github.io).

## Suggested Learning Path

1. Prepare an isolated environment with the [setup guide](./docs/setup.md).
2. Use each lab index to find the relevant walkthrough.
3. Analyze the source, request, response, and actual observed behavior.
4. Record environment differences using the [troubleshooting guide](./docs/troubleshooting.md).
5. Document root cause and remediation with the [lab note template](./docs/lab-note-template.md).

## Read Locally

Requirements: Node.js and npm.

```bash
git clone https://github.com/hacker369/LabsTutorialNotes.git
cd LabsTutorialNotes
npx docsify-cli serve .
```

Open the local address printed by Docsify (usually `http://localhost:3000`).

## Repository Layout

```text
LabsTutorialNotes/
├── README.md / README_EN.md
├── index.html                 # Docsify entry and theme
├── home.md                    # Website landing page
├── _sidebar.md / _navbar.md   # Website navigation
├── notes/                     # Lab index pages
├── docs/                      # Setup, troubleshooting, template, glossary
├── sqli-labs靶场通关笔记.md    # Existing full notes retained during migration
├── xss-labs靶场通关笔记.md
├── upload-labs靶场通关笔记.md
├── GoogleXSSGame靶场通关笔记.md
├── img/                       # Existing screenshots
└── scripts/check_images.py    # Image reference and size checks
```

## Contributing

Issues and pull requests are welcome for broken links, version differences, typos, or steps that cannot be reproduced. Please include the lab version, relevant environment versions, observed behavior, and verification status. See [maintenance guidelines](./docs/MAINTENANCE.md).

## Safety

Use these notes only with local or explicitly authorized training labs, CTFs, and security research. Run intentionally vulnerable legacy applications in isolated virtual machines or containers and do not expose them to the public internet.

## License

[MIT License](./LICENSE). Referenced lab projects remain the property of their respective authors and are subject to their own licenses and terms.
