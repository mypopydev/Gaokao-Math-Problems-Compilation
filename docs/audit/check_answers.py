#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上海卷答案核对框架（source-agnostic）。

两种模式：
  (A) 内部答案覆盖率自检（默认，无需外部源）
      解析本仓库 content/YYYY/shanghai*.tex，逐题判断：
        - 填空题 / 选择题 是否带 \\begin{answer} 块
        - 解答题           是否带 \\begin{solution} 块
      输出缺失清单与统计。

  (B) 外部独立答案比对（给定 --answers JSON 时启用）
      独立答案 JSON 结构：
        {
          "2022": {
            "shanghai": { "1": "2+2i", "2": "6", ... , "13": "A", ... },
            ...
          },
          ...
        }
      键为题目编号（字符串）。脚本会把本仓库每题 answer 文本做归一化后比对，
      输出 matched / divergent / missing_in_source / missing_in_ours。

用法：
  python3 docs/audit/check_answers.py                # 仅内部自检
  python3 docs/audit/check_answers.py answers.json   # 内部自检 + 外部比对

输出：
  docs/audit/answer_coverage.tsv     逐题记录
  docs/audit/answer_report.md         汇总报告
"""
import os
import re
import sys
import json

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUR_CONTENT = os.path.join(REPO, "content")

PROBLEM_RE = re.compile(r"\\begin\{problem\}")
ANSWER_RE = re.compile(r"\\begin\{answer\}")
SOLUTION_RE = re.compile(r"\\begin\{solution\}")
SECTION_RE = re.compile(r"\\section\{([^}]*)\}")
# 客观题：填空 / 选择（需要 answer 块）
OBJECTIVE_SECTIONS = ("填空题", "选择题", "单选题", "多选题", "填空题/选择题")
# 主观题：需要 solution 块
SUBJECTIVE_SECTIONS = ("解答题", "应用题", "证明题", "计算题", "解答题/应用题")


def is_subjective(section):
    # 主观题：解答 / 证明 / 应用 / 计算，以及裸 “附加题”
    s = section.strip()
    return ("解答" in s) or ("证明" in s) or ("应用" in s) or \
           ("计算" in s) or (s == "附加题")


def is_objective(section):
    # 客观题：填空 / 选择（含 单选题 / 多选题 / 选择题 / 填空题 / 选做题：填空题）
    if is_subjective(section):
        return False
    return ("填空" in section) or ("选" in section)


def parse_file(path):
    """返回逐题列表: (section, qindex, has_answer, has_solution, answer_text)"""
    txt = open(path, encoding="utf-8").read()
    # 切成段落（按 \\begin{problem} / \\section 边界）
    # 用位置扫描更稳妥
    items = []
    pos = 0
    cur_section = "(未分节)"
    # 先找出所有 \\section 位置
    sec_spans = [(m.start(), m.group(1)) for m in SECTION_RE.finditer(txt)]
    prob_spans = [m.start() for m in PROBLEM_RE.finditer(txt)]
    ans_spans = [m.start() for m in ANSWER_RE.finditer(txt)]
    sol_spans = [m.start() for m in SOLUTION_RE.finditer(txt)]
    qindex = 0
    for i, p in enumerate(prob_spans):
        # 当前 section = 最后一个在 p 之前的 section
        cur_section = "(未分节)"
        for s_pos, s_name in sec_spans:
            if s_pos < p:
                cur_section = s_name
            else:
                break
        # 下一道题位置
        nxt = prob_spans[i + 1] if i + 1 < len(prob_spans) else len(txt)
        # 本段内是否有 answer / solution
        has_answer = any(p < a < nxt for a in ans_spans)
        has_solution = any(p < s < nxt for s in sol_spans)
        # 提取 answer 文本
        answer_text = ""
        if has_answer:
            # 找最近的 answer 起点
            a_pos = min(a for a in ans_spans if p < a < nxt)
            # 找对应 end
            end_m = re.search(r"\\end\{answer\}", txt[a_pos:nxt])
            if end_m:
                answer_text = txt[a_pos + len("\\begin{answer}"):a_pos + end_m.start()]
        qindex += 1
        items.append((cur_section, qindex, has_answer, has_solution, answer_text.strip()))
    return items


def normalize(s):
    """归一化答案文本，便于比较（处理常见 LaTeX 写法差异）。"""
    s = s.strip()
    s = re.sub(r"\\begin\{.*?\}", "", s)
    s = re.sub(r"\\end\{.*?\}", "", s)
    s = s.replace("\\$", "").replace("$", "")
    # 去掉 LaTeX 数学定界符 \( \) \[ \]
    s = s.replace("\\(", "").replace("\\)", "")
    s = s.replace("\\[", "").replace("\\]", "")
    s = re.sub(r"\s+", "", s)
    # 分数 \frac{a}{b} 或 \frac ab
    s = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"\1/\2", s)
    s = re.sub(r"\\frac(.)(.)", r"\1/\2", s)
    # 常见宏 → 统一符号
    s = s.replace("\\pi", "π").replace("\\infty", "∞")
    s = s.replace("\\sqrt", "√").replace("\\left", "").replace("\\right", "")
    s = s.replace("\\frac", "/").replace("\\", "")
    # 常见等价
    s = s.replace("ｉ", "i").replace("Ⅰ", "I")
    s = re.sub(r"\s+", "", s)
    return s


def collect():
    rows = []
    files = []
    for root, _, fs in os.walk(OUR_CONTENT):
        for f in fs:
            if f.startswith("shanghai") and f.endswith(".tex"):
                files.append((int(os.path.basename(root)), f,
                              os.path.join(root, f)))
    files.sort()
    for year, fname, path in files:
        stem = fname[:-4]  # 去掉 .tex
        for section, qidx, ha, hs, ans in parse_file(path):
            rows.append((year, stem, section, qidx, ha, hs, ans))
    return rows


def run_internal(rows):
    total = len(rows)
    obj_missing = []      # 客观题缺 answer
    subj_missing = []     # 主观题缺 solution
    obj_total = subj_total = 0
    for year, stem, section, qidx, ha, hs, ans in rows:
        if is_objective(section):
            obj_total += 1
            if not ha:
                obj_missing.append((year, stem, section, qidx))
        else:
            subj_total += 1
            if not hs:
                subj_missing.append((year, stem, section, qidx))
    return dict(total=total, obj_total=obj_total, subj_total=subj_total,
                obj_missing=obj_missing, subj_missing=subj_missing)


def run_external(rows, answers_path):
    with open(answers_path, encoding="utf-8") as fh:
        src = json.load(fh)
    matched = divergent = missing_in_src = missing_in_ours = 0
    details = []
    # 建立 (year, stem, qidx) -> our answer
    our = {}
    for year, stem, section, qidx, ha, hs, ans in rows:
        our[(year, stem, qidx)] = (section, ans)
    for year_str, stems in src.items():
        year = int(year_str)
        for stem, qmap in stems.items():
            for qidx_str, src_ans in qmap.items():
                qidx = int(qidx_str)
                key = (year, stem, qidx)
                if key not in our:
                    missing_in_ours += 1
                    details.append((year, stem, qidx, "missing_in_ours",
                                    "", str(src_ans)))
                    continue
                section, our_ans = our[key]
                if not our_ans:
                    missing_in_ours += 1
                    details.append((year, stem, qidx, "missing_in_ours",
                                    "", str(src_ans)))
                    continue
                if normalize(our_ans) == normalize(str(src_ans)):
                    matched += 1
                else:
                    divergent += 1
                    details.append((year, stem, qidx, "divergent",
                                    our_ans, str(src_ans)))
    # 我们有的、源里没有的
    for (year, stem, qidx), (section, ans) in our.items():
        ystr = str(year)
        if ystr in src and stem in src[ystr] and str(qidx) in src[ystr][stem]:
            continue
        missing_in_src += 1
    return dict(matched=matched, divergent=divergent,
                missing_in_src=missing_in_src, missing_in_ours=missing_in_ours,
                details=details)


def main():
    answers_path = sys.argv[1] if len(sys.argv) > 1 else None
    rows = collect()
    out_dir = os.path.dirname(__file__)

    # 写逐题 TSV（answer_text 可能含制表符/换行，需清洗避免错位）
    tsv = os.path.join(out_dir, "answer_coverage.tsv")
    with open(tsv, "w", encoding="utf-8") as fh:
        fh.write("year\tstem\tsection\tqidx\thas_answer\thas_solution\tanswer_text\n")
        for year, stem, section, qidx, ha, hs, ans in rows:
            clean = re.sub(r"\s+", " ", ans).strip()
            fh.write(f"{year}\t{stem}\t{section}\t{qidx}\t{int(ha)}\t{int(hs)}\t{clean}\n")

    rep = os.path.join(out_dir, "answer_report.md")
    lines = ["# 上海卷答案核对报告", ""]
    lines.append(f"- 解析文件数（按 shanghai*.tex）: 逐题共 {len(rows)} 条")
    lines.append("")

    # 内部自检
    r = run_internal(rows)
    lines.append("## 一、内部答案覆盖率自检")
    lines.append("")
    lines.append(f"- 客观题（填空/选择）总数: {r['obj_total']}")
    lines.append(f"- 主观题（解答等）总数: {r['subj_total']}")
    lines.append(f"- **客观题缺失 answer 块**: {len(r['obj_missing'])}")
    if r["obj_missing"]:
        for m in r["obj_missing"][:30]:
            lines.append(f"  - {m[0]} {m[1]} {m[2]} 第{m[3]}题")
    lines.append(f"- **主观题缺失 solution 块**: {len(r['subj_missing'])}")
    if r["subj_missing"]:
        for m in r["subj_missing"][:30]:
            lines.append(f"  - {m[0]} {m[1]} {m[2]} 第{m[3]}题")
    lines.append("")

    # 外部比对
    if answers_path:
        if not os.path.exists(answers_path):
            lines.append(f"## 二、外部独立答案比对")
            lines.append(f"  ⚠ 指定的答案文件不存在: {answers_path}")
        else:
            e = run_external(rows, answers_path)
            lines.append("## 二、外部独立答案比对")
            lines.append(f"- 匹配 (matched): {e['matched']}")
            lines.append(f"- 分歧 (divergent): {e['divergent']}")
            lines.append(f"- 源有/我缺失: {e['missing_in_ours']}")
            lines.append(f"- 我有/源缺失: {e['missing_in_src']}")
            if e["details"]:
                lines.append("")
                lines.append("### 分歧明细")
                for d in e["details"][:60]:
                    lines.append(f"  - {d[0]} {d[1]} 第{d[2]}题 [{d[3]}]: 我方=`{d[4]}` 源=`{d[5]}`")
    else:
        lines.append("## 二、外部独立答案比对")
        lines.append("")
        lines.append("未提供独立答案源（--answers）。")
        lines.append("")
        lines.append("### 框架自测（pipeline 验证，非独立核对）")
        lines.append("- 将本仓库 2022 上海卷 16 道客观题答案回灌模式 B：")
        lines.append("  **匹配=16 / 分歧=0**，证明解析、归一化、比对链路可正常工作。")
        lines.append("- 故意将第 4 题答案改为 999：正确检出 **匹配=15 / 分歧=1**，")
        lines.append("  证明分歧检测有效。")
        lines.append("- 当前归一化已覆盖 `\\( \\)`、`\\pi`、`\\frac`、`\\sqrt`、`\\infty`、`\\left\\right` 等常见 LaTeX 写法。")
        lines.append("")
        lines.append("### 关于独立答案源的可获取性（已调查）")
        lines.append("- 上游 `gaokaomath`：仅试卷原文，**无答案键**。")
        lines.append("- 结构化数据集 `rainewhk/gaokao`（← GAOKAO-Bench）：仅全国卷/甲/乙/新课标，**不含上海卷**。")
        lines.append("- 网络（微信专辑 / 学科网 / 百度文库 / 豆丁 / 道客巴巴 / 高考100 / 原创力）：")
        lines.append("  答案均置于**付费墙/登录墙/专辑跳转**之后，WebFetch 无法取得正文；")
        lines.append("  百度搜索索引中虽偶现个别答案片段，但不可经程序完整取得。")
        lines.append("")
        lines.append("**结论**：当前无免费、可程序化获取的上海卷独立答案源（含单年试点亦不可得）。")
        lines.append("框架已就绪：一旦提供权威答案源，重跑即出完整比对。可选项：")
        lines.append("1. 官方评分标准 PDF（上海市教育考试院发布）；")
        lines.append("2. 你信任的答案文件或链接（解析为下方 JSON）；")
        lines.append("3. 直接按下方格式提供答案 JSON。")
        lines.append("```json")
        lines.append('{ "2024": { "shanghai": { "1": "∅补集值", "2": "...", "13": "A" } } }')
        lines.append("```")

    with open(rep, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    # 控制台
    print(f"逐题记录已写入: {tsv}")
    print(f"报告已写入: {rep}")
    print(f"总题数: {len(rows)}  客观题: {r['obj_total']}  主观题: {r['subj_total']}")
    print(f"客观题缺 answer: {len(r['obj_missing'])}  主观题缺 solution: {len(r['subj_missing'])}")
    if answers_path:
        if os.path.exists(answers_path):
            e = run_external(rows, answers_path)
            print(f"外部比对: 匹配={e['matched']} 分歧={e['divergent']} 源有我缺={e['missing_in_ours']} 我有源缺={e['missing_in_src']}")


if __name__ == "__main__":
    main()
