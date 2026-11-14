import re


def _clean_lines(lesson):
    """Remove Markdown symbols so we count only real sentences."""
    lines = []
    for line in lesson.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        line = re.sub(r"^[-*•]\s+", "", line)       # bullets
        line = re.sub(r"^\d+[.)]\s+", "", line)     # numbered steps
        line = line.replace("**", "").replace("*", "").replace("`", "")
        lines.append(line)
    return lines


def _sentences(lesson):
    sentences = []
    for line in _clean_lines(lesson):
        parts = re.split(r"(?<=[.!?])\s+", line)
        sentences.extend(p for p in parts if p.strip())
    return sentences


def word_count(lesson):
    return len(re.findall(r"\b\w+\b", lesson))


def check_avg_sentence_length(lesson, limit=18):
    sentences = _sentences(lesson)
    if not sentences:
        return False, "No sentences found."
    total = sum(len(re.findall(r"\b\w+\b", s)) for s in sentences)
    avg = total / len(sentences)
    if avg <= limit:
        return True, f"Average sentence length is {avg:.1f} words."
    return False, f"Average sentence length is {avg:.1f} words. Shorten sentences to {limit} words or fewer."


def check_length(lesson, low=500, high=1000):
    n = word_count(lesson)
    if low <= n <= high:
        return True, f"Lesson has {n} words."
    return False, f"Lesson has {n} words. It must be between {low} and {high} words."


def check_has_recap(lesson):
    pattern = r"^\s*#+\s*.*\b(recap|summary)\b"
    if re.search(pattern, lesson, flags=re.IGNORECASE | re.MULTILINE):
        return True, "Recap section found."
    return False, "No heading named 'Recap' or 'Summary' found. Add one at the end."


def run_code_checks(lesson):
    """Run all code-based checks. Returns the same format as the evaluator."""
    checks = [
        ("avg_sentence_length", check_avg_sentence_length),
        ("length_ok", check_length),
        ("has_recap", check_has_recap),
    ]
    results = []
    for check_id, fn in checks:
        passed, reason = fn(lesson)
        results.append({"id": check_id, "passed": passed, "reason": reason})
    return results


if __name__ == "__main__":
    # Quick self-test
    good = """# What is RAG?
RAG helps an AI answer using real documents. It is simple. """ + ("This is a short and clear sentence. " * 80) + """
## Recap
- RAG finds information first.
"""
    bad = "This is a very short lesson with no recap."
    print("GOOD LESSON:")
    for r in run_code_checks(good):
        print(r)
    print("\nBAD LESSON:")
    for r in run_code_checks(bad):
        print(r)