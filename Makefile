VENV=.venv
PY=$(VENV)/bin/python

init:
	python3 -m venv $(VENV)
	. $(VENV)/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

refine:
	$(PY) 01_refine_docs.py

index:
	$(PY) 02_build_index.py

ask:
	$(PY) 03_query.py

eval:
	$(PY) 04_eval.py
