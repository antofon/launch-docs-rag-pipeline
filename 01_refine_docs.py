# 01_refine_docs.py
import re, json
from pathlib import Path
import ollama
from langchain.prompts import ChatPromptTemplate

DATA = Path("data")
OUT = Path("artifacts"); OUT.mkdir(exist_ok=True, parents=True)

product_name = "Breakout Rooms"
version_or_date = "2025-09"
audience_hint = "Agents + AI ingestion"
raw_notes = (DATA/"release_notes.md").read_text()
policy_text = (DATA/"policy.md").read_text()
previous_article_path = DATA/"previous_article.md"
previous_article = previous_article_path.read_text() if previous_article_path.exists() else ""

system_msg = (
  "You are a doc specialist for a youth-focused learning platform. "
  "Convert raw product notes into (1) Markdown doc and (2) JSON for AI ingestion. "
  "No invention; use TODO when unknown. Grade level ~7–8. Youth-safety first. "
  "Output EXACTLY two fenced blocks: ===DOC_MARKDOWN=== ... ===END_DOC_MARKDOWN=== "
  "and ===DOC_JSON=== ... ===END_DOC_JSON===."
)

user_tmpl = """Product: {product_name}
Version/Date: {version_or_date}
Audience: {audience_hint}

Raw notes:
{raw_notes}

Policy (optional):
{policy_text}

Previous article (optional):
{previous_article}

Return TWO blocks:
===DOC_MARKDOWN===
# Title
## Overview
## Who this helps
## Key changes
## How it works (steps)
## Use cases
## Limitations & known caveats
## Policy notes & must-include lines
## FAQs (parents + teachers)
## Glossary
## Changes from last version
## Source excerpts
===END_DOC_MARKDOWN===
===DOC_JSON===
{{ "title": "", "version": "", "audience": [], "overview": "", "key_changes": [],
  "steps": [], "use_cases": [], "limitations": [], "policy_notes": [],
  "must_include_terms": [], "faqs": [], "glossary": [],
  "changes_from_previous": [], "llm_readiness": {{ "grade_level_estimate": 0,
  "ambiguous_phrases": [], "banned_or_sensitive_phrases": [], "terminology_map": [] }},
  "youth_safety": {{ "pii_requested": false, "cautions": [] }},
  "sources": [] }}
===END_DOC_JSON===
"""

prompt = ChatPromptTemplate.from_messages([
  ("system", system_msg),
  ("human", user_tmpl)
])

# Render messages
messages = prompt.format_messages(
    product_name=product_name,
    version_or_date=version_or_date,
    audience_hint=audience_hint,
    raw_notes=raw_notes,
    policy_text=policy_text,
    previous_article=previous_article
)

# Convert to Ollama format
ollama_messages = []
for m in messages:
    role = "user" if m.type == "human" else "system"
    ollama_messages.append({"role": role, "content": m.content})

# Call Ollama with Mistral
resp = ollama.chat(model="mistral", messages=ollama_messages, options={"temperature": 0.2})
text = resp.get("message", {}).get("content", "")

print("Raw Ollama output (truncated):\n", text[:500])  # debug preview

# Parse output
md = re.search(r"===DOC_MARKDOWN===\s*(.*?)\s*===END_DOC_MARKDOWN===", text, re.S)
js = re.search(r"===DOC_JSON===\s*(\{.*\})\s*===END_DOC_JSON===", text, re.S)

assert md and js, "Could not parse fenced blocks. Check Raw Ollama output above."

(OUT/"doc.md").write_text(md.group(1).strip())
json_obj = json.loads(js.group(1))
(OUT/"doc.json").write_text(json.dumps(json_obj, indent=2))

print("Wrote artifacts:")
print(" -", OUT/"doc.md")
print(" -", OUT/"doc.json")