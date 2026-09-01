# 上海卷内容与答案准确性复核报告 v3

- 框架初始化时间（UTC）: 2026-09-01T06:24:24+00:00
- 审计基线 commit: `d8ca16478afe24821f4d74de2f6c3a01c760354d`
- 文件: 97
- 题目: 2261
- 类型: {'subjective': 561, 'objective': 1700}

## 当前状态

v3 全量 LLM 批次重算已完成：37 个批次、2261/2261 题均已输出并通过 ID、顺序、JSON schema 校验。

- 原始 LLM 结论：正确 2190 / 错误候选 17 / 不确定 54
- 原始批次结果仅代表独立重算结论；17 个 `incorrect` 仍需二级对抗复核后，才能认定为真实内容错误。
- 本轮未修改任何 `content/` 文件，也未读取或复用 v2 的 LLM 校验结果。
- 转录自动比对已执行；扫描件视觉复核和错误候选二级复核尚未纳入本次批次聚合。

## 中间产物

- `tmp/audit/v3/snapshot.json`：不可变审计基线元数据
- `tmp/audit/v3/problems.jsonl`：当前内容解析结果
- `tmp/audit/v3/anomalies.jsonl`：静态候选（不是错误结论）
- `tmp/audit/v3/consistency.jsonl`：答案—解析字符串失配候选（不是错误结论）
- `tmp/audit/v3/batches_manifest.json`：不跨试卷的 LLM 批次清单
- `tmp/audit/v3/verify/`：预留给独立重算结果，禁止混入旧结果

## v3 自动聚合结果

- 校验文件: 37
- 已校验题目: 2261 / 2261
- 结论: correct=2190 / incorrect=17 / uncertain=54
- 本节为机器聚合结果；人工复核结论必须另行列出，不得覆盖原始 verdict。

### 按题型

- `objective:correct`: 1651
- `objective:incorrect`: 8
- `objective:uncertain`: 41
- `subjective:correct`: 539
- `subjective:incorrect`: 9
- `subjective:uncertain`: 13

### 按年份

- `1977:correct`: 18
- `1985:correct`: 44
- `1986:correct`: 70
- `1987:correct`: 29
- `1988:correct`: 28
- `1989:correct`: 28
- `1990:correct`: 27
- `1991:correct`: 26
- `1991:uncertain`: 1
- `1992:correct`: 24
- `1992:uncertain`: 2
- `1993:correct`: 25
- `1993:uncertain`: 1
- `1994:correct`: 77
- `1994:uncertain`: 1
- `1995:correct`: 59
- `1995:uncertain`: 1
- `1996:correct`: 52
- `1996:uncertain`: 6
- `1997:correct`: 54
- `1998:correct`: 43
- `1998:uncertain`: 1
- `1999:correct`: 43
- `1999:uncertain`: 1
- `2000:correct`: 64
- `2000:uncertain`: 2
- `2001:correct`: 63
- `2001:incorrect`: 1
- `2001:uncertain`: 2
- `2002:correct`: 60
- `2002:uncertain`: 6
- `2003:correct`: 65
- `2003:uncertain`: 1
- `2004:correct`: 59
- `2004:uncertain`: 7
- `2005:correct`: 66
- `2006:correct`: 66
- `2007:correct`: 63
- `2008:correct`: 64
- `2009:correct`: 66
- `2010:correct`: 68
- `2010:uncertain`: 1
- `2011:correct`: 67
- `2011:uncertain`: 2
- `2012:correct`: 68
- `2012:uncertain`: 1
- `2013:correct`: 77
- `2014:correct`: 75
- `2014:uncertain`: 3
- `2015:correct`: 80
- `2015:uncertain`: 2
- `2016:correct`: 80
- `2016:uncertain`: 2
- `2017:correct`: 41
- `2017:uncertain`: 1
- `2018:correct`: 42
- `2019:correct`: 40
- `2019:uncertain`: 1
- `2020:correct`: 37
- `2020:incorrect`: 5
- `2021:correct`: 36
- `2021:incorrect`: 4
- `2021:uncertain`: 2
- `2022:correct`: 40
- `2022:incorrect`: 2
- `2023:correct`: 37
- `2023:incorrect`: 2
- `2023:uncertain`: 3
- `2024:correct`: 38
- `2024:incorrect`: 2
- `2024:uncertain`: 2
- `2025:correct`: 40
- `2025:uncertain`: 2
- `2026:correct`: 41
- `2026:incorrect`: 1

## 最终归档说明

### 1. 归档范围与完整性

- 正式校验结果：`tmp/audit/v3/verify/verify_b00.jsonl` 至 `verify_b36.jsonl`。
- 共 37 个批次、2261 条记录；每批次已核对输入输出行数、ID 集合、ID 顺序、字段集合和 verdict 枚举。
- b33 正式结果为 `verify_b33.jsonl`，共 63 条：正确 58 / 错误候选 4 / 不确定 1。
- b33 重试副本已归档至 `tmp/audit/v3/archive/retry_b33.jsonl`，不在正式聚合目录，不参与统计。
- 机器聚合结果保存在 `tmp/audit/v3/aggregate.json`。

### 2. 17 个错误候选（需二级复核）

以下是独立 LLM 重算阶段的 `incorrect`，不是未经人工复核的最终修订清单：

