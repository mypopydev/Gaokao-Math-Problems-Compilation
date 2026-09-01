# 上海卷 v3 二级复核最终报告

## 1. 审计范围

- 基线 commit：`d8ca16478afe24821f4d74de2f6c3a01c760354d`
- 上海卷文件：97
- 题目：2261
- 一级 LLM 初筛：正确 2190 / 错误候选 17 / 不确定 54
- 本报告只归档二级复核，不修改任何 `content/` 文件。

## 2. 二级复核结果

对一级的 17 个 `incorrect` 和 54 个 `uncertain`（共 71 条）逐条进行原题、当前 LaTeX、上游 PDF 及可用图片复核。

| 二级结论 | 数量 |
|---|---:|
| `verified_correct` | 35 |
| `verified_solution_error` | 13 |
| `verified_answer_error` | 1 |
| `verified_transcription_error` | 9 |
| `ambiguous_problem` | 13 |
| **合计** | **71** |

逐条证据保存在：

- `tmp/audit/v3/review/errors/e01.jsonl` 至 `e04.jsonl`
- `tmp/audit/v3/review/uncertain/u01.jsonl` 至 `u06.jsonl`

每条记录字段为：`id`、`second_verdict`、`derived`、`evidence`、`action`。

## 3. 最终确认的内容问题

### 3.1 答案/结论错误（1）

- `2023/shanghai_spring#Q16`
  - 题设只约束 `k>2022` 的部分和尾部，无法推出前缀等差及尾部等比结构。
  - 已构造满足题设但否定选项 C 的数列反例。
  - 定性：`verified_answer_error`。

### 3.2 解析错误（12 个错误候选；另有 1 个不确定项，见下文）

- `2001/shanghai_liberal#Q22`：列举数列项时漏掉输入项 `x_0=49/65`。
- `2020/shanghai#Q21`：遗漏等比数列 `q=0` 特例。
- `2020/shanghai_spring#Q4`：复数虚部符号错误，但所求实部仍为 2。
- `2020/shanghai_spring#Q15`：错误声称 `AB≥2`，实际弦长满足相反的边界关系；最终轨迹答案仍可成立。
- `2020/shanghai_spring#Q16`：判别式写成 `Δ>0`，应检查 `Δ=0`。
- `2020/shanghai_spring#Q21`：A 性质不等式方向写反。
- `2021/shanghai#Q16`：无依据断言乘积为正；答案结论需按正确推导重写。
- `2021/shanghai#Q18`：使用 `sin C<sin B ⇒ C<B`，缺少角度范围论证；最终周长值可由合法角度关系得到。
- `2021/shanghai_spring#Q20`：题面绝对值函数定义域为 `R`，解析擅自使用受限定义域和不存在的双根情形。
- `2022/shanghai_spring#Q21`：由“对每个 t 存在某个 x”错误推出全局单调性；分段反例满足题设但非全局递增。
- `2024/shanghai_spring#Q18`：解析写出 `PA=√2`，正确应为 `PA=√3`；最终二面角表达式碰巧仍正确。
- `2024/shanghai_spring#Q20`：第(2)问区间下端点应结合非退化三角形条件重新表述；第(3)问坐标错误已由一级复核发现。

### 3.3 转录错误（5）

- `2023/shanghai_spring#Q17`：上游写“AE 是直线 ME 到平面 PAB 的距离”，当前内容误录为“AC”；答案 `6/5` 与 `2` 本身正确。
- `2000/shanghai_science#Q21`：当前内容指数写成固定 `2`，历史版本和题意应为含 `n` 的表达式。
- `2023/shanghai#Q18`：当前题面漏录原卷中的小问，解析反而引入未出现在题面的条件。
- `2024/shanghai_spring#Q16`：当前题面漏录选项所引用的陈述（1）、（2）。
- `2017/shanghai_spring#Q14`：原卷选项 C 为“充要”，当前内容误录为“充分”。

### 3.4 题面歧义或不适定（17）

