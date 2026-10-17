# upload-labs 靶场通关笔记

> **说明**：本文面向**授权安全学习 / CTF 练习**。upload-labs 是故意存在漏洞的教学靶场，仅可在本地或授权环境中使用。请勿将相关技术用于未授权系统。

***

## 1. 概述

**upload-labs** 是由 [c0ny1](https://github.com/c0ny1/upload-labs) 维护的 PHP 文件上传漏洞练习靶场，汇总渗透测试与 CTF 中常见的上传绕过手法，目前常见版本约 **20～21 关**。

| 项目 | 说明 |
| --- | --- |
| 项目地址 | <https://github.com/c0ny1/upload-labs> |
| 语言 | PHP |
| 目标 | 系统练习前端校验、MIME、黑白名单、解析漏洞、图片马、竞争条件等 |
| 推荐环境 | Windows + PHP 5.2.x（部分关依赖旧特性）；或 Docker |

### 漏洞类型总览

| 关卡 | 主要考点 |
| --- | --- |
| Pass-01 | 前端 JS 校验 |
| Pass-02 | Content-Type / MIME |
| Pass-03 | 黑名单不完整（可解析后缀） |
| Pass-04 | 黑名单遗漏 `.htaccess` |
| Pass-05 | `.user.ini` + 相关绕过 |
| Pass-06 | 后缀大小写 |
| Pass-07 | 后缀空格 |
| Pass-08 | 后缀点号 |
| Pass-09 | Windows `::$DATA` |
| Pass-10 | 点 + 空格 + 点 |
| Pass-11 | 双写绕过 |
| Pass-12 | 白名单 + GET `%00` 截断 |
| Pass-13 | 白名单 + POST `%00` 截断 |
| Pass-14～16 | 图片马 / 文件头 / getimagesize 等 |
| Pass-17 | 二次渲染 |
| Pass-18～19 | 条件竞争 |
| Pass-20～21 | 综合 / 路径与后缀组合 |

> 不同镜像或 fork 关卡编号可能略有差异，以本地源码为准。

***

## 2. 环境搭建

### 2.1 官方推荐配置

| 配置项 | 建议 |
| --- | --- |
| 系统 | Windows 优先（Pass-19 等部分题更适合 Linux） |
| PHP | **5.2.17**（过高会导致 `%00` 等关无法复现） |
| 扩展 | `php_gd2`、`php_exif` |
| Web 服务 | Apache，**module 方式**连接 PHP（非纯 CGI 时部分解析特性不同） |

### 2.2 Docker 快速启动

```bash
docker pull c0ny1/upload-labs
docker run -d -p 8080:80 --name upload-labs c0ny1/upload-labs
```

浏览器访问：`http://127.0.0.1:8080`

若提示 upload 目录不存在：

```bash
docker exec -it upload-labs bash
mkdir -p /var/www/html/upload
chown www-data:www-data /var/www/html/upload
chmod 777 /var/www/html/upload
```

### 2.3 本地源码

```bash
git clone https://github.com/c0ny1/upload-labs.git
# 放入 phpStudy / 自建 Apache+PHP 网站目录后访问
```

Windows 也可使用项目 Release 中的集成环境包。

![1787403202970-8856c796-5d0b-4d04-bc9a-ec5376149019.png](../../img/282317868/1787403202970-8856c796-5d0b-4d04-bc9a-ec5376149019-471472.png)

<font style="color:#DF2A3F;">提示：</font>如果使用 Windows 部署靶场的话，记得关闭 Windows 安全中心，不然上传 shell 会被安全中心当病毒查杀掉，导致实验失败。关闭的过程如下：

在 Windows 设置里面，打开“更新与安全”。

![1787457886475-be58e95e-8436-4357-ad37-689d688b100f.png](../../img/282317868/1787457886475-be58e95e-8436-4357-ad37-689d688b100f-100807.png)

点击左侧的“Windows 安全中心”，点击中间的“打开 Windows 安全中心”。

![1787457948800-493648ca-2a99-4234-8fa5-cac41922aa06.png](../../img/282317868/1787457948800-493648ca-2a99-4234-8fa5-cac41922aa06-102154.png)

点击左侧列表的“病毒和威胁防护”，在“‘病毒和威胁防护’设置”下面点击管理设置。

![1787457968214-43c589e3-bfdc-4942-bc4b-2ed26e011d33.png](../../img/282317868/1787457968214-43c589e3-bfdc-4942-bc4b-2ed26e011d33-871813.png)

关闭“实时保护”按钮，即可关闭 Windows 安全中心。

![1787458052573-13402f4c-ca3e-49f2-bb72-935f262e52f9.png](../../img/282317868/1787458052573-13402f4c-ca3e-49f2-bb72-935f262e52f9-244694.png)

或者使用这个开源的 defender-control 去关闭“Windows 安全中心”也可以。

<https://github.com/pgkt04/defender-control>

![1787458296603-d83831ce-824d-47af-90f1-b90056b4c395.png](../../img/282317868/1787458296603-d83831ce-824d-47af-90f1-b90056b4c395-188816.png)

![1787458266034-7ad87aae-713b-4593-84f3-9604054db835.png](../../img/282317868/1787458266034-7ad87aae-713b-4593-84f3-9604054db835-923976.png)

### 2.4 练习前准备

**测试用 PHP 一句话（仅用于靶场）：**

```php
<?php @eval($_POST['cmd']); ?>
```

或先验证环境：

```php
<?php phpinfo(); ?>
```

**常用工具：**

* Burp Suite / Caido 等抓包改包
* 浏览器开发者工具（禁用 JS）
* 可选：蚁剑 / 冰蝎（连接成功后的 Webshell，仅靶场）

***

## 3. 通关详解

下列为通用解题思路与源码逻辑说明。界面截图请在本地靶场自行对照；步骤按「看源码 → 找校验点 → 构造绕过 → 验证」展开。

***

![1787403304062-e9c94d0e-6305-4605-ad97-1401fc1b8447.png](../../img/282317868/1787403304062-e9c94d0e-6305-4605-ad97-1401fc1b8447-799937.png)

可能会用到的图片素材

kali-1.0.png

![1787568621794-785f510e-9b13-4280-bcf2-39b9f97c608a.png](../../img/282317868/1787568621794-785f510e-9b13-4280-bcf2-39b9f97c608a-775046.png)

kali-linux.png

![1787568621799-83de61d8-31cf-42cd-8e28-a5b981345a04.png](../../img/282317868/1787568621799-83de61d8-31cf-42cd-8e28-a5b981345a04-111444.png)

hacker.jpg

![1787568650882-0267d27b-41ac-4b06-9a3a-d92ad49fd178.jpeg](../../img/282317868/1787568650882-0267d27b-41ac-4b06-9a3a-d92ad49fd178-144144.jpeg)

GIF 图片素材：

sample-animated-400x300.gif

![1787568593875-1f88a34f-634b-4c9a-96b7-6208aa797c7b.gif](../../img/282317868/1787568593875-1f88a34f-634b-4c9a-96b7-6208aa797c7b-609239.gif)
