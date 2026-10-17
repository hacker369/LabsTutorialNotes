# xss-labs 靶场通关笔记

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

![1789717261593-6e9cd5b8-b8da-4c11-b06e-8952b102e660.png](../../img/285636619/1789717261593-6e9cd5b8-b8da-4c11-b06e-8952b102e660-343236.png)

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
