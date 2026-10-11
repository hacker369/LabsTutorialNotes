# 仓库维护说明

本文记录 LabsTutorialNotes 的已知问题与后续优化方向，方便自己或协作者跟进。

## 当前状况（约 2026-10）

| 项目 | 说明 |
|------|------|
| 笔记文件 | 4 篇主笔记 + README |
| 截图 | `img/` 下约 1500+ 张，合计约 130MB+ |
| 单文件体积 | `sqli-labs靶场通关笔记.md` 约 320KB，GitHub 在线阅读偏重 |
| 图片目录 | 语雀导出风格：`img/<数字 ID>/时间戳-uuid-*.png` |

大量图片会导致：`git clone` / `git push` 变慢、仓库体积膨胀。

## 推荐优化（按优先级）

### 1. 压缩现有截图

在本地仓库根目录可尝试（需自行安装工具）：

```bash
# 示例：使用 pngquant 批量压缩（会覆盖，请先备份或新分支）
find img -name '*.png' -print0 | xargs -0 -P4 -I{} pngquant --quality=65-85 --ext .png --force {}
```

或使用 [TinyPNG](https://tinypng.com/) / ImageMagick 转 WebP 后改 md 内链接。

### 2. Git LFS（大文件）

本仓库已添加 `.gitattributes` 中的 LFS 规则草案。启用步骤：

```bash
git lfs install
# 若规则已写入 .gitattributes
git add .gitattributes
git add img
git commit -m "chore: track lab screenshots with Git LFS"
git push
```

注意：对**已经提交进普通 Git 历史**的大文件，仅加 LFS 不会缩小旧历史，需要 `git lfs migrate` 等历史重写（慎用，需协调所有协作者）。

### 3. 拆分超长笔记

建议将 `sqli-labs靶场通关笔记.md` 拆为例如：

```text
notes/sqli-labs/
  00-overview.md
  01-less-01-10.md
  02-less-11-20.md
  ...
```

根目录 README 表格链到各篇即可。

### 4. 截图策略

- 每关保留 **1～2 张关键成功图** 通常足够  
- 避免逐步探测全量截图  
- 新图尽量直接导出为压缩 PNG / WebP，并放入按靶场划分的目录，例如 `img/xss-labs/`

### 5. 体例统一

- payload 代码块语言标记使用 `sql` / `http` / `html` / `text`，避免误用 `latex`  
- 减少语雀导出残留的 `<font>` 等标签  
- 每关尽量固定：关卡信息 → 考点 → payload → 原理 → 截图 → 小结

## 不在本仓库做的事

- 不提供可对真实站点武器化的一键脚本  
- 不收录未授权实战目标信息  
