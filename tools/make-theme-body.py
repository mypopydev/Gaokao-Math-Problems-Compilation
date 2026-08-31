#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""按课标主题抽取题目，生成“分主题分册”的正文 tex。

与 tools/make-body-index.sh（按地区/年份整卷拼接）不同，本脚本按
docs/classify/classification.json 中的主题字段重组题目：同一主题的题目
按年份倒序汇成一册，并保留原题号（\setcounter{probnum}{qidx-1}）与题源
标注（\probmeta{（2022·上海·秋·7）}）。

产物:
  <outdir>/body-<id>.tex       每个主题一册的正文（由 Theme.tex \input）
  <outdir>/theme-names.mk      供 Makefile 使用的 id/名称/题数映射
  <outdir>/manifest.tsv        id/名称/题数/册标题（人工核对用）

用法:
  python3 tools/make-theme-body.py                       # 默认 shanghai
  python3 tools/make-theme-body.py --area shanghai --outdir tmp/theme
  python3 tools/make-theme-body.py --answer              # 同时供答案册使用（正文相同）

说明: 题目册与答案册共用同一份 body-*.tex，区别仅在于 Theme.tex /
Theme-answer.tex 中的 \showanswerfalse / \showanswertrue。
"""
import argparse
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(REPO, "content")
CLASSIFY_DIR = os.path.join(REPO, "docs", "classify")
TAXO = os.path.join(CLASSIFY_DIR, "taxonomy.json")
CLASSIFICATION = os.path.join(CLASSIFY_DIR, "classification.json")

# 与 docs/classify/classify.py 保持一致的抽取正则（额外容忍可选参数）。
PROBLEM_RE = re.compile(r"\\begin\{problem\}(\[.*?\])?(.*?)\\end\{problem\}", re.S)
ANSWER_RE = re.compile(r"\\begin\{answer\}(.*?)\\end\{answer\}", re.S)
SOLUTION_RE = re.compile(r"\\begin\{solution\}(.*?)\\end\{solution\}", re.S)
# 章节标题：\chapter{2022年上海卷（秋）} / \chapter{1990年上海卷}
CHAPTER_RE = re.compile(r"\\chapter\{(\d{4})年(.+?)卷(?:（(.+?)）)?\}")

CN_NUM = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五",
          6: "六", 7: "七", 8: "八", 9: "九", 10: "十"}

# 主题册标题前缀：id 由 taxonomy.json 的 themes 顺序决定（1..N），0 为未分类附录。
UNC_ID = 0


def load_problems(path):
    r"""返回 [(optional_arg, body, answer, solution)]，顺序即 qidx。

    answer/solution 只在“本题 \end{problem} 与下一题 \begin{problem} 之间”
    的片段中查找，避免把后面题目的解析误挂到本题。
    """
    txt = open(path, encoding="utf-8-sig").read()
    matches = list(PROBLEM_RE.finditer(txt))
    out = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(txt)
        tail = txt[start:end]
        ans = ANSWER_RE.search(tail)
        sol = SOLUTION_RE.search(tail)
        out.append((
            m.group(1) or "",
            m.group(2).strip("\n"),
            ans.group(1).strip("\n") if ans else None,
            sol.group(1).strip("\n") if sol else None,
        ))
    return out


def parse_title(path):
    r"""从文件首个 \chapter 解析 (year, region, session)。"""
    txt = open(path, encoding="utf-8-sig").read()
    m = CHAPTER_RE.search(txt)
    if not m:
        return None
    return int(m.group(1)), m.group(2).strip(), (m.group(3) or "").strip()


def label(year, region, session, qidx, nonstd):
    r"""题源标注，如 （2022·上海·秋·7）；非课标单元追加 △非课标。"""
    parts = [str(year), region] + ([session] if session else []) + [str(qidx)]
    s = "（%s）" % "·".join(parts)
    if nonstd:
        # 用数学字体输出 △：直接写 Unicode 字符 △ 会被 CJK 字体取代，
        # PDF 文本层退化为 U+FFFD（无法复制/检索）。
        s += "\\textsuperscript{\\ensuremath{\\triangle}}非课标"
    return s


def write_if_changed(path, text):
    """仅在内容变化时写盘，避免 make 触发无谓的重新编译。"""
    try:
        if open(path, encoding="utf-8").read() == text:
            return False
    except OSError:
        pass
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--area", default="shanghai",
                    help="内容文件前缀过滤（默认 shanghai）")
    ap.add_argument("--classification", default=CLASSIFICATION)
    ap.add_argument("--taxonomy", default=TAXO)
    ap.add_argument("--outdir", default=os.path.join(REPO, "tmp", "theme"))
    args = ap.parse_args()

    taxo = json.load(open(args.taxonomy, encoding="utf-8"))
    rows = json.load(open(args.classification, encoding="utf-8"))
    if args.area != "all":
        rows = [r for r in rows if r["stem"].startswith(args.area)]
    nonstd = {u["id"] for u in taxo["units"] if u.get("out_of_standard")}

    themes = list(taxo["themes"])
    theme_id = {t: i + 1 for i, t in enumerate(themes)}
    theme_name = {i + 1: t for i, t in enumerate(themes)}
    theme_name[UNC_ID] = "未分类"

    # 按 (year, stem) 缓存文件内容，避免重复读盘。
    cache = {}
    def blocks(year, stem):
        key = (year, stem)
        if key not in cache:
            path = os.path.join(CONTENT, str(year), stem + ".tex")
            cache[key] = load_problems(path) if os.path.exists(path) else []
        return cache[key]

    titles = {}
    def title_of(year, stem):
        key = (year, stem)
        if key not in titles:
            path = os.path.join(CONTENT, str(year), stem + ".tex")
            info = parse_title(path) if os.path.exists(path) else None
            titles[key] = info or (year, "未知", stem)
        return titles[key]

    # 分组：theme_id -> [row]
    groups = {}
    missing = 0
    for r in rows:
        tid = theme_id.get(r["theme"], UNC_ID)
        groups.setdefault(tid, []).append(r)

    os.makedirs(args.outdir, exist_ok=True)
    manifest = []

    for tid in sorted(groups, key=lambda i: (i == UNC_ID, i)):
        rs = groups[tid]
        # 年份倒序；同年按文件名字典序，再按题号升序。
        rs = sorted(rs, key=lambda r: (-r["year"], r["stem"], r["qidx"]))
        name = theme_name[tid]
        head = "主题%s %s" % (CN_NUM.get(tid, str(tid)), name) if tid != UNC_ID \
            else "附录 未分类"
        n_nonstd = sum(1 for r in rs if r["primary"] in nonstd)
        n_ans = 0

        lines = []
        lines.append("% 自动生成，请勿手改：python3 tools/make-theme-body.py")
        lines.append("\\chapter*{%s}" % head)
        lines.append("\\addcontentsline{toc}{chapter}{%s}" % head)
        lines.append("\\markboth{%s}{%s}" % (head, head))
        lines.append("\\begin{center}\\small\\color{gray}")
        lines.append("本册共 %d 题，按年份倒序编排；题号沿用原试卷题号，"
                     "题首灰色小字为题源（年份·省市·卷别·题号）." % len(rs))
        if n_nonstd:
            lines.append("\\par 其中 %d 题标 "
                         "\\textsuperscript{\\ensuremath{\\triangle}}非课标，"
                         "属超出课标必修/选择性必修范围的内容（如微积分、"
                         "矩阵与行列式、参数方程、算法初步等），"
                         "按内容相近的主题归册." % n_nonstd)
        lines.append("\\end{center}")
        lines.append("")

        cur_year = None
        for r in rs:
            y, stem, q = r["year"], r["stem"], r["qidx"]
            bl = blocks(y, stem)
            if q > len(bl):
                missing += 1
                print("make-theme-body: 缺少题块 %s/%s#%d" % (y, stem, q),
                      file=sys.stderr)
                continue
            opt, body, ans, sol = bl[q - 1]
            if ans or sol:
                n_ans += 1
            if y != cur_year:
                cur_year = y
                lines.append("\\section*{%d年}" % y)
                lines.append("\\addcontentsline{toc}{section}{%d年}" % y)
                lines.append("")
            _, region, session = title_of(y, stem)
            lines.append("\\setcounter{probnum}{%d}" % (q - 1))
            lines.append("\\begin{problem}%s" % opt)
            lines.append("\\probmeta{%s}" % label(
                y, region, session, q, r["primary"] in nonstd))
            lines.append(body.rstrip())
            lines.append("\\end{problem}")
            if ans is not None:
                lines.append("\\begin{answer}")
                lines.append(ans.rstrip())
                lines.append("\\end{answer}")
            if sol is not None:
                lines.append("\\begin{solution}")
                lines.append(sol.rstrip())
                lines.append("\\end{solution}")
            lines.append("")

        out = os.path.join(args.outdir, "body-%d.tex" % tid)
        write_if_changed(out, "\n".join(lines) + "\n")

        # 编译入口：把正文路径注入共用的 Theme*.tex，Makefile 直接编译它。
        rel = os.path.relpath(out, REPO).replace(os.sep, "/")
        for tag, driver in (("", "Theme.tex"), ("answer-", "Theme-answer.tex")):
            drv = os.path.join(args.outdir, "driver-%s%d.tex" % (tag, tid))
            write_if_changed(
                drv,
                "%% 自动生成，请勿手改：python3 tools/make-theme-body.py\n"
                "\\newcommand{\\themebodyfile}{%s}\n"
                "\\input{%s}\n" % (rel, driver))

        manifest.append((tid, name, head, len(rs), n_nonstd, n_ans))
        print("make-theme-body: %s  %d 题 (非课标 %d, 有答案/解析 %d)"
              % (os.path.relpath(out, REPO), len(rs), n_nonstd, n_ans))

    with open(os.path.join(args.outdir, "manifest.tsv"), "w",
              encoding="utf-8") as fh:
        fh.write("id\tname\thead\tcount\tnonstd\twith_answer\n")
        for tid, name, head, n, ns, na in manifest:
            fh.write("\t".join(map(str, (tid, name, head, n, ns, na))) + "\n")

    with open(os.path.join(args.outdir, "theme-names.mk"), "w",
              encoding="utf-8") as fh:
        fh.write("# 自动生成，请勿手改：python3 tools/make-theme-body.py\n")
        fh.write("THEME_IDS := %s\n"
                 % " ".join(str(t[0]) for t in manifest))
        for tid, name, head, n, ns, na in manifest:
            fh.write("THEME_NAME_%d := %s\n" % (tid, name))
            fh.write("THEME_HEAD_%d := %s\n" % (tid, head))
            fh.write("THEME_COUNT_%d := %d\n" % (tid, n))
    if missing:
        print("make-theme-body: 警告，%d 条分类记录未找到题块" % missing,
              file=sys.stderr)


if __name__ == "__main__":
    main()
