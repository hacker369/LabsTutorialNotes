# 贡献指南

感谢愿意完善这份笔记！无论是指正错误还是补充关卡，请先花一分钟读完本页。

## 环境准备

```bash
git clone git@github.com:hacker369/LabsTutorialNotes.git
cd LabsTutorialNotes
npx docsify-cli serve .    # http://localhost:3000 实时预览
```

## 章节体例（尽量保持统一）

每个关卡建议固定为六段结构，方便读者横向对比：

```text
### Less-N：注入类型一句话
- 关卡信息：请求方式 / 闭合类型 / 源码关键差异
- 考点：本关练什么
- Payload：代码块给出完整可复现 payload
- 原理：为什么这样能绕过（2~4 句话）
- 截图：1~2 张关键成功图
- 小结：与相邻关卡的对比 / 易错点
```

## 代码块语言标记

| 内容 | 标记 |
|------|------|
| SQL 语句 | `sql` |
| HTTP 请求/响应 | `http` |
| HTML / XSS payload | `html` |
| JS 片段 | `javascript` |
| 命令行 | `bash` |
| URL、无语言文本 | `text` |

**不要使用 `latex`**（语雀导出残留），渲染样式不对且无高亮。

## 截图规范（CI 会强制检查新增图片）

1. 放入 `img/<靶场名>/`（如 `img/sqli-labs/`），不再使用纯数字目录
2. 每关保留 1~2 张关键成功图即可，不要全量截屏
3. 入库前压缩：`pngquant --quality=65-85 --ext .png --force 图片.png`，单张 < 512KB
4. 图片必须在 md 中被引用，孤儿图会被 CI 拦截
5. 自检：`python3 scripts/check_images.py`

## 提交流程

1. 从 `main` 拉分支：`git checkout -b fix/less-27-php8`
2. 提交时写清楚改动范围：`docs: 修正 Less-27 的报错注入 payload（PHP 8 适配）`
3. 发起 PR 并填写模板自查清单
4. CI（图片引用/体积/外链检查）通过后合并

## 反馈 Issue

- payload 在你的环境不生效 → 用「Payload 失效反馈」模板，务必写清 PHP/MySQL 版本
- 笔误、原理解释问题、更优解法 → 用「内容纠错 / 改进建议」模板
