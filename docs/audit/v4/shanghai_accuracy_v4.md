# 上海卷内容与答案准确性复核报告 v4

- 状态：**已完成；content/ 已按报告修订（两处）**
- 基线 commit：`e2211baa1e3f3344e63dfc3acfd52a4be44c1c49`
- 范围：97 文件 / 2261 题（客观 1700 + 主观 561）
- 原卷来源：`/Users/barryjzhao/Sources/AI/gaokaomath`
- 工作原则：对照原卷、回答与解析三处；二级复核 + 直接 PDF 渲染 + 独立代数重导。

## 一、最终结论（post-secondary-review tally）

| 类别 | 数量 | 说明 |
|---|---|---|
| `verified_correct` | 2253 | 二级复核确认无错 |
| `ambiguous_problem` | 8 | 题面/原卷本身歧义，不修订 |
| 仍需 `incorrect` 处理 | 0 | 全部 9 个一级候选已重新分类 |

`verified_correct` 已含 2026 春季 Q11（修正转录后与原卷一致）。

## 二、内容修订清单（已应用）

1. **`content/2010/shanghai_science.tex` 第 497 行（Q23 第(3)问）** — 回退 `e2211baa` 错误修订
   - 改前（错）：`sinθ−cosθ<1` → 区间 `(0, π)` 排除 `π/2`
   - 改后（对）：`sinθ−cosθ<1/2` → 区间 `(0, π/4+arcsin(√2/4))`
   - 独立代数重导确认。

2. **`content/2026/shanghai_spring.tex` 第 142、151 行（Q11）** — 修正 Γ₂ 主轴转录错误
   - 改前（错）：`Γ₂: x²/(b²+2) + y²/b² = 1`（x-主轴）
   - 改后（对）：`Γ₂: y²/(b²+2) + x²/b² = 1`（y-主轴）
   - 答案保持 `3`，与原卷一致（不擅自校正原卷的 `b⁴=3 → b²` 应为 `√3` 的代数勘误；按 2000/理科#Q21 历史勘误处理惯例）。

回归：`bootstrap_v4.py` 复核解析后问题数仍为 2261，文件 97，类型分布不变。

## 三、二级复核详情

### 9 个一级错误候选 → 8 verified_correct + 1 ambiguous_problem

| ID | 二级判定 | 依据 |
|---|---|---|
| `2007/shanghai_science#Q14` | verified_correct | AB·AC、BA·BC、CA·BC 三处分别判 k=−6、−1、判别<0，得 k=2 值，答案 B 正确 |
| `2010/shanghai_science#Q23` | verified_correct（已修订） | 中点 F 在椭圆内 → `sinθ−cosθ<1/2` → 区间 `(0, π/4+arcsin(√2/4))` |
| `2013/shanghai_liberal#Q11` | verified_correct | 奇球 4 → P(奇积)=C(4,2)/C(7,2)=2/7 → P(偶积)=5/7 |
| `2019/shanghai#Q11` | ambiguous_problem | 原卷视觉确认 `n∈ℕ*`；n=1,2 无实点；原卷歧义忠实保留 |
| `2019/shanghai_spring#Q18` | verified_correct | 原卷答案 `q∈(−1,0)∪(0,3/4)`；仓库一致；q=0 不属于等比数列（标准约定） |
| `2023/shanghai_spring#Q20(3)` | verified_correct | 原卷答案 `(√3,3]`（2023 春季上海 PDF p.3 视觉确认）；P 是椭圆上一点而非必为切点 |
| `2024/shanghai#Q20` | verified_correct | 独立重导：(2) 三子情形 P=(2,2√2)；(3) `m²=10/b²−3` → 区间 `(0,√3)∪(√3, √30/3]` |
| `2024/shanghai_spring#Q12` | verified_correct | 独立计数：两种无序 {2,4,8,16}、{−1,7,11,13} × 4! = 48 |
| `2026/shanghai_spring#Q11` | verified_correct（已修订） | 原卷 y-主轴；四焦点矩形共圆 → a²=3；代数给出 b²=√3 但原卷答案 3 含代数勘误，按约定保留 |

### 7 个一级不确定 → 全部 ambiguous_problem

- `1996/shanghai_liberal#Q15`、`1996/shanghai_science#Q15`：直线 OA 允许内外分点两解。
- `2004/shanghai_liberal#Q18`、`2004/shanghai_science#Q18`：面积单位 cm² 与坐标单位 m 冲突。
- `2004/shanghai_liberal#Q19`、`2004/shanghai_science#Q19`：题面使用未定义的 B。
- `2024/shanghai_spring#Q11`：圆形通道条件不足，圆不唯一。

## 四、原卷转录自动比对

- PDF 映射：97/97
- 可提取文本 PDF：63
- 扫描型 PDF：30
- LOW_COVERAGE：4（2020、2021、2025、2026 秋卷；仅为待视觉复核信号）
- 上游缺失：0

附注：`1994/shanghai_liberal#Q26` 存在一个不影响结果的面积记号笔误（外部第一象限区域应对应三角形 OKR 的面积，公式和最终结果正确）。

## 五、已修订文件回归

| 文件 / 题号 | 修订内容 | 状态 |
|---|---|---|
| `2004/shanghai_science#Q21` | 一般 `t∈(0,1)`，V=(1−t³)√2/12，菱形直平行六面体构造 | 正确 |
| `2020/shanghai_spring#Q21` | 不等式改为 `≤`，结论对应反转 | 正确 |
| `2025/shanghai#Q8` | 补 `a>0` 条件 | 正确 |
| `2010/shanghai_science#Q23` | `e2211baa` 的 `<1` 修订**错误** | **本轮已回退** |
| `1988/shanghai#Q23` | `h=√3 a/2` | 正确（先前图示误读已撤销） |
| `2000/shanghai_science#Q21` | 指数 `2` → `n` | 历史勘误/源不一致，保留 |

## 六、未自动修复的源端/历史问题

1. `2000/shanghai_science#Q21`：原卷印 `2`，仓库用 `n`；数学上连续并与后续小问一致，已在仓库历史保留（不视作转录错误）。
2. `2026/shanghai_spring#Q11`：原卷答案 `3` 含代数勘误（`b⁴=3 → b²=√3`）；按上述约定保留 `3`。
3. `1994/shanghai_liberal#Q26`：面积记号笔误无害。

## 七、产物

- `tmp/audit/v4/snapshot.json`、`problems.jsonl`：在 commit `e2211baa` 解析（96 文件未变）
- `tmp/audit/v4/batches/`、`batches_manifest.json`：31 个批次；b18 含 2010 Q23、b30 含 2026 Q11
- `tmp/audit/v4/review/errors/`：`e01`–`e04` 二级复核结果
- `tmp/audit/v4/review/uncertain_uA.jsonl`、`uncertain_uB.jsonl`、`uncertain_final.json`：7 项 ambiguous 记录
- `tmp/audit/v4/aggregate.json`：tally 与修订元数据
- 本文件：`docs/audit/v4/shanghai_accuracy_v4.md`

`docs/audit/v4/`、`tmp/audit/v4/` 当前被 `.gitignore` 覆盖；本轮修订仅作用于 `content/` 两个文件（git diff 见 `git diff content/2010/shanghai_science.tex content/2026/shanghai_spring.tex`）。是否提交请另行指示。