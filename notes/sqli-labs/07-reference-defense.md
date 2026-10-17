# SQLi-Labs：速查、排错与防御

> 本章从仓库原始通关笔记拆分而来。截图继续使用仓库根目录的 `img/`，并已按新目录调整相对路径。请结合当前靶场版本验证实际行为。

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

---

**分章导航：** [索引](README.md) · [环境与基础](00-overview.md) · [Less-1–10](01-less-01-10.md) · [Less-11–20](02-less-11-20.md) · [Less-21–30](03-less-21-30.md) · [Less-31–40](04-less-31-40.md) · [Less-41–50](05-less-41-50.md) · [Less-51–65](06-less-51-65.md) · [速查与防御](07-reference-defense.md)
