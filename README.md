# LabsTutorialNotes

Web 安全**经典靶场通关笔记**（自用 + 分享）：sqli-labs、xss-labs、upload-labs、Google XSS Game。

> **免责声明**  
> 本文档仅供在**本地或已授权**的教学靶场中学习使用。笔记中的手法针对故意存在漏洞的练习环境。  
> **请勿**对未授权的真实系统进行测试或攻击。作者不对任何滥用行为负责。

**在线阅读（静态站）：** [https://hacker369.github.io/LabsTutorialNotes.github.io/](https://hacker369.github.io/LabsTutorialNotes.github.io/)  
站点仓库：[LabsTutorialNotes.github.io](https://github.com/hacker369/LabsTutorialNotes.github.io)

---

## 目录导航

| 靶场 | 笔记 | 说明 |
|------|------|------|
| [sqli-labs](https://github.com/Audi-1/sqli-labs) | [sqli-labs靶场通关笔记.md](./sqli-labs靶场通关笔记.md) | SQL 注入（报错 / 联合 / 盲注 / 过滤绕过等） |
| [xss-labs](https://github.com/do0dl3/xss-labs) | [xss-labs靶场通关笔记.md](./xss-labs靶场通关笔记.md) | XSS 反射、过滤绕过、事件与编码 |
| [upload-labs](https://github.com/c0ny1/upload-labs) | [upload-labs靶场通关笔记.md](./upload-labs靶场通关笔记.md) | 文件上传绕过 |
| [Google XSS Game](https://xss-game.appspot.com/) | [GoogleXSSGame靶场通关笔记.md](./GoogleXSSGame靶场通关笔记.md) | Google 官方 XSS 闯关 |

相关仓库（组件漏洞 / Vulhub 复现笔记）：  
→ [VulhubTutorialNotes.github.io](https://github.com/hacker369/VulhubTutorialNotes.github.io) · [在线阅读](https://hacker369.github.io/VulhubTutorialNotes.github.io/)

---

## 推荐阅读顺序

1. **sqli-labs**：先建立注入探测与联合查询直觉  
2. **xss-labs**：理解输出上下文与过滤绕过  
3. **upload-labs**：前后端校验、解析差异  
4. **Google XSS Game**：巩固浏览器侧 XSS  
5. 再进入 Vulhub 等真实组件漏洞环境

每篇笔记大致结构：

1. 概述与环境安装  
2. 重要概念 / 参数说明  
3. 分关（或分题）payload + 原理 + 截图  
4. 小结

---

## 环境建议

| 场景 | 建议 |
|------|------|
| Windows 入门 | phpStudy / XAMPP + 浏览器 +（可选）Burp Suite |
| 少踩 PHP 版本坑 | Docker 镜像部署各靶场（笔记内有示例命令） |
| 抓包改请求 | Burp Suite 社区版 / 浏览器插件 |

具体步骤见各笔记中的「安装」章节。

---

## 仓库结构

```text
LabsTutorialNotes/
├── README.md
├── LICENSE
├── .gitattributes
├── docs/
│   └── MAINTENANCE.md          # 维护与图片优化说明
├── sqli-labs靶场通关笔记.md
├── xss-labs靶场通关笔记.md
├── upload-labs靶场通关笔记.md
├── GoogleXSSGame靶场通关笔记.md
└── img/                        # 笔记截图（语雀导出目录结构）
```

---

## 如何贡献 / 纠错

- 发现 payload 失效、环境差异或笔误：欢迎开 Issue  
- 直接 PR 小修改也欢迎（请尽量保持现有章节风格）

维护与体积优化说明见 [docs/MAINTENANCE.md](./docs/MAINTENANCE.md)。

---

## License

代码与文档默认采用 [MIT License](./LICENSE)。  
笔记中引用的靶场项目版权归其各自作者所有。