| id | 初步判定 |
|---|---|
| `2001/shanghai_liberal#Q22` | 解析列举数列项时遗漏输入项 `x_0=49/65`；其余计算一致。 |
| `2020/shanghai#Q21` | 遗漏等比数列 `q=0` 的特例，参数范围不完整。 |
| `2020/shanghai_spring#Q4` | 复数解析的虚部符号错误，虽实部答案为 2。 |
| `2020/shanghai_spring#Q15` | 解析错误声称 `AB\ge2`，但弦长表达式不支持该断言。 |
| `2020/shanghai_spring#Q16` | 判别式条件写成严格 `>0`，应检查等号情形。 |
| `2020/shanghai_spring#Q21` | A 性质不等式方向写反，导致第(2)问结论错误。 |
| `2021/shanghai#Q16` | 解析无依据断言乘积为正，可构造反例。 |
| `2021/shanghai#Q18` | 使用 `\sin C<\sin B\Rightarrow C<B`，缺少必要角度范围论证。 |
| `2021/shanghai_spring#Q12` | 按题面量词 `\forall n\,\exists\varphi` 可逐 n 选取相位，题面与解析解释不一致。 |
| `2021/shanghai_spring#Q20` | 题面绝对值函数的定义域与解析擅自采用的受限定义域不一致。 |
| `2022/shanghai#Q12` | 将某充分条件误作任意函数下的必要条件；常函数构成反例。 |
| `2022/shanghai_spring#Q21` | 由“对每个 `t` 存在某个 `x`”错误推出全局单调性；存在分段函数反例。 |
| `2023/shanghai_spring#Q16` | 仅由部分和绝对值递减无法推出所称等差/等比结构。 |
| `2023/shanghai_spring#Q17` | 将斜边误作中线长度，导致第(1)问正切值错误。 |
| `2024/shanghai_spring#Q18` | 解析明确写出错误的 `PA=\sqrt2`，应为 `PA=\sqrt3`；最终表达式需单独核查。 |
| `2024/shanghai_spring#Q20` | 第(2)问区间下端点开闭仍需结合非退化三角形定义和原卷二次裁定。 |
| `2026/shanghai_spring#Q11` | 四焦点共圆与两椭圆交点条件疑似不相容，解析给出 `b^2=3` 缺乏充分依据。 |

### 3. 54 个不确定项

不确定项主要由以下原因产生：缺失图形或选择题位图、程序框图缺失、题面量词或变量不完整、单位/点名矛盾，以及解析只给近似值而题目要求精确值。逐题记录保存在各批次 `verify_bXX.jsonl` 中；本报告不把 `uncertain` 视为错误。

### 4. 归档边界

- v3 批次校验是独立重算初筛，不等同于最终人工裁定。
- 本报告和中间产物均不修改 `content/`；任何内容修订必须经过二级原卷复核和用户明确确认。
- 转录自动比对已完成；扫描件视觉复核、54 个不确定项和 17 个错误候选的二级复核仍是后续工作，不应在本报告中提前宣称已解决。

## 附录 A：54 个不确定题目 ID

`1991/shanghai#Q14`、`1992/shanghai#Q11`、`1992/shanghai#Q12`、`1993/shanghai#Q11`、`1994/shanghai#Q11`、`1995/shanghai_science#Q29`、`1996/shanghai_liberal#Q8`、`1996/shanghai_liberal#Q15`、`1996/shanghai_science#Q7`、`1996/shanghai_science#Q8`、`1996/shanghai_science#Q15`、`1996/shanghai_science#Q18`、`1998/shanghai_liberal#Q6`、`1999/shanghai_liberal#Q8`、`2000/shanghai_science#Q21`、`2000/shanghai_spring#Q22`、`2001/shanghai_liberal#Q12`、`2001/shanghai_science#Q12`、`2002/shanghai_liberal#Q13`、`2002/shanghai_liberal#Q15`、`2002/shanghai_liberal#Q16`、`2002/shanghai_science#Q13`、`2002/shanghai_science#Q15`、`2002/shanghai_science#Q16`、`2003/shanghai_spring#Q18`、`2004/shanghai_liberal#Q5`、`2004/shanghai_liberal#Q18`、`2004/shanghai_liberal#Q19`、`2004/shanghai_science#Q5`、`2004/shanghai_science#Q18`、`2004/shanghai_science#Q19`、`2004/shanghai_science#Q22`、`2010/shanghai_spring#Q12`、`2011/shanghai_spring#Q11`、`2011/shanghai_spring#Q13`、`2012/shanghai_science#Q10`、`2014/shanghai_science#Q19`、`2014/shanghai_spring#Q15`、`2014/shanghai_spring#Q30`、`2015/shanghai_spring#Q1`、`2015/shanghai_spring#Q11`、`2016/shanghai_science#Q16`、`2016/shanghai_spring#Q16`、`2017/shanghai_spring#Q14`、`2019/shanghai#Q11`、`2021/shanghai#Q14`、`2021/shanghai_spring#Q19`、`2023/shanghai#Q14`、`2023/shanghai#Q18`、`2023/shanghai_spring#Q14`、`2024/shanghai_spring#Q11`、`2024/shanghai_spring#Q16`、`2025/shanghai#Q11`、`2025/shanghai_spring#Q11`。

逐题的 derived/reason 保留在对应的 `tmp/audit/v3/verify/verify_bXX.jsonl` 中。
