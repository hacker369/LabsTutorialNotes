# SQLi-Labs：环境搭建与基础

> **适用范围**：仅限本地 / 授权靶场练习。sqli-labs 是故意存在 SQL 注入漏洞的教学平台，请勿对未授权系统使用文中手法。\
> **项目地址**：<https://github.com/Audi-1/sqli-labs>
>
> 在线靶场：<https://ctf.hscsec.cn/range/sqli-labs/>

***

## 1. 概述

### 什么是 SQL 注入

当 Web 应用向后台数据库传递 <font style="color:#DF2A3F;">SQL 语句</font> 进行数据库操作时，如果对用户输入的参数<font style="color:#DF2A3F;">没有经过严格的过滤处理</font>，那么攻击者就可以构造特殊的 SQL 语句，直接输入数据库引擎执行，获取或修改数据库中的数据。

### 系统库

在<font style="color:#DF2A3F;">5.0</font>以上的大版本提供了访问数据库元数据（sql 服务自带的数据库）的方式。

\*\*<font style="color:#DF2A3F;">information_schema </font>\*\***库**：是信息数据库，其中保存着关于 MySQL 服务器所维护的所有其他数据库的信息(例如数据库或表的名称，列的数据类型或访问权限)

SCHEMATA 表：提供了所有数据库信息。

* schema_name：数据库名

TABLES 表：提供了所以表的信息。

* table_name：表名
* table_schema：表所属的数据库

COLUMNS 表：详细描述了每张表的所有列的信息。

* column_name：字段名
* table_name：字段所属的表名
* table_schema：表所属的数据库名

**performance_schema 库**：具有87张表，MySQL 5.5开始新增的一个数据库，主要用于收集数据库服务器性能参数。内存数据库，数据放在内存中直接操作的数据库。相对于磁盘，内存的数据读写速度要高出几个数量级。

**mysql 库**：是核心数据库，类似于 sql server中的 master 表，主要负责存储数据库的用户（账户）信息、权限设置、关键字等 mysql 自己需要使用的控制和管理信息。常用举例：在 mysql.user（5.7版本之前）表中修改root 用户的密码 sys 库

**sys 库**：sys 库是 MySQL 5.7 增加的系统数据库，这个库是通过视图的形式把 information_schema 和 performance_schema 结合起来，查询出更加令人容易理解的数据。可以查询谁使用了最多的资源，哪张表访问最多等。

sqli-labs（作者 Audi-1）是经典的 SQL 注入练习平台，覆盖报错注入、联合查询、布尔/时间盲注、POST、Header、二次注入、过滤绕过、堆叠查询等场景。关卡目录一般为 Less-1 ~ Less-65（含部分 `Less-25a` 等变体）。

| 项目 | 说明 |
| --- | --- |
| 仓库 | <https://github.com/Audi-1/sqli-labs> |
| 技术栈 | PHP + MySQL/MariaDB |
| 数据库名（默认） | `security` |
| 常见练习表 | `users`（含 `id/username/password` 等） |
| 官方说明 | 见仓库 `readme.md` |

### 官方覆盖的知识点分类

| 类别 | 含义（中文） |
| --- | --- |
| Error Based（Union） | 报错 / 联合查询（字符串、整型等） |
| Double Injection | 双查询报错类注入 |
| Blind Boolean / Time | 布尔盲注 / 时间盲注 |
| Update / Insert | 更新、插入语句中的注入 |
| Header Injection | Referer / User-Agent / Cookie |
| Second Order | 二次注入 |
| WAF / Blacklist Bypass | 绕过注释、OR/AND、空格、UNION 等过滤 |
| addslashes / escape | 转义函数绕过（含特殊条件） |
| Stacked queries | 堆叠查询 |
| Challenge（约 54–65） | 限次数取 key 等综合题 |

***

## 2. 安装步骤

### 2.1 环境要求

* PHP（传统环境常用 5.x；也有社区 PHP7+ 适配版），推荐使用 PHP 5.3.29。
* MySQL 或 MariaDB
* Apache / Nginx
* 浏览器；建议配合 Burp Suite

> 注意：原版大量使用已弃用的 `mysql_*` 函数，**PHP 7+ 默认不可用**。若本机是新 PHP，请用 Docker 镜像，或找标注支持 PHP7 的 fork。

### 2.2 方式一：源码 + phpStudy / LAMP（传统）

```bash
git clone https://github.com/Audi-1/sqli-labs.git
# 将目录放到网站根目录，例如 /var/www/html/sqli-labs 或 phpStudy 的 WWW
```

1. 编辑数据库账号文件：

```latex
sqli-labs/sql-connections/db-creds.inc
```

![1789965066682-0679b630-ab37-4298-935c-bddce6658a5a.png](../../img/285943702/1789965066682-0679b630-ab37-4298-935c-bddce6658a5a-795269.png)

