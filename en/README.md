<div class="hero">

<div class="hero-tag">WEB SECURITY LABS · WALKTHROUGHS</div>

# LabsTutorialNotes

<p class="hero-sub">Structured, reproducible notes for web security labs: environment setup, request analysis, source-code review, troubleshooting, and remediation.</p>

<p class="hero-stats">4 labs · 112 documented lessons · source analysis · troubleshooting · remediation</p>

<p class="hero-cta"><a class="cta-main" href="#/notes/sqli-labs/README.md">Start Learning →</a> <a class="cta-ghost" href="https://github.com/hacker369/LabsTutorialNotes">GitHub Repo</a></p>

</div>

<p class="lang-note">🌐 <strong>Note</strong>: the walkthrough content is primarily written in Chinese. Use the <strong>EN / 中文</strong> control in the top bar to switch the site interface.</p>

<div class="card-grid">

<a class="lab-card" href="#/notes/sqli-labs/README.md">
<div class="lab-icon">💉</div>
<div class="lab-name">SQLi-Labs</div>
<div class="lab-desc">SQL injection fundamentals, query contexts, error and UNION techniques, blind injection, filtering behavior, and source-code analysis.</div>
<span class="pill green">65 documented lessons</span><span class="pill">Chapter index</span>
</a>

<a class="lab-card" href="#/notes/xss-labs/README.md">
<div class="lab-icon">⚡</div>
<div class="lab-name">XSS-Labs</div>
<div class="lab-desc">Reflected XSS, HTML and JavaScript contexts, event attributes, encoding, filtering, and browser behavior.</div>
<span class="pill green">20 documented levels</span><span class="pill">Chapter index</span>
</a>

<a class="lab-card" href="#/notes/upload-labs/README.md">
<div class="lab-icon">📤</div>
<div class="lab-name">Upload-Labs</div>
<div class="lab-desc">File-upload validation, MIME and filename handling, server parsing behavior, race conditions, and defensive storage practices.</div>
<span class="pill green">21 documented passes</span><span class="pill">Chapter index</span>
</a>

<a class="lab-card" href="#/notes/google-xss-game/README.md">
<div class="lab-icon">🎯</div>
<div class="lab-name">Google XSS Game</div>
<div class="lab-desc">Browser contexts, DOM behavior, URL and attribute handling, and client-side input processing.</div>
<span class="pill green">6 documented levels</span><span class="pill">Chapter index</span>
</a>

</div>

## <span class="mono-h">// Quick Start</span>

<div class="quick-grid">

<div class="step-card">
<span class="step-num">STEP 01</span>
<h4>Prepare an isolated lab</h4>
<p>Check the lab source and versions of the operating system, PHP, database, and web server. Avoid exposing intentionally vulnerable services to the public internet.</p>
</div>

<div class="step-card">
<span class="step-num">STEP 02</span>
<h4>Reproduce and observe</h4>
<p>Record the request, response, visible behavior, and error messages. Separate observations from assumptions.</p>
</div>

<div class="step-card">
<span class="step-num">STEP 03</span>
<h4>Analyze and remediate</h4>
<p>Trace the input through the source code, explain the root cause, and document a fix with a verification method.</p>
</div>

</div>

## <span class="mono-h">// Learning Resources</span>

- [Setup guide](#/docs/setup.md) · [Troubleshooting](#/docs/troubleshooting.md)
- [Lab note template](#/docs/lab-note-template.md) · [Web security glossary](#/docs/glossary.md)
- [Maintenance guide](#/docs/MAINTENANCE.md)
- Related project: [VulhubTutorialNotes](https://hacker369.github.io/VulhubTutorialNotes.github.io/)

<div class="disclaimer">

<p><strong>⚠️ Disclaimer</strong></p>

<p>Use these notes only with local or explicitly authorized training labs, CTFs, and security research. Do not test real systems without authorization. Run intentionally vulnerable legacy applications in isolated virtual machines or containers.</p>

</div>

<p class="home-footer">Powered by Docsify · <a href="https://github.com/hacker369/LabsTutorialNotes">github.com/hacker369/LabsTutorialNotes</a></p>
