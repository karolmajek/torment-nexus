# The paper. `make` regenerates every table from results/runs, then builds the PDF.
#
# Tables first, always: a PDF built against a stale generated/ is a paper whose numbers
# disagree with the run records, and that is the one failure this directory exists to prevent.

PYTHON ?= python
TEX    ?= latexmk

GENERATED := $(wildcard generated/*.tex)
SOURCES   := main.tex refs.bib $(wildcard sections/*.tex)

.PHONY: all tables pdf clean distclean watch

all: pdf

tables:
	$(PYTHON) tools/gen_tables.py

pdf: tables
	$(TEX) -pdf -interaction=nonstopmode -halt-on-error main.tex

watch: tables
	$(TEX) -pdf -pvc main.tex

clean:
	$(TEX) -c
	rm -f main.bbl main.blg

distclean: clean
	$(TEX) -C
	rm -f generated/*.tex
