LATEXMK ?= latexmk
LATEXMK_FLAGS := -xelatex -synctex=1 -interaction=nonstopmode -halt-on-error \
	-e '$$xelatex = "xelatex -cnf-line=extra_mem_bot=10000000 %O %S"'
AUTO_IMAGE_LAYOUT ?= go run tools/typeset/auto_image_layout.go
IMAGE_LAYOUT_OUTPUT := tools/typeset/generated_image_layout.tex
IMAGE_LAYOUT_REPORT := tmp/auto_image_layout.tsv
IMAGE_LAYOUT_INPUTS := $(shell find content -type f -name '*.tex') \
	$(shell find img -type f \( -name '*.png' -o -name '*.jpg' -o -name '*.jpeg' \))
IMAGE_LAYOUT_TOOL_INPUTS := tools/typeset/auto_image_layout.go \
	tools/typeset/image_label_detector.py \
	tools/typeset/image_label_calibration.tex \
	styles.tex

# B1: TeX Live 数学字体的绝对路径，由构建脚本在编译前生成。
MATH_FONTS_OUTPUT := tmp/math-fonts.tex
TEXLIVE_FONT_PATHS := tools/texlive-font-paths.sh

# 试卷子集过滤：AREA=all 编译全部；AREA=shanghai 仅上海卷，以此类推
# （子串匹配，AREA=shanghai 覆盖 shanghai / shanghai_spring /
#  shanghai_science / shanghai_liberal）。
AREA ?= all
BODY_INDEX := tools/make-body-index.sh
BODY_OUTPUT := tmp/body.tex

# 子集编译时使用独立的 jobname，避免覆盖全文 PDF。
ifeq ($(AREA),all)
JOBNAME_MAIN :=
JOBNAME_ANSWER :=
else
JOBNAME_MAIN := -jobname=Compilation-$(AREA)
JOBNAME_ANSWER := -jobname=Compilation-answer-$(AREA)
endif

.PHONY: all pdf pdf-main pdf-answer image-layout math-fonts body-index clean

all: pdf

pdf: pdf-main pdf-answer

pdf-main: math-fonts image-layout body-index
	$(LATEXMK) $(LATEXMK_FLAGS) $(JOBNAME_MAIN) Compilation.tex

pdf-answer: math-fonts image-layout body-index
	$(LATEXMK) $(LATEXMK_FLAGS) $(JOBNAME_ANSWER) Compilation-answer.tex

math-fonts:
	$(TEXLIVE_FONT_PATHS) $(MATH_FONTS_OUTPUT)

# 生成过滤后的正文索引 tmp/body.tex（按 AREA 过滤 index/YYYY.tex）。
body-index:
	$(BODY_INDEX) $(AREA) $(BODY_OUTPUT)

# C1: 若已存在提交好的布局表则跳过重新生成（auto_image_layout 工具不在仓库内）。
image-layout:
	@if [ -f "$(IMAGE_LAYOUT_OUTPUT)" ]; then \
		echo "image-layout: $(IMAGE_LAYOUT_OUTPUT) 已存在，跳过重新生成"; \
	else \
		echo "image-layout: 生成 $(IMAGE_LAYOUT_OUTPUT) ..."; \
		$(AUTO_IMAGE_LAYOUT) \
			-root . \
			-output $(IMAGE_LAYOUT_OUTPUT) \
			-report $(IMAGE_LAYOUT_REPORT) \
			-crop-in-place; \
	fi

crop-ui:
	go run ./tools/crop/manualcrop -root . -addr 127.0.0.1:8766 -open

clean:
	$(LATEXMK) -C $(JOBNAME_MAIN) Compilation.tex
	$(LATEXMK) -C $(JOBNAME_ANSWER) Compilation-answer.tex
