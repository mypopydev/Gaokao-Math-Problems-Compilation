# 高考数学题库

本代码库包含生成题目版和答案版 PDF 所需的 LaTeX 源文件、索引、题图、重绘图源和布局表。

代码库不提供成品 PDF，需按以下说明自行编译。

## 试题来源与致谢

本仓库中**大部分试题的源头来自 [deekur/gaokaomath](https://github.com/deekur/gaokaomath)**，在此向原仓库作者及贡献者表示感谢。

本项目在其基础上进行了重新整理、排版、校订、索引、题图处理、重绘以及答案整理等工作。对于来源于其他资料或由本项目进一步整理、补充的内容，其权利仍归相应权利人所有。

## 【特别提醒】许可与转载要求

除另有注明的第三方内容外，本仓库中由本项目整理、编写和制作的内容采用 **Creative Commons Attribution-ShareAlike 4.0 International（CC BY-SA 4.0）** 协议发布：

https://creativecommons.org/licenses/by-sa/4.0/

这意味着你可以复制、转载、分发、修改和再创作本仓库中的受许可内容，也可以将其用于商业用途，但必须遵守以下要求：

1. **署名（BY）**：转载、分发或改编时必须给予适当署名，保留本项目名称及仓库链接，并保留适用的原作者、贡献者和来源信息。
2. **注明修改**：如果对内容进行了修改、整理、删减或再创作，应明确说明内容已经被修改。
3. **相同方式共享（SA）**：如果发布基于本仓库内容制作的改编或衍生作品，必须以 **CC BY-SA 4.0** 或该协议允许的兼容许可继续发布，不得将衍生作品改为禁止他人继续共享和改编的封闭许可。
4. **保留上游来源**：对于来源于 [deekur/gaokaomath](https://github.com/deekur/gaokaomath) 的试题或整理成果，转载或改编时应同时保留该上游仓库的来源说明及链接。
5. **不得附加额外限制**：不得通过法律条款或技术措施，额外限制其他人在 CC BY-SA 4.0 已允许范围内使用这些内容。

简而言之：**可以转载、修改、再发布，甚至商业使用，但必须署名；改编后继续公开发布时，也必须允许后来者按照相同规则继续使用。**

完整许可说明见仓库根目录的 [`LICENSE`](./LICENSE) 文件及 Creative Commons 官方页面。

## 构建

环境需要：

- TeX Live / MacTeX（含 XeLaTeX、latexmk 及 `styles.tex` 引用的宏包）
- 中文与西文字体：
  - **Windows / 标准 TeX Live**：`SimSun`、`SimHei`、`KaiTi`、`Times New Roman`
  - **macOS**：无需安装 Windows 字体，构建脚本会自动回退到系统自带的
    `Songti SC`（宋体）、`STHeiti`（黑体）、`Times New Roman` 等；
    数学字体则由 `tools/texlive-font-paths.sh` 通过 `kpsewhich` 以绝对
    路径加载 TeX Live 自带字体，因此**必须使用 `make` 触发构建**。

```bash
make pdf
```

生成：

- `Compilation.pdf`
- `Compilation-answer.pdf`

清理构建产物：

```bash
make clean
```

### 只编译指定地区（试卷子集）

通过 `AREA` 变量可只编译某一地区的试卷与答案，例如只编译上海卷：

```bash
make pdf AREA=shanghai
```

生成：

- `Compilation-shanghai.pdf`
- `Compilation-answer-shanghai.pdf`

`AREA` 按子串匹配 `content/YYYY/<地区>.tex`，因此 `shanghai` 会同时收录
`shanghai`、`shanghai_spring`（春考）、`shanghai_science`、`shanghai_liberal`。
`AREA=all`（默认）编译全部内容；也可用 `beijing`、`tianjin`、`national_paper_1`
等只编译对应地区。`AREA` 改变后无需手动清理，构建脚本会重新生成过滤后的正文索引
`tmp/body.tex`。

> 清理时若指定了 `AREA`，`make clean AREA=shanghai` 只清理该子集产物；
> 不带 `AREA` 的 `make clean` 清理默认（全文）产物。

### 按课标主题分册编译

`make pdf-theme` 按《普通高中数学课程标准（2017 年版 2025 年修订）》的 5 个主题
重组题目，每册按年份倒序编排（同一年份下按原卷顺序）：

```bash
make pdf-theme                      # 默认 THEME_AREA=shanghai
make pdf-theme THEME_AREA=beijing   # 其它地区（需已有对应分类结果）
```

生成 5 册题目 + 5 册答案，共 10 个 PDF（上海卷 2261 题已全部分类，无未分类附录）：

| 分册 | 主题 | 上海卷题数 |
| --- | --- | --- |
| `Theme-1-预备知识.pdf` | 主题一 预备知识 | 431 |
| `Theme-2-函数.pdf` | 主题二 函数 | 775 |
| `Theme-3-几何与代数.pdf` | 主题三 几何与代数 | 830 |
| `Theme-4-概率与统计.pdf` | 主题四 概率与统计 | 206 |
| `Theme-5-数学建模活动与数学探究活动.pdf` | 主题五 数学建模活动与数学探究活动 | 19 |

对应的答案册为 `Theme-answer-<id>-<主题>.pdf`，内容为「题目 + 答案/解析」。

每册要点：

- **题号**沿用原试卷题号，题首灰色小字标注题源，形如 `（2022·上海·秋）`
  （不再重复题号）；卷别随年份不同可能为 `春`/`秋`/`文`/`理`/`秋文`/`秋理`；
- 当前 `△非课标` 标记仅用于“参数方程与极坐标”混合单元（上海卷共 38 题）：其中参数部分对应 B 类选修“模型”的参变数模型，极坐标尚未在课程标准 PDF 中核定；微积分、矩阵与变换属于课程标准选修内容，算法与程序框图属于必修函数应用中的程序框图要求，不使用该标记。
  所有扩展内容仍按内容相近的主题归册，并在题源后按实际范围标记；
- 分类结果来自 `docs/classify/classification.json`（由
  `python3 docs/classify/classify.py --all` 生成），正文由
  `tools/make-theme-body.py` 抽取重组，分册入口为 `Theme.tex` /
  `Theme-answer.tex`，专用宏在 `theme-styles.tex`。


> 注意：数学字体（TeX Gyre Termes Math、STIX、Latin Modern Math、Asana Math）
> 在编译前由 `make` 调用 `tools/texlive-font-paths.sh` 生成 `tmp/math-fonts.tex`。
> 直接运行 `xelatex`（不走 `make`）时，`styles.tex` 会回退到按字体名加载，这在
> macOS 上会失败；请始终通过 `make pdf` 构建。
