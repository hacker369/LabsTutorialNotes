# Upload-Labs 通用方法论与防御

> 本文为 [Upload-Labs 学习索引](README.md) 的章节拆分。仅在本地或明确授权的靶场中练习。

---

## 4. 通用方法论（适合知识库沉淀）

### 4.1 分析顺序

1. 有无前端校验？→ 禁用 JS / 改包
2. 看 Content-Type / 扩展名 / 内容检测谁先谁后
3. 黑名单还是白名单？
4. 文件名是否保留？是否重命名？路径是否可控？
5. Web 服务器与 PHP 版本、系统（Win/Linux）决定哪些后缀与截断有效
6. 上传成功后如何**执行**（直接解析 / include / .htaccess / .user.ini）
7. nginx 0.83 /1.jpg%00php
8. apahce 1x 或者 2x 当 apache 遇见不认识的后缀名，会从后向前解析例如 1.php.rar 不认识 rar 就向前解析，直到知道它认识的后缀名。
9. phpcgi 漏洞(nginx iis7 或者以上) 上传图片后 1.jpg。访问 1.jpg/1.php 也会解析成php。
10. Apache HTTPD 换行解析漏洞（CVE-2017-15715）
11. apache通过 mod_php来运行脚本，其 2.4.0-2.4.29中存在apache换行解析漏洞，在解析php时xxx.php\x0A 将被按照 PHP 后缀进行解析，导致绕过一些服务器的安全策略。

### 文件上传漏洞通用检测方法

判断是否为黑白名单，如果是白名单 寻找可控参数。如果是黑名单禁止上传，可以用有危害的后缀名批量提交测试，寻找遗留的执行脚本。

.php

.php5

.php4

.php3

.php2

.html

.htm

.phtml

.pht

.pHp

.phP

.pHp5

.pHp4

.pHp3

.pHp2

.Html

.Htm

.pHtml

.jsp

.jspa

.jspx

.jsw

.jsv

.jspf

.jtml

.jSp

.jSpx

.jSpa

.jSw

.jSv

.jSpf

.jHtml

.asp

.aspx

.asa

.asax

.ascx

.ashx

.asmx

.cer

.aSp

.aSpx

.aSa

.aSax

.aScx

.aShx

.aSmx

.cEr

.sWf

.swf

.htaccess

使用 burpsuite 抓包上传将后缀名设置成变量，把这些文件设置成一个字典批量提交。

![1787879792005-76a10c77-9b61-4cb6-a7b6-ea5a537cde91.png](../../img/282317868/1787879792005-76a10c77-9b61-4cb6-a7b6-ea5a537cde91-509608.png)

抓包后发到 Intruder，点击清除，然后在文件名后面的后缀选起来，点击右侧的添加按钮。包括点也要加。

![1787879765841-4a1a04c6-232c-43a9-a934-95711d6b9a7e.png](../../img/282317868/1787879765841-4a1a04c6-232c-43a9-a934-95711d6b9a7e-569793.png)

在有效载荷这里导入后缀名字典文件。

![1787879817171-c68388ba-8cd9-4a03-9165-e602f5764be8.png](../../img/282317868/1787879817171-c68388ba-8cd9-4a03-9165-e602f5764be8-483229.png)

开始攻击。 查看数据包大小 查看确定时候可上传即可。

![1787879874885-9e487e90-e0df-4cd6-a2e4-9434f02bbc04.png](../../img/282317868/1787879874885-9e487e90-e0df-4cd6-a2e4-9434f02bbc04-881503.png)

### 文件上传的攻击方法

![1787880638299-9f063b50-831c-4334-a939-904a1ba2d5b6.png](../../img/282317868/1787880638299-9f063b50-831c-4334-a939-904a1ba2d5b6-714472.png)

### 4.2 防御思路对照

| 检测手段 | 常见绕过方向 |
| --- | --- |
| 前端 JS | 禁用 JS、改 HTML、抓包改后缀 |
| MIME | 改 `Content-Type` |
| 扩展名黑名单 | 冷门后缀、大小写、空格、点、`::$DATA`、双写、.htaccess |
| 扩展名白名单 | `%00` 截断、解析漏洞、配合配置文件 |
| 文件头 / getimagesize | 图片马 |
| 二次渲染 | 残留载荷或其它漏洞面 |
| 先存后检 | 条件竞争 |

***

## 5. 防御建议（开发视角）

1. **永远不要信任前端校验**
2. 使用**白名单**扩展名，并 `strtolower` 后比较
3. **随机重命名**存储，不要用用户原始文件名
4. 上传目录**禁止脚本执行**（Apache/Nginx 配置）
5. 禁止 `.htaccess` / `.user.ini` 上传与生效
6. 图片类：解码再存储或严格二次处理，并避免 `include` 用户文件
7. 保持 PHP/中间件版本更新，避免 `%00`、旧解析漏洞
8. 有条件做内容安全策略与独立文件存储域

服务器端使用白名单防御，修复 web 中间件的漏洞，禁止客户端存在可控参数，存放文件目录禁止脚本执行，限制后缀名 一定要设置图片格式 jpg、gif 、png 文件名随机的，不可预测。

***

## 6. 常见问题

| 问题 | 说明 |
| --- | --- |
| `%00` 无效 | PHP ≥ 5.3.4 已修复；需低版本环境 |
| `.htaccess` 无效 | `AllowOverride None` 或非 Apache |
| `.phtml` 不执行 | 当前 Apache 未把该后缀交给 PHP |
| Docker 无法上传 | `upload` 目录权限或未创建 |
| 关卡与文章不一致 | fork/版本不同，以本机 `Pass-XX` 源码为准 |

***

## 7. 清理与卸载

```bash
# Docker
docker stop upload-labs
docker rm upload-labs
docker rmi c0ny1/upload-labs

# 本地源码
# 删除网站目录中的 upload-labs 文件夹即可
# 并清空 upload 目录中的测试 webshell，避免残留
```

***

## 8. 参考资料

* 官方仓库：<https://github.com/c0ny1/upload-labs>
* 官方 README 环境说明与 Docker 构建方式
* 各安全博客 Writeup（搜索「upload-labs Pass-XX」对照源码学习）
* 【汇总】文件上传漏洞upload-labs无法复现汇总：<https://wiki.bafangwy.com/doc/174/>

***

## 9. 学习建议

1. 每关先**自己读源码**再看题解
2. 记录：校验点、绕过点、依赖的 PHP/OS 条件
3. 每关结束后写一条**对应防御措施**
4. 不要只会传 webshell，要理解「为何能执行」

***

**笔记版本**：v1.0\
**适用对象**：Web 安全入门 → 文件上传专项\
**环境提醒**：PHP 版本与 OS 会显著影响部分关卡可解性

> 本文描述的是公开教学靶场中的已知漏洞模式，用于合法安全研究与防御建设。实战中仅可在明确授权下进行测试。