常见字段含义：

| 配置项 | 中文含义 | 示例 |
| --- | --- | --- |
| `$dbuser` | 数据库用户名 | `root` |
| `$dbpass` | 数据库密码 | `root` / 空 / `toor` |
| `$dbname` | 库名（部分文件） | `security` |
| `$host` | 数据库主机 | `localhost` |

2. 浏览器访问：

```latex
http://127.0.0.1/sqli-labs/
```

3. 点击页面上的 **Setup/resetDB**（或类似「重建数据库」链接），创建库表并导入数据。

![1789965025945-39b7f378-6e36-4733-83fa-03dd3a694bec.png](../../img/285943702/1789965025945-39b7f378-6e36-4733-83fa-03dd3a694bec-427588.png)

4. 再点各 **Lesson / Less-x** 开始练习。

### 2.3 方式二：Docker（推荐，少踩 PHP 版本坑）

社区常见用法示例（镜像名可能因维护者而异，请以实际拉取结果为准）：

```bash
# 示例：部分环境可直接使用已有镜像
docker pull acgpiano/sqli-labs
docker run -dt --name sqli-labs -p 80:80 acgpiano/sqli-labs
```

访问：

```latex
http://127.0.0.1:80/
```

![1790873545326-9dabb557-c990-4a5d-98a0-e0676e8bb21e.png](../../img/285943702/1790873545326-9dabb557-c990-4a5d-98a0-e0676e8bb21e-359676.png)

### 2.4 验证安装

* 首页能打开各 Less 链接
* Less-1 访问 `?id=1` 能显示用户信息

![1789965190706-358674df-6417-4f4b-9dd4-f1f0d75cae2b.png](../../img/285943702/1789965190706-358674df-6417-4f4b-9dd4-f1f0d75cae2b-794761.png)

* `?id=1'` 在报错关应出现 SQL 语法错误信息（便于学习）

***

## 3. 基本使用

### 3.1 推荐练习顺序

1. **Less-1～10**：GET 报错 / 联合 / 盲注基础
2. **Less-11～17**：POST、更新、头注入入门
3. **Less-18～22**：UA / Referer / Cookie / 二次相关
4. **Less-23～28**：过滤、注释、空格等绕过
5. **Less-29～37**：更复杂过滤与转义
6. **Less-38～53**：堆叠、进阶变体
7. **Less-54～65**：限次 Challenge

### 3.2 通用手注流程（有回显时）

1. 判断注入点与闭合：`' " ) )` 等
2. 注释尾巴：`--+` 或 `%23`（`#`）
3. `order by n` 判列数
4. `union select` 找回显位
5. 查库 → 表 → 列 → 数据（`information_schema`）

### 3.3 数据库结构（默认 security）

练习中最常用：

| 对象 | 说明 |
| --- | --- |
| 库 `security` | 默认靶场库 |
| 表 `users` | 用户表 |
| 字段 | `id`, `username`, `password` 等 |

***

## 4. 重要参数与 SQL 片段说明

| 名称 | 中文含义 |
| --- | --- |
| `id` | 最常见的 GET 注入参数 |
| `uname` / `passwd` | POST 登录类关卡用户名/密码参数 |
| `' / " / )` | 字符串或括号闭合符 |
| `--+` / `#` | 注释掉后面原 SQL |
| `order by n` | 探测查询列数 |
| `union select` | 联合查询，合并结果集 |
| `information_schema` | MySQL 元数据库（库名/表名/列名） |
| `group_concat()` | 把多行拼成一个字符串便于一次回显 |
| `updatexml()` / `extractvalue()` | 报错注入常用函数 |
| `sleep(n)` / `benchmark()` | 时间盲注延时 |
| `substr` / `ascii` / `length` | 盲注逐字符判断 |
| `0x...` 十六进制 | 绕过引号被转义时写字符串 |

### 常用的系统函数

1. version()——MySQL 版本
2. user()——数据库用户名
3. database()——数据库名
4. @@datadir——数据库路径
5. @@version_compile_os——操作系统版本

### 常用的字符串连接函数

1. concat(str1,str2,...)——没有分隔符地连接字符串
2. concat_ws(separator,str1,str2,...)——含有分隔符地连接字符串
3. group_concat(str1,str2,...)——连接一个组的所有字符串，并以逗号分隔每一条数据

***


---

**分章阅读：** [关卡索引](README.md) · [Less-1–10](01-less-01-10.md) · [Less-11–20](02-less-11-20.md) · [Less-21–30](03-less-21-30.md) · [Less-31–40](04-less-31-40.md) · [Less-41–50](05-less-41-50.md) · [Less-51–65](06-less-51-65.md) · [速查与防御](07-reference-defense.md)
