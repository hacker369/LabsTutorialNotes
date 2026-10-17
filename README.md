<div align="center">

# 🛡️ LabsTutorialNotes

**Web Security Labs · Source Code Analysis · Reproducible Notes**

> 从环境搭建、请求分析，到漏洞原理、复现排错与安全修复。

[![License](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Docsify](https://img.shields.io/badge/Docs-Docsify-00e5ff.svg)](https://hacker369.github.io/LabsTutorialNotes/)
[![CI](https://github.com/hacker369/LabsTutorialNotes/actions/workflows/ci.yml/badge.svg)](https://github.com/hacker369/LabsTutorialNotes/actions/workflows/ci.yml)

**[在线阅读](https://hacker369.github.io/LabsTutorialNotes/)** · **[靶场索引](#-靶场索引)** · **[问题反馈](https://github.com/hacker369/LabsTutorialNotes/issues/new/choose)**

</div>

```text
root@LabsTutorialNotes:~$ cat project.info
scope     : web security training labs
approach  : reproduce -> inspect -> understand -> remediate
theme     : dark terminal / neon green / cyan
```

## // 项目简介

LabsTutorialNotes 是一份面向本地安全学习和授权教学环境的 Web 安全靶场笔记。内容不仅记录测试输入，也关注环境版本、源码逻辑、请求与响应、失败原因和安全修复。

- **重视可复现性：** 尽量记录操作系统、PHP、数据库和 Web 服务版本。
- **重视原理：** 解释输入为什么产生当前行为，而不只罗列 Payload。
- **重视排错：** 保留版本差异、错误信息和真实实验中的问题。
- **重视防御：** 在适当的章节中补充根因与修复思路。

## // 靶场索引

| 靶场 | 主要主题 | 关卡规模* | 学习入口 |
|---|---|:---:|---|
| 💉 **SQLi-Labs** | SQL 注入、盲注、过滤逻辑与查询上下文 | 65 | [分章阅读](./notes/sqli-labs/README.md) · [原始完整笔记](./sqli-labs靶场通关笔记.md) |
| ⚡ **XSS-Labs** | 输出上下文、反射型 XSS、编码与过滤 | 20 | [打开索引](./notes/xss-labs/README.md) · [原始完整笔记](./xss-labs靶场通关笔记.md) |
| 📤 **Upload-Labs** | 文件上传校验、解析差异与竞态条件 | 21 | [打开索引](./notes/upload-labs/README.md) · [原始完整笔记](./upload-labs靶场通关笔记.md) |
| 🎯 **Google XSS Game** | 浏览器上下文与 DOM 行为 | 6 | [打开索引](./notes/google-xss-game/README.md) · [原始完整笔记](./GoogleXSSGame靶场通关笔记.md) |

<sub>*关卡数量为当前笔记的标注规模；不同版本或分支可能存在差异，请以实际源码和对应笔记为准。</sub>

组件漏洞与真实 CVE 环境的相关笔记见姊妹项目：[VulhubTutorialNotes](https://github.com/hacker369/VulhubTutorialNotes.github.io)。

## // 推荐学习路线

1. **准备隔离环境：** 先阅读 [环境搭建指南](./docs/setup.md)，核对靶场和运行时版本。
2. **按关卡复现：** 从靶场索引进入对应教程，记录请求、响应和实际观察。
3. **分析源码：** 找出输入处理、过滤、输出或数据库操作的关键位置。
4. **排查差异：** 使用 [故障排查手册](./docs/troubleshooting.md) 记录环境与行为差异。
5. **总结与修复：** 参考 [实验笔记模板](./docs/lab-note-template.md) 补充根因、修复和验证。

## // 快速开始

在线阅读：**[hacker369.github.io/LabsTutorialNotes](https://hacker369.github.io/LabsTutorialNotes/)**

本地阅读需要 Node.js 和 npm：

```bash
git clone https://github.com/hacker369/LabsTutorialNotes.git
cd LabsTutorialNotes
npx docsify-cli serve .
```

随后打开终端输出的本地地址（Docsify 默认通常为 `http://localhost:3000`）。

## // 仓库结构

```text
LabsTutorialNotes/
├── README.md / README_EN.md
├── index.html                 # Docsify 入口与主题
├── home.md                    # 在线站点首页
├── _sidebar.md / _navbar.md   # 站点导航
├── notes/                     # 靶场索引与拆分章节
│   ├── sqli-labs/
│   │   ├── README.md
│   │   ├── 00-overview.md
│   │   ├── 01-less-01-10.md … 06-less-51-65.md
│   │   └── 07-reference-defense.md
│   ├── xss-labs/
│   ├── upload-labs/
│   └── google-xss-game/
├── docs/                      # 环境、排错、模板与术语
├── sqli-labs靶场通关笔记.md    # 现有完整笔记，迁移期间保留
├── xss-labs靶场通关笔记.md
├── upload-labs靶场通关笔记.md
├── GoogleXSSGame靶场通关笔记.md
├── img/                       # 现有截图路径
└── scripts/check_images.py    # 图片引用与体积检查
```

## // 贡献与维护

发现链接失效、版本差异、笔误或无法复现的步骤，欢迎提交 [Issue](https://github.com/hacker369/LabsTutorialNotes/issues/new/choose) 或 Pull Request。提交实验笔记时，请说明测试环境与验证状态；维护流程见 [docs/MAINTENANCE.md](./docs/MAINTENANCE.md)。

## // 安全声明

本项目仅用于本地或明确授权的教学靶场、CTF 和安全研究。请勿对未授权的真实系统进行测试。运行故意存在漏洞的旧版应用时，请使用隔离的虚拟机或容器，避免暴露到公网。

## // License

[MIT License](./LICENSE)。所引用靶场项目的代码与品牌归各自权利人所有，请同时遵守其许可证与使用条款。
