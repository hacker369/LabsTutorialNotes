<div class="hero">

<div class="hero-tag">WEB SECURITY LABS · WALKTHROUGH</div>

# LabsTutorialNotes

<p class="hero-sub">Web 安全经典靶场的<strong>完整通关实录</strong>——每一关都亲手打过：环境怎么搭、payload 为什么这样构造、失败了几次、最后怎么绕过，全部记录在案。</p>

<p class="hero-stats">4 大靶场 · 122 关全通 · 13,000+ 行笔记 · 700+ payload · 1,000+ 实操截图</p>

<p class="hero-cta"><a class="cta-main" href="#/sqli-labs靶场通关笔记.md">开始通关 →</a> <a class="cta-ghost" href="https://github.com/hacker369/LabsTutorialNotes">GitHub 源码</a></p>

</div>

<div class="card-grid">

<a class="lab-card" href="#/sqli-labs靶场通关笔记.md">
<div class="lab-icon">💉</div>
<div class="lab-name">sqli-labs</div>
<div class="lab-desc">SQL 注入从零到进阶：报错、联合查询、布尔/时间盲注、堆叠注入、宽字节与过滤绕过，75 关逐关实录。</div>
<span class="pill green">75 关</span><span class="pill">9,200 行</span><span class="pill">★★★☆☆</span>
</a>

<a class="lab-card" href="#/xss-labs靶场通关笔记.md">
<div class="lab-icon">⚡</div>
<div class="lab-name">xss-labs</div>
<div class="lab-desc">XSS 输出上下文思维训练：反射型注入、事件触发、标签闭合、编码对抗与过滤绕过，Level 1~20。</div>
<span class="pill green">20 关</span><span class="pill">820 行</span><span class="pill">★★☆☆☆</span>
</a>

<a class="lab-card" href="#/upload-labs靶场通关笔记.md">
<div class="lab-icon">📤</div>
<div class="lab-name">upload-labs</div>
<div class="lab-desc">文件上传攻防全景：前端校验绕过、MIME 检测、%00 截断、解析漏洞、.htaccess 与竞态条件，Pass 1~21。</div>
<span class="pill green">21 关</span><span class="pill">2,800 行</span><span class="pill">★★★☆☆</span>
</a>

<a class="lab-card" href="#/GoogleXSSGame靶场通关笔记.md">
<div class="lab-icon">🎯</div>
<div class="lab-name">Google XSS Game</div>
<div class="lab-desc">Google 官方闯关：真实浏览器环境下的上下文构造、DOM 惰性求值与提示利用，6 关全解。</div>
<span class="pill green">6 关</span><span class="pill">420 行</span><span class="pill">★★★☆☆</span>
</a>

</div>

## <span class="mono-h">// 快速开始</span>

<div class="quick-grid">

<div class="step-card">
<span class="step-num">STEP 01</span>
<h4>在线阅读</h4>
<p>零配置直接开看：<a href="#/sqli-labs靶场通关笔记.md">本站</a> 即为完整笔记，支持全文搜索与点击图片放大。</p>
</div>

<div class="step-card">
<span class="step-num">STEP 02</span>
<h4>搭建靶场</h4>
<p>Windows 推荐 phpStudy / XAMPP；少踩 PHP 版本坑就用 Docker，各笔记「安装」章节有现成命令。</p>
</div>

<div class="step-card">
<span class="step-num">STEP 03</span>
<h4>逐关复现</h4>
<p>按推荐路线开打：每关先自己尝试，再对照笔记复盘 payload 构造思路，速度查表见各笔记末章。</p>
</div>

</div>

## <span class="mono-h">// 推荐路线</span>

1. **sqli-labs** —— 建立注入探测与联合查询直觉
2. **xss-labs** —— 理解输出上下文与编码绕过
3. **upload-labs** —— 掌握前后端校验与解析差异
4. **Google XSS Game** —— 浏览器侧综合巩固
5. 进阶到组件漏洞：[VulhubTutorialNotes 笔记站](https://hacker369.github.io/VulhubTutorialNotes.github.io/)

<div class="disclaimer">

<p><strong>⚠️ 免责声明</strong></p>

<p>本笔记仅供在<strong>本地或已授权</strong>的教学靶场中学习使用，所有手法均针对故意存在漏洞的练习环境。请勿对未授权的真实系统进行测试或攻击，作者不对任何滥用行为负责。</p>

</div>

<p class="home-footer">Powered by Docsify · <a href="https://github.com/hacker369/LabsTutorialNotes">github.com/hacker369/LabsTutorialNotes</a></p>
