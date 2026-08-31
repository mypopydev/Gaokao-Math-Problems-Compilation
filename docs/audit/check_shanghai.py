#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上海卷内容准确性审计（阶段 1+2）。

把本仓库 content/YYYY/shanghai*.tex 与上游 gaokaomath 的上海卷原始 PDF
建立映射，产出覆盖矩阵，并比较题量（LaTeX 侧可靠；PDF 侧为启发式估算）。

用法:
  python3 docs/audit/check_shanghai.py

输出:
  docs/audit/coverage.tsv   覆盖矩阵 + 题量对比
  docs/audit/gaps.txt       上游有但本仓库无的缺口
"""
import os
import re
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUR_CONTENT = os.path.join(REPO, "content")
UP_REGULAR = os.path.join(os.path.expanduser("~"),
                          "Sources/AI/gaokaomath/普通高考")
UP_SPRING = os.path.join(os.path.expanduser("~"),
                         "Sources/AI/gaokaomath/春季高考")

PROBLEM_RE = re.compile(r"\\begin\{problem\}")
ANSWER_RE = re.compile(r"\\begin\{answer\}")
SECTION_RE = re.compile(r"\\section\{([^}]*)\}")
CHAPTER_RE = re.compile(r"\\chapter\{([^}]*)\}")

# 上游题目编号行的启发式（两位数内编号；覆盖 1. / 1． / （1） / 1、 等）
UP_ITEM_RE = re.compile(r"^\s*(?:\(?\d{1,2}[.．、)）]|（\d{1,2}）)")


def find_our():
    out = []
    for root, _, files in os.walk(OUR_CONTENT):
        for f in files:
            if f.startswith("shanghai") and f.endswith(".tex"):
                year = os.path.basename(root)
                stem = f[:-4]
                out.append((int(year), stem, os.path.join(root, f)))
    out.sort()
    return out


def map_upstream(year, stem):
    y = str(year)
    if stem == "shanghai_spring":
        cands = [f"{y}春季上海.pdf", f"{y}上海春季.pdf"]
        base = UP_SPRING
    else:
        base = UP_REGULAR
        if stem == "shanghai_science":
            cands = [f"{y}上海理.pdf", f"{y}上海试点教材理.pdf"]
        elif stem == "shanghai_liberal":
            cands = [f"{y}上海文.pdf", f"{y}上海试点教材文.pdf"]
        elif stem == "shanghai":
            cands = [f"{y}上海.pdf"]
        else:
            return None
    for c in cands:
        p = os.path.join(base, y, c)  # 上游 PDF 位于 普通高考/YYYY/ 或 春季高考/YYYY/ 子目录
        if os.path.exists(p):
            return p
    return None


def our_counts(path):
    txt = open(path, encoding="utf-8").read()
    problems = len(PROBLEM_RE.findall(txt))
    answers = len(ANSWER_RE.findall(txt))
    chapters = CHAPTER_RE.findall(txt)
    sections = SECTION_RE.findall(txt)
    return problems, answers, chapters, sections


def up_counts(pdf):
    try:
        res = subprocess.run(["pdftotext", pdf, "-"],
                             capture_output=True, text=True, timeout=60)
    except Exception:
        return None, []
    text = res.stdout
    cnt = sum(1 for ln in text.splitlines() if UP_ITEM_RE.match(ln))
    secs = re.findall(r"(填空题|选择题|解答题|应用题|证明题|计算题)", text)
    return cnt, secs


def main():
    rows = []
    gaps = []
    for year, stem, path in find_our():
        up = map_upstream(year, stem)
        our_p, our_a, chaps, secs = our_counts(path)
        if up:
            up_p, up_secs = up_counts(up)
            up_str = os.path.relpath(up, os.path.expanduser("~"))
            up_sec_str = ",".join(sorted(set(up_secs)))
        else:
            up_p, up_secs, up_str, up_sec_str = ("-", [], "(缺失)", "")
            gaps.append(f"{year} {stem}  -> 上游无对应 PDF")
        rows.append((year, stem, our_p, our_a,
                     ",".join(secs), up_str, up_p, up_sec_str))

    # 反向：上游上海卷 PDF 是否都有对应
    up_files = []
    for base in (UP_REGULAR, UP_SPRING):
        for d in sorted(os.listdir(base)):
            dd = os.path.join(base, d)
            if not os.path.isdir(dd):
                continue
            try:
                yint = int(d)
            except ValueError:
                continue
            for fn in sorted(os.listdir(dd)):
                if "上海" in fn and fn.endswith(".pdf"):
                    up_files.append((yint, os.path.join(dd, fn)))

    # 构建已映射上游集合
    mapped_up = set()
    for year, stem, path in find_our():
        up = map_upstream(year, stem)
        if up:
            mapped_up.add(os.path.abspath(up))

    for year, up in up_files:
        if os.path.abspath(up) not in mapped_up:
            gaps.append(f"上游 {year} {os.path.basename(up)} -> 本仓库无对应")

    with open(os.path.join(os.path.dirname(__file__), "coverage.tsv"),
              "w", encoding="utf-8") as fh:
        fh.write("year\tstem\tour_problems\tour_answers\t"
                 "our_sections\tupstream_pdf\tupstream_problem_est\t"
                 "upstream_sections\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")

    with open(os.path.join(os.path.dirname(__file__), "gaps.txt"),
              "w", encoding="utf-8") as fh:
        if gaps:
            fh.write("\n".join(gaps) + "\n")
        else:
            fh.write("(无缺口)\n")

    # 控制台摘要
    print(f"本仓库上海卷文件数: {len(rows)}")
    print(f"已映射上游 PDF 数: {len(mapped_up)}")
    print(f"上游上海卷 PDF 数: {len(up_files)}")
    print(f"缺口数: {len(gaps)}")
    for g in gaps:
        print("  GAP:", g)
    # 题量对比异常（上游估算与本地差异较大）
    print("\n题量对比 (our / upstream_est):")
    for r in rows:
        year, stem, op, oa, osec, upstr, upp, us = r
        flag = ""
        if isinstance(upp, int) and op > 0:
            if upp == 0:
                flag = "  <-- 上游未抽到题号"
            elif abs(op - upp) > max(3, 0.3 * op):
                flag = "  <-- 差异较大"
        print(f"  {year} {stem:18s} our={op:3d} ans={oa:3d} up_est={str(upp):>4s}{flag}")


if __name__ == "__main__":
    main()
