#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按《普通高中数学课程标准（2017版2025修订）》对高考题做规则/关键词分类。

用法:
  python3 docs/classify/classify.py                 # 默认抽样年份 2022/2017/2000
  python3 docs/classify/classify.py 2022 2017 2000  # 指定年份
  python3 docs/classify/classify.py --all           # 全部年份(上海卷)

输出:
  docs/classify/classification.tsv   每行一题: year, stem, qidx, primary_unit,
                                      theme, module, matched_units, competencies, level
  docs/classify/classification.json  同上(机器可读)
"""
import os
import re
import sys
import json

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUR_CONTENT = os.path.join(REPO, "content")
TAXO = os.path.join(os.path.dirname(__file__), "taxonomy.json")
OUT_DIR = os.path.dirname(__file__)

PROBLEM_RE = re.compile(r"\\begin\{problem\}(.*?)\\end\{problem\}", re.S)

# 模块 -> 学业质量水平(启发式估算, 非精确)
MODULE_LEVEL = {
    "必修": "水平1-2",
    "选择性必修": "水平2-3",
    "选修": "水平3",
}


def load_taxo():
    return json.load(open(TAXO, encoding="utf-8"))


def extract_problems(path):
    txt = open(path, encoding="utf-8").read()
    return [m.group(1) for m in PROBLEM_RE.finditer(txt)]


def classify(text, taxo):
    text = text or ""
    # 归一化：避免关键词在中文/LaTeX 常用词中的子串误命中
    # - '\i'(虚数单位) vs '\in'(属于) / '\bs{i}'(向量基)
    # - '\bar' 补集 vs 共轭：taxonomy 已用 '\bar z' 精确化
    text = text.replace("\\in", "∈elem").replace("\\bs{i}", "𝐛𝐢𝐬")
    # 中文歧义保护：'复数' 若嵌在 '重复数字/重复数据' 中(如"无重复数字")则不算命中
    fushu_allowed = "重复数字" not in text and "重复数据" not in text
    scored = []
    for u in taxo["units"]:
        hits = [kw for kw in u["kw"]
                if (kw == "复数" and fushu_allowed and kw in text) or
                   (kw != "复数" and kw in text)]
        if hits:
            scored.append((u, len(hits), hits))
    scored.sort(key=lambda x: (-x[1], taxo["units"].index(x[0])))
    # 三角函数优先：含三角符号(\sin/\cos/\tan 等)且语义为“最值/值域/周期/解集”的题
    # 应归三角函数，而非被“不等式与方程”的宽泛词(最大/最小/解集)吸走。
    trig_u = next((u for u in taxo["units"] if u["id"] == "trig"), None)
    if trig_u is not None and re.search(r"\\(?:sin|cos|tan|cot|sec|csc)\b", text):
        if scored and scored[0][0]["id"] == "inequality" and re.search(
                r"最值|最大值|最小值|值域|周期|解集", text):
            scored = [s for s in scored if s[0]["id"] != "trig"]
            scored.insert(0, (trig_u, 1, ["(三角优先)"]))
    # 立体几何优先：含立体主体词(棱柱/棱锥/圆柱/圆锥/球/截面/体积等)的题应归
    # 立体几何初步/空间向量，而非被“直线与圆”的宽泛词(直线/圆/圆心)吸走。
    # 注意：保护“三角形的外接圆/内切圆”(属直线与圆)，故仅在不含该场景时触发。
    if scored and scored[0][0]["id"] == "line_circle":
        has_solid = re.search(
            r"棱锥|棱柱|棱台|正方体|长方体|四面体|圆柱|圆锥|圆台|球体|球面|"
            r"旋转体|母线|截面|二面角|异面|线面|面面|点到平面|体积|表面积|侧面积|"
            r"三视图|直观图", text)
        tri_circum = re.search(r"△|三角形", text) and ("外接圆" in text or "内切圆" in text)
        if has_solid and not tri_circum:
            hit_solid = [s for s in scored if s[0]["id"] in ("solid_basic", "space_vec")]
            if hit_solid:
                target_id = hit_solid[0][0]["id"]
                scored = [s for s in scored if s[0]["id"] != target_id]
                scored.insert(0, (hit_solid[0][0], 1, ["(立体优先)"]))
    # 复数优先：含复数/虚数/复平面/共轭/实部/虚部等信号的题应归复数，
    # 而非被“直线与圆/平面向量”的坐标/轨迹词吸走。
    if scored and scored[0][0]["id"] in ("line_circle", "vector2d"):
        if re.search(r"复数|虚数|复平面|共轭|实部|虚部|虚根|虚数单位|辐角主值", text):
            hit_complex = any(u["id"] == "complex" for u, _, _ in scored)
            if hit_complex:
                scored = [s for s in scored if s[0]["id"] != "complex"]
                scored.insert(0, (next(u for u in taxo["units"] if u["id"] == "complex"), 1, ["(复数优先)"]))
    # 统计优先：含统计核心词(茎叶图/直方图/百分位数/中位数/回归/相关系数等)的题
    # 应归统计，而非被“排列/选取”等计数噪声词吸走(如茎叶图的“排列在中间”非排列数)。
    if scored and scored[0][0]["id"] == "counting":
        if re.search(r"茎叶图|直方图|百分位|中位数|回归|相关系数|独立性检验|"
                     r"频率分布|方差分析|置信|加权平均|样本(?!点)", text):
            hit_stat = [s for s in scored if s[0]["id"] == "stat"]
            if hit_stat:
                scored = [s for s in scored if s[0]["id"] != "stat"]
                scored.insert(0, (hit_stat[0][0], 1, ["(统计优先)"]))

    def promote(unit_id, marker):
        nonlocal scored
        hit = next((s for s in scored if s[0]["id"] == unit_id), None)
        if hit is None:
            return
        scored = [s for s in scored if s[0]["id"] != unit_id]
        scored.insert(0, (hit[0], 1, [marker]))
        return True

    # 阶段一优先级规则：优先识别被通用关键词吞掉的专题。
    # 概率 > 非课标专题 > 圆锥曲线；统计优先已在上方执行，因此统计不会被概率覆盖。
    if scored and scored[0][0]["id"] in {
            "counting", "set", "vector2d", "inequality", "logic"}:
        if re.search(r"概率|分布列|随机变量|古典概型|互斥|独立事件|正态分布|二项分布", text):
            promote("prob", "(概率优先)")

    # 椭圆/双曲线/抛物线等专属词优先于“直线/圆/最大值”等通用词。
    # 复数题的复平面轨迹可能在选项中出现这些词，保持复数分类。
    if (scored and scored[0][0]["id"] != "prob"
            and not re.search(r"复数|虚数|复平面|共轭|实部|虚部|虚根", text)):
        if re.search(r"椭圆|双曲线|抛物线|焦点|离心率|渐近线|准线|圆锥曲线", text):
            promote("conic", "(圆锥曲线优先)")

    # 非课标专题最后提升，覆盖圆锥曲线选项噪声；不把“极限”作为微积分信号，
    # 因数列中的无穷等比数列极限仍属于数列单元。
    nonstandard_priority = (
        ("matrix", r"矩阵|行列式"),
        ("parametric", r"参数方程|极坐标"),
        ("calc_adv", r"定积分|不定积分|微积分"),
        ("algorithm", r"程序框图|(?<!运)算法|框图"),
    )
    if scored and scored[0][0]["id"] != "prob":
        for unit_id, signal in nonstandard_priority:
            if re.search(signal, text):
                promote(unit_id, "(非课标优先)")
                break

    if not scored:
        # “函数” 兜底：含 函数 但无具体单元命中
        if "函数" in text:
            return dict(primary="funcprop", primary_name="函数概念与性质",
                        theme="函数", module="必修",
                        matched=["函数概念与性质(兜底)"],
                        comp=["数学抽象", "数学运算"], level="水平1-2",
                        note="仅命中'函数'兜底")
        return dict(primary=None, primary_name="未分类", theme="", module="",
                    matched=[], comp=[], level="", note="无可匹配关键词")
    primary_u, _, _ = scored[0]
    matched_names = [u["name"] for u, _, _ in scored]
    # 核心素养 = 命中单元的并集(取前若干个主要单元)
    comps = []
    for u, _, _ in scored[:3]:
        for c in u["comp"]:
            if c not in comps:
                comps.append(c)
    return dict(
        primary=primary_u["id"],
        primary_name=primary_u["name"],
        theme=primary_u["theme"],
        module=primary_u["module"],
        matched=matched_names,
        comp=comps,
        level=MODULE_LEVEL.get(primary_u["module"], ""),
        note="",
    )


def main():
    args = sys.argv[1:]
    if args and args[0] == "--all":
        years = "ALL"
    elif args:
        years = [int(a) for a in args]
    else:
        years = [2022, 2017, 2000]  # 默认抽样

    taxo = load_taxo()
    rows = []
    files = []
    for root, _, fs in os.walk(OUR_CONTENT):
        for f in fs:
            if f.startswith("shanghai") and f.endswith(".tex"):
                y = int(os.path.basename(root))
                if years != "ALL" and y not in years:
                    continue
                files.append((y, f[:-4], os.path.join(root, f)))
    files.sort()

    for y, stem, path in files:
        probs = extract_problems(path)
        for i, text in enumerate(probs, 1):
            r = classify(text, taxo)
            rows.append((y, stem, i, r))

    # 写 TSV
    tsv = os.path.join(OUT_DIR, "classification.tsv")
    with open(tsv, "w", encoding="utf-8") as fh:
        fh.write("year\tstem\tqidx\tprimary_unit\ttheme\tmodule\t"
                 "matched_units\tcompetencies\tlevel\tnote\n")
        for y, stem, i, r in rows:
            fh.write("\t".join([
                str(y), stem, str(i), r["primary_name"], r["theme"],
                r["module"], ";".join(r["matched"]), ";".join(r["comp"]),
                r["level"], r["note"],
            ]) + "\n")

    js = [{"year": y, "stem": stem, "qidx": i, **r}
          for y, stem, i, r in rows]
    with open(os.path.join(OUT_DIR, "classification.json"), "w", encoding="utf-8") as fh:
        json.dump(js, fh, ensure_ascii=False, indent=1)

    # 控制台摘要
    total = len(rows)
    unc = sum(1 for _, _, _, r in rows if r["primary"] is None)
    fb = sum(1 for _, _, _, r in rows if r.get("note", "").startswith("仅命中"))
    print(f"分类完成: {total} 题  (年份范围: {years if years!='ALL' else '全部'})")
    print(f"  未分类: {unc}   函数兜底: {fb}")
    print(f"  TSV: {tsv}")
    print(f"  JSON: {os.path.join(OUT_DIR, 'classification.json')}")
    # 主题分布
    from collections import Counter
    c = Counter(r["theme"] for _, _, _, r in rows)
    print("  主题分布:", dict(c))


if __name__ == "__main__":
    main()