- `2022/shanghai#Q12`：对固定任意函数时，解析给出的统一区间是充分条件但未必必要；题面量词不足。
- `1992/shanghai#Q12`：原卷未限制参数 a，log_a x 与 x^a 的单调性随参数变化，选项无法唯一确定。
- `2002/shanghai_liberal#Q16`、`2002/shanghai_science#Q16`：图表显示温度最高月与用电量最高月存在并列，选项 A/C 均可能成立，题面/解析与官方选项不一致。
- `2026/shanghai_spring#Q11`：四焦点共圆与两椭圆四个实交点条件不相容，原题/参考解析存在逻辑问题。
- `2021/shanghai_spring#Q12`：字面量词 `∀n∃φ` 使每个正 θ 都可逐项选相位，与官方答案解释不一致。
- `2004/shanghai_liberal#Q18`：米与平方厘米单位矛盾，且图示方向影响结果。
- `2004/shanghai_liberal#Q19`：小问使用未定义的 B。
- `2004/shanghai_science#Q18`：单位与图示方向存在矛盾。
- `2004/shanghai_science#Q19`：小问使用未定义的 B。
- `2004/shanghai_science#Q22`：题目前提与椭圆条件矛盾。
- `2024/shanghai_spring#Q11`：仅给出圆过 E、F 和 AD 上一点，未明确圆形通道需在草坪内/与 AD 相切，圆不唯一。
- `2015/shanghai_spring#Q1`：原卷本身保留“若集合则”的病句，虽可推出补集，但题面不完整。
- `2015/shanghai_spring#Q11`：未给出组成三位数的数字集合，答案不唯一。
- `1996/shanghai_liberal#Q15`：题目写“直线 OA”，导致内外分点两种解。
- `1996/shanghai_science#Q15`：题目写“直线 OA”，同样允许外部点解，文字条件不足以唯一确定答案。
- `2019/shanghai#Q11`：`n=1,2` 时不存在实数点，题面自然数范围与解析使用范围不一致。

## 4. 一级不确定项中已确认正确（35）

这些题目原先仅因图形、选项或数据缺失而标记 uncertain；二级复核通过本地图片或上游 PDF 后确认答案/解析正确：

- `1991/shanghai#Q14`
- `1992/shanghai#Q11`
- `1993/shanghai#Q11`
- `1994/shanghai#Q11`
- `1995/shanghai_science#Q29`
- `1996/shanghai_liberal#Q8`
- `1996/shanghai_science#Q7`
- `1996/shanghai_science#Q8`
- `1996/shanghai_science#Q18`
- `1998/shanghai_liberal#Q6`
- `1999/shanghai_liberal#Q8`
- `2000/shanghai_spring#Q22`
- `2001/shanghai_liberal#Q12`
- `2001/shanghai_science#Q12`
- `2002/shanghai_liberal#Q13`
- `2002/shanghai_liberal#Q15`
- `2002/shanghai_science#Q13`
- `2002/shanghai_science#Q15`
- `2003/shanghai_spring#Q18`
- `2004/shanghai_liberal#Q5`
- `2004/shanghai_science#Q5`
- `2010/shanghai_spring#Q12`
- `2011/shanghai_spring#Q11`
- `2011/shanghai_spring#Q13`
- `2012/shanghai_science#Q10`
- `2014/shanghai_science#Q19`
- `2014/shanghai_spring#Q15`
- `2014/shanghai_spring#Q30`
- `2016/shanghai_science#Q16`
- `2016/shanghai_spring#Q16`
- `2021/shanghai#Q14`
- `2023/shanghai#Q14`
- `2023/shanghai_spring#Q14`
- `2025/shanghai#Q11`
- `2025/shanghai_spring#Q11`

## 5. 已执行修订（用户授权）

已根据二级复核结论修订 11 个内容文件中的确认错误；未处理 `ambiguous_problem` 和 `verified_correct` 项：

- 答案/结论：`2023/shanghai_spring#Q16` 改为严格题面下“原选项无正确答案”，并补充反例。
- 解析：修正 `2001/shanghai_liberal#Q22`、`2020/shanghai#Q21`、`2020/shanghai_spring#Q4/#Q15/#Q16/#Q21`、`2021/shanghai#Q16/#Q18`、`2021/shanghai_spring#Q20`、`2022/shanghai_spring#Q21`、`2024/shanghai_spring#Q18/#Q20`。
- 转录：修正 `2000/shanghai_science#Q21` 指数及完整推导、`2023/shanghai#Q18` 漏录小问、`2024/shanghai_spring#Q16` 漏录陈述、`2017/shanghai_spring#Q14` 选项文字、`2023/shanghai_spring#Q17` 的 `AC→AE`。

复核后重新解析仍为 97 文件、2261 题（客观 1700 / 主观 561）；`make AREA=shanghai pdf` 题目册和答案册构建成功，`git diff --check` 通过。

## 6. 处理边界

- 本轮修订仅处理二级确认的答案、解析和转录错误，未处理 `ambiguous_problem`。
- `ambiguous_problem` 项仍需权威勘误或用户另行决定，不能据此擅自改写题面。
- 当前修改尚未提交或推送；提交前应再次审阅完整 diff。
- 建议下一步按优先级处理：
  1. `verified_answer_error`；
  2. `verified_transcription_error`；
  3. 明确的 `verified_solution_error`；
  4. `ambiguous_problem` 单独保留说明或回查官方版本。
