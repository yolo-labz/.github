# yolo-labz brand — generated assets.
#
#   make model   render the gremlin turnaround + vector avatar from
#                model/params.json, then machine-check the result
#                (palette deltaE, PNG determinism, silhouette IoU).
#   make cards   render the same gremlin once and typeset the Open Graph,
#                Twitter and repository social cards from it; a repeat run
#                must reproduce every committed byte.
#   make check   the checker's own self-test (CIEDE2000 reference pairs).
#
# Requires: blender (>= 5), rsvg-convert, python3. No pip packages.

BLENDER ?= blender
PYTHON  ?= python3
THREADS ?= 4
BUILD   ?= build

.PHONY: model cards cards-verify check clean

model:
	rm -rf $(BUILD)
	$(BLENDER) -b --factory-startup -t $(THREADS) -P model/gremlin.py -- --out $(BUILD)
	$(PYTHON) model/svg/build_svg.py --out $(BUILD)
	$(PYTHON) model/check.py --build $(BUILD)

cards:
	$(PYTHON) model/cards.py --build $(BUILD)/cards --blender $(BLENDER) --threads $(THREADS)

# Cheap integrity gate: sizes + sha256 against cards.json, no blender needed.
cards-verify:
	$(PYTHON) model/cards.py --verify

check:
	$(PYTHON) model/check.py --self-test

# `clean` also drops the determinism baseline, which is what you want after an
# intentional change to model/params.json or model/gremlin.py.
clean:
	rm -rf $(BUILD) model/.determinism
