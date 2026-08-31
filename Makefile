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

.PHONY: all pdf pdf-main pdf-answer image-layout math-fonts clean

all: pdf

pdf: pdf-main pdf-answer

pdf-main: math-fonts image-layout
	$(LATEXMK) $(LATEXMK_FLAGS) Compilation.tex

pdf-answer: math-fonts image-layout
	$(LATEXMK) $(LATEXMK_FLAGS) Compilation-answer.tex

# B1: 定位 TeX Live 数学字体并生成 tmp/math-fonts.tex（按绝对路径加载，
# 对 macOS 友好；Windows / Linux 的 TeX Live 同样可用 kpsewhich 找到）。
math-fonts:
	$(TEXLIVE_FONT_PATHS) $(MATH_FONTS_OUTPUT)

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
	$(LATEXMK) -C Compilation.tex
	$(LATEXMK) -C Compilation-answer.tex
