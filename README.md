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

> 注意：数学字体（TeX Gyre Termes Math、STIX、Latin Modern Math、Asana Math）
> 在编译前由 `make` 调用 `tools/texlive-font-paths.sh` 生成 `tmp/math-fonts.tex`。
> 直接运行 `xelatex`（不走 `make`）时，`styles.tex` 会回退到按字体名加载，这在
> macOS 上会失败；请始终通过 `make pdf` 构建。
