import json
from llm import call_gemini, strip_fences
from checks import run_code_checks


def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _load_rubric():
    with open("rubric.json", "r", encoding="utf-8") as f:
        return json.load(f)


def _llm_checks(rubric):
    return [c for c in rubric["checks"] if c["type"] == "llm"]


def evaluate_with_llm(lesson):
    """Evaluator agent: judges the judgment-based checkpoints. Strict, temperature 0."""
    rubric = _load_rubric()
    checks = _llm_checks(rubric)
    expected_ids = [c["id"] for c in checks]

    checkpoints_text = "\n".join(f'- id: {c["id"]} | question: {c["question"]}' for c in checks)
    prompt = (
        _read("prompts/evaluator.txt")
        .replace("<<CHECKPOINTS>>", checkpoints_text)
        .replace("<<FACTS>>", _read("grounding_facts.md"))
        .replace("<<LESSON>>", lesson)
    )

    parsed = None
    for attempt in range(2):  # one retry if the JSON is broken
        raw = call_gemini(prompt, temperature=0.0, json_mode=True)
        try:
            parsed = json.loads(strip_fences(raw))
            if "results" in parsed and isinstance(parsed["results"], list):
                break
        except json.JSONDecodeError:
            pass
        parsed = None
        print("  [evaluator] Invalid JSON from model, retrying...")

    if parsed is None:
        # Fail safe: if the evaluator cannot answer, treat everything as failed.
        return [
            {"id": cid, "passed": False, "reason": "Evaluator returned invalid output."}
            for cid in expected_ids
        ]

    by_id = {r.get("id"): r for r in parsed["results"] if isinstance(r, dict)}
    results = []
    for cid in expected_ids:
        r = by_id.get(cid)
        if r is None:
            results.append({"id": cid, "passed": False, "reason": "Evaluator skipped this check."})
        else:
            results.append(
                {
                    "id": cid,
                    "passed": bool(r.get("passed", False)),
                    "reason": str(r.get("reason", "")).strip(),
                }
            )
    return results


def evaluate_lesson(lesson):
    """Run code checks + LLM checks. Returns (all_passed, results)."""
    results = run_code_checks(lesson) + evaluate_with_llm(lesson)
    all_passed = all(r["passed"] for r in results)
    return all_passed, results


if __name__ == "__main__":
    # Test with a deliberately BAD lesson (wrong facts, no example, jargon)
    bad_lesson = """# What is RAG?
RAG retrains the large language model's weights every time a user asks a question, using vector embeddings and cosine similarity.

## Recap
- RAG is retraining.
"""
    passed, results = evaluate_lesson(bad_lesson)
    print("ALL PASSED:", passed)
    for r in results:
        mark = "PASS" if r["passed"] else "FAIL"
        print(f'[{mark}] {r["id"]}: {r["reason"]}')