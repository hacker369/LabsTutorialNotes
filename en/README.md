<div class="hero">

<div class="hero-tag">WEB SECURITY LABS · WALKTHROUGH</div>

# LabsTutorialNotes

<p class="hero-sub">Complete hands-on walkthroughs of classic web security labs — every challenge solved personally: environment setup, payload construction, failed attempts, and the final bypass. All in one place.</p>

<p class="hero-stats">4 labs · 122 challenges cleared · 13,000+ lines · 700+ payloads · 1,000+ screenshots</p>

<p class="hero-cta"><a class="cta-main" href="#/sqli-labs靶场通关笔记.md">Start Level 1 →</a> <a class="cta-ghost" href="https://github.com/hacker369/LabsTutorialNotes">GitHub Repo</a></p>

</div>

<p class="lang-note">🌐 <strong>Note</strong>: the walkthrough content itself is written in Chinese (with plenty of screenshots). The site UI is bilingual — use the <strong>EN / 中文</strong> button in the top bar to switch.</p>

<div class="card-grid">

<a class="lab-card" href="#/sqli-labs靶场通关笔记.md">
<div class="lab-icon">💉</div>
<div class="lab-name">sqli-labs</div>
<div class="lab-desc">SQL injection from zero to advanced: error-based, UNION, boolean/time-based blind, stacked queries, charset tricks and filter bypass — all 75 challenges.</div>
<span class="pill green">75 levels</span><span class="pill">9,200 lines</span><span class="pill">★★★☆☆</span>
</a>

<a class="lab-card" href="#/xss-labs靶场通关笔记.md">
<div class="lab-icon">⚡</div>
<div class="lab-name">xss-labs</div>
<div class="lab-desc">Output-context thinking for XSS: reflected injection, event handlers, tag closing, encoding games and filter evasion — Level 1~20.</div>
<span class="pill green">20 levels</span><span class="pill">820 lines</span><span class="pill">★★☆☆☆</span>
</a>

<a class="lab-card" href="#/upload-labs靶场通关笔记.md">
<div class="lab-icon">📤</div>
<div class="lab-name">upload-labs</div>
<div class="lab-desc">File upload attack surface: client-side checks, MIME validation, null-byte truncation, parser vulnerabilities, .htaccess and race conditions — Pass 1~21.</div>
<span class="pill green">21 levels</span><span class="pill">2,800 lines</span><span class="pill">★★★☆☆</span>
</a>

<a class="lab-card" href="#/GoogleXSSGame靶场通关笔记.md">
<div class="lab-icon">🎯</div>
<div class="lab-name">Google XSS Game</div>
<div class="lab-desc">Google's official XSS challenge: context construction, DOM lazy evaluation and hint usage in a real browser environment — all 6 levels.</div>
<span class="pill green">6 levels</span><span class="pill">420 lines</span><span class="pill">★★★☆☆</span>
</a>

</div>

## <span class="mono-h">// Quick Start</span>

<div class="quick-grid">

<div class="step-card">
<span class="step-num">STEP 01</span>
<h4>Read online</h4>
<p>Zero setup: this site <a href="#/sqli-labs靶场通关笔记.md">is the full notes</a>, with full-text search and click-to-zoom screenshots.</p>
</div>

<div class="step-card">
<span class="step-num">STEP 02</span>
<h4>Set up the lab</h4>
<p>Windows: phpStudy / XAMPP. To avoid PHP version pitfalls use Docker — ready-made commands in each walkthrough's install chapter.</p>
</div>

<div class="step-card">
<span class="step-num">STEP 03</span>
<h4>Solve &amp; review</h4>
<p>Try each challenge yourself first, then compare with the notes. Cheat sheets live in the last chapter of every walkthrough.</p>
</div>

</div>

## <span class="mono-h">// Recommended Path</span>

1. **sqli-labs** — build injection instinct and UNION-query intuition
2. **xss-labs** — understand output contexts and encoding bypass
3. **upload-labs** — master validation gaps and parser quirks
4. **Google XSS Game** — consolidate browser-side XSS
5. Level up to real-world CVEs: [VulhubTutorialNotes](https://hacker369.github.io/VulhubTutorialNotes.github.io/)

<div class="disclaimer">

<p><strong>⚠️ Disclaimer</strong></p>

<p>These notes are for learning in <strong>local or properly authorized</strong> teaching labs only. Every technique targets intentionally vulnerable practice environments. Do <strong>not</strong> test or attack real systems without authorization. The author accepts no liability for misuse.</p>

</div>

<p class="home-footer">Powered by Docsify · <a href="https://github.com/hacker369/LabsTutorialNotes">github.com/hacker369/LabsTutorialNotes</a></p>
