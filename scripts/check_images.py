#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片健康检查脚本（CI 与本地通用）
=================================
用法：
  python3 scripts/check_images.py              # 本地全量报告（不阻塞）
  python3 scripts/check_images.py --strict     # 存在孤儿图片/缺失引用时退出码 1
  python3 scripts/check_images.py --ci BASE    # CI 模式：只对 BASE..HEAD 新增图片强制校验
  python3 scripts/check_images.py --summary    # 额外输出 Markdown 到 $GITHUB_STEP_SUMMARY

规则：
  1. 新增到 img/ 的图片必须被某个 .md 引用（防孤儿图堆积）——CI 阻塞
  2. 新增图片单张不得超过 512KB（请先用 pngquant 压缩）——CI 阻塞
  3. 存量孤儿图片只报告不阻塞，清理方式见 docs/MAINTENANCE.md
"""
import hashlib
import os
import re
import subprocess
import sys

IMG_EXT_RE = re.compile(r"\.(png|jpe?g|gif|webp|svg|bmp)$", re.I)
IMG_REF_RE = re.compile(r'(?:\./)?img/[^\s\)\]"\'>`]+')
SKIP_DIRS = {".git", "node_modules"}
MAX_NEW_IMAGE_BYTES = 512 * 1024  # 新增图片体积上限 512KB


def md5sum(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{int(n)} B"
        n /= 1024


def collect_md_refs(repo):
    """返回 (被引用且存在于磁盘的图片路径集合, 引用了但磁盘缺失的 [(md, raw), ...])"""
    refs, missing = set(), []
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if not f.lower().endswith(".md"):
                continue
            mdp = os.path.join(root, f)
            try:
                text = open(mdp, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            for m in IMG_REF_RE.finditer(text):
                raw = m.group(0).rstrip(".,;:!?`|")
                if not IMG_EXT_RE.search(raw) or "*" in raw or "<" in raw:
                    continue  # 跳过 img/<占位符> 等文档说明文字
                for base in (os.path.dirname(mdp), repo):
                    cand = os.path.normpath(os.path.join(base, raw))
                    if os.path.isfile(cand):
                        refs.add(os.path.normpath(cand))
                        break
                else:
                    missing.append((os.path.relpath(mdp, repo), raw))
    return refs, missing


def disk_images(repo):
    out = []
    img_root = os.path.join(repo, "img")
    if not os.path.isdir(img_root):
        return out
    for root, dirs, files in os.walk(img_root):
        for f in files:
            if IMG_EXT_RE.search(f):
                out.append(os.path.join(root, f))
    return out


def full_report(repo, refs, missing, images):
    referenced = [p for p in images if os.path.normpath(p) in refs]
    orphans = sorted(p for p in images if os.path.normpath(p) not in refs)
    if referenced:
        ref_hashes = {md5sum(p) for p in referenced}
        dup_orphans = [p for p in orphans if md5sum(p) in ref_hashes]
        uniq_orphans = [p for p in orphans if md5sum(p) not in ref_hashes]
    else:
        dup_orphans, uniq_orphans = [], orphans
    biggest = sorted(images, key=os.path.getsize, reverse=True)[:10]
    return referenced, orphans, dup_orphans, uniq_orphans, missing, biggest


def main():
    args = sys.argv[1:]
    strict = "--strict" in args
    summary = "--summary" in args
    ci_mode = "--ci" in args
    base = args[args.index("--ci") + 1] if ci_mode else None

    # 定位仓库根（含 img/ 或 .git 的目录）
    repo = os.getcwd()
    while not (os.path.isdir(os.path.join(repo, "img")) and os.path.isdir(os.path.join(repo, ".git"))) and repo != os.path.dirname(repo):
        repo = os.path.dirname(repo)
    os.chdir(repo)

    refs, missing = collect_md_refs(repo)
    images = disk_images(repo)
    referenced, orphans, dup_orphans, uniq_orphans, missing, biggest = full_report(repo, refs, missing, images)

    lines = []
    code = 0

    if ci_mode:
        # 只检查本次新增的图片：未引用 / 超大 => 失败
        try:
            added = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=A", base, "HEAD", "--", "img"],
                capture_output=True, text=True, check=True).stdout.splitlines()
        except subprocess.CalledProcessError:
            print(f"::warning::无法对比基准 {base}，跳过新增图片检查")
            added = []
        problems = []
        for rel in added:
            rel = rel.strip()
            if not rel or not IMG_EXT_RE.search(rel):
                continue
            p = os.path.join(repo, rel)
            if not os.path.isfile(p):
                continue  # 同一 PR 内又删除了
            if os.path.normpath(p) not in refs:
                problems.append(f"{rel}：未被任何 .md 引用（孤儿图）")
            size = os.path.getsize(p)
            if size > MAX_NEW_IMAGE_BYTES:
                problems.append(f"{rel}：{human(size)} 超过 512KB 上限，请先压缩（pngquant --quality=65-85）或转 WebP")
        if problems:
            code = 1
            for prob in problems:
                print(f"::error::{prob}")
            print(f"\n[CI] 新增图片检查：{len(problems)} 个问题，已阻断合并。")
        else:
            print(f"[CI] 新增图片检查通过：本次新增 {len([a for a in added if IMG_EXT_RE.search(a)])} 张，全部被引用且体积合规。")
        print(f"[CI] 存量状态（仅提示，不阻塞）：孤儿图 {len(orphans)} 张，如需清理见 docs/MAINTENANCE.md。")
    else:
        lines.append(f"磁盘图片总数      : {len(images)}")
        lines.append(f"被 md 引用        : {len(referenced)}")
        lines.append(f"未引用-有重复副本 : {len(dup_orphans)} 张 / {human(sum(os.path.getsize(p) for p in dup_orphans))}")
        lines.append(f"未引用-内容唯一   : {len(uniq_orphans)} 张 / {human(sum(os.path.getsize(p) for p in uniq_orphans))}")
        lines.append(f"引用缺失          : {len(missing)} 处")
        if orphans and not strict:
            lines.append("\n孤儿图示例（最多 20 条）：")
            lines += [f"  {os.path.relpath(p, repo)}" for p in orphans[:20]]
        lines.append("\n体积 Top10：")
        lines += [f"  {human(os.path.getsize(p)):>9}  {os.path.relpath(p, repo)}" for p in biggest]
        if strict and (orphans or missing):
            code = 1
            lines.insert(0, "[strict] 检查未通过！")

    text = "\n".join(lines)
    print(text)

    if summary and os.environ.get("GITHUB_STEP_SUMMARY"):
        md = ["## 🖼️ 图片健康报告", "```", text, "```"]
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write("\n".join(md) + "\n")

    sys.exit(code)


if __name__ == "__main__":
    main()
