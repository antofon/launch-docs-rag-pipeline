# 04_eval_mistral.py
import re, json
from pathlib import Path
import ollama

ART = Path("artifacts")
doc_json = json.loads((ART/"doc.json").read_text())

# A few canned eval questions
eval_qs = [
    "What changed in this release?",
    "How do teachers benefit?",
    "List any limitations."
]

def eval_answer(q, ans):
    results = {}
    results["question"] = q
    results["answer"] = ans
    results["has_citation"] = bool(re.search(r"\[\d+\]", ans))
    results["mentions_todo"] = "TODO" in ans
    results["safe_language"] = not any(x in ans.lower() for x in ["password", "address", "ssn"])
    return results

all_results = []
for q in eval_qs:
    messages = [
        {"role": "system", "content": "Answer using safe language, cite from docs."},
        {"role": "user", "content": f"Q: {q}\nContext: {doc_json}"}
    ]
    resp = ollama.chat(model="mistral", messages=messages)
    ans = resp["message"]["content"]
    all_results.append(eval_answer(q, ans))

(ART/"eval_results.json").write_text(json.dumps(all_results, indent=2))
print("Wrote evaluation results to artifacts/eval_results.json")
