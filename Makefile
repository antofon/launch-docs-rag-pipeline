VENV=.venv
PY=$(VENV)/bin/python

init:
	python3 -m venv $(VENV)
	. $(VENV)/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

refine:
	$(PY) 01_refine_docs_mistral.py

index:
	$(PY) 02_build_index_mistral.py

ask:
	$(PY) 03_query_mistral.py

eval:
	$(PY) 04_eval_mistral.py
