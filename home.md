<div class="hero">

<div class="hero-tag">WEB SECURITY LABS · SOURCE ANALYSIS · REPRODUCIBLE NOTES</div>

# LabsTutorialNotes

<p class="hero-sub">从环境搭建、请求分析，到漏洞原理、复现排错与安全修复。记录的不只是测试输入，更是每一步背后的原因。</p>

<p class="hero-stats">4 大靶场 · 122 个标注关卡 · 源码分析 · 环境排错 · 安全修复</p>

<p class="hero-cta"><a class="cta-main" href="#/notes/sqli-labs/README.md">开始学习 →</a> <a class="cta-ghost" href="https://github.com/hacker369/LabsTutorialNotes">GitHub 源码</a></p>

</div>

<div class="card-grid">

<a class="lab-card" href="#/notes/sqli-labs/README.md">
<div class="lab-icon">💉</div>
<div class="lab-name">sqli-labs</div>
<div class="lab-desc">SQL 注入基础与进阶：查询上下文、报错与联合查询、盲注、过滤逻辑及版本差异。</div>
<span class="pill green">75 关标注</span><span class="pill">源码分析</span><span class="pill">排错记录</span>
</a>

<a class="lab-card" href="#/notes/xss-labs/README.md">
<div class="lab-icon">⚡</div>
<div class="lab-name">xss-labs</div>
<div class="lab-desc">理解输入如何进入 HTML 与 JavaScript 上下文，以及浏览器解析、编码与过滤的影响。</div>
<span class="pill green">20 关标注</span><span class="pill">输出上下文</span><span class="pill">防御思路</span>
</a>

<a class="lab-card" href="#/notes/upload-labs/README.md">
<div class="lab-icon">📤</div>
<div class="lab-name">upload-labs</div>
<div class="lab-desc">分析上传校验、MIME、文件名处理、解析配置和操作系统差异，并总结安全存储策略。</div>
<span class="pill green">21 关标注</span><span class="pill">环境差异</span><span class="pill">安全配置</span>
</a>

<a class="lab-card" href="#/notes/google-xss-game/README.md">
<div class="lab-icon">🎯</div>
<div class="lab-name">Google XSS Game</div>
<div class="lab-desc">通过浏览器挑战理解 DOM、页面上下文和输入解析，练习从现象反推原理。</div>
<span class="pill green">6 关标注</span><span class="pill">浏览器行为</span><span class="pill">综合练习</span>
</a>

</div>

## <span class="mono-h">// 推荐学习路线</span>

<div class="quick-grid">

<div class="step-card">
<span class="step-num">STEP 01</span>
<h4>准备隔离环境</h4>
<p>先核对操作系统、PHP、数据库与 Web 服务版本。建议使用专用虚拟机或容器，不要把故意存在漏洞的实验服务暴露到公网。</p>
</div>

<div class="step-card">
<span class="step-num">STEP 02</span>
<h4>复现并观察</h4>
<p>记录请求、响应、页面现象和错误信息。将已验证的结果与待验证的推论分开，避免只记忆单一 Payload。</p>
</div>

<div class="step-card">
<span class="step-num">STEP 03</span>
<h4>分析并修复</h4>
<p>回到源码追踪输入数据流，解释根因，再总结安全修复和验证方式。排错可从侧栏进入环境指南与故障排查手册。</p>
</div>

</div>

## <span class="mono-h">// 工具箱</span>

- [环境搭建指南](#/docs/setup.md) · [故障排查](#/docs/troubleshooting.md)
- [实验笔记模板](#/docs/lab-note-template.md) · [Web 安全术语表](#/docs/glossary.md)
- [仓库维护规范](#/docs/MAINTENANCE.md) · [提交问题或建议](https://github.com/hacker369/LabsTutorialNotes/issues/new/choose)

<div class="disclaimer">

<p><strong>⚠️ 免责声明</strong></p>

<p>本项目仅供本地或明确授权的教学靶场、CTF 与安全研究使用。请勿对未授权的真实系统进行测试。运行故意存在漏洞的旧版应用时，请使用隔离的虚拟机或容器，并避免暴露到公网。</p>

</div>

<p class="home-footer">Powered by Docsify · <a href="https://github.com/hacker369/LabsTutorialNotes">github.com/hacker369/LabsTutorialNotes</a></p>
