import argparse
import json
import os
import sys
from datetime import datetime

from generator import generate_lesson
from evaluator import evaluate_lesson
from checks import word_count
import memory as mem

DEFAULT_TOPIC = "Introduction to RAG (Retrieval-Augmented Generation)"

# A deliberate false statement + unexplained jargon, used for the demo
INJECTED_ERROR = (
    "RAG retrains the model's weights every time you ask a question, "
    "using vector embeddings and cosine similarity."
)


def inject_error(lesson):
    """Insert a false statement right after the first heading."""
    lines = lesson.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("#"):
            lines.insert(i + 1, "\n" + INJECTED_ERROR + "\n")
            return "\n".join(lines)
    return INJECTED_ERROR + "\n\n" + lesson


def compare_with_previous(prev, current):
    """Describe what changed between two attempts (used in the rejection log)."""
    prev_failed = {f["id"] for f in prev["failed_checks"]}
    curr_failed = {f["id"] for f in current["failed_checks"]}
    return {
        "fixed": sorted(prev_failed - curr_failed),
        "still_failing": sorted(prev_failed & curr_failed),
        "new_failures": sorted(curr_failed - prev_failed),
        "word_count_before": prev["word_count"],
        "word_count_after": current["word_count"],
    }


def run(topic, max_retries, inject):
    memory = mem.load_memory()
    mistakes = mem.build_mistakes_text(memory)
    max_attempts = max_retries + 1
    prefix = "demo_" if inject else ""

    os.makedirs("outputs/drafts", exist_ok=True)

    attempts = []
    lesson = None
    failures = None
    best = None  # (number_of_failed_checks, lesson)
    shipped_ok = False

    print(f"\nTopic: {topic}")
    print(f"Max attempts: {max_attempts} (1 original + {max_retries} retries)")
    print(f"Memory: {memory['runs']} earlier run(s)")
    print(f"Mistakes to avoid:\n{mistakes}\n")

    for attempt in range(1, max_attempts + 1):
        print(f"=== Attempt {attempt}/{max_attempts} ===")
        injected_now = False

        if attempt == 1:
            print("Generator: writing lesson...")
            lesson = generate_lesson(topic, mistakes)
            if inject:
                lesson = inject_error(lesson)
                injected_now = True
                print("!! DEMO MODE: a deliberate error was injected into this draft.")
        else:
            print("Generator: rewriting using failure feedback...")
            lesson = generate_lesson(topic, mistakes, previous_lesson=lesson, failures=failures)

        # Save every draft so before/after can be compared
        with open(f"outputs/drafts/{prefix}attempt_{attempt}.md", "w", encoding="utf-8") as f:
            f.write(lesson)

        print("Evaluator: checking rubric...")
        passed, results = evaluate_lesson(lesson)
        failed = [{"id": r["id"], "reason": r["reason"]} for r in results if not r["passed"]]

        entry = {
            "attempt": attempt,
            "error_injected_for_demo": injected_now,
            "word_count": word_count(lesson),
            "checks_passed": sum(1 for r in results if r["passed"]),
            "checks_total": len(results),
            "passed": passed,
            "failed_checks": failed,
        }
        if attempts:
            entry["changes_from_previous_attempt"] = compare_with_previous(attempts[-1], entry)
        attempts.append(entry)

        for r in results:
            mark = "PASS" if r["passed"] else "FAIL"
            print(f"  [{mark}] {r['id']}: {r['reason']}")

        if best is None or len(failed) <= best[0]:
            best = (len(failed), lesson)

        if passed:
            shipped_ok = True
            print(f"\nAll checks passed on attempt {attempt}. Shipping lesson.\n")
            break

        failures = failed
        if attempt < max_attempts:
            print(f"\nRejected ({len(failed)} failed). Sending reasons back to generator.\n")

    final_lesson = lesson if shipped_ok else best[1]
    status = "SHIPPED" if shipped_ok else "NEEDS_HUMAN_REVIEW"
    if not shipped_ok:
        print(f"\nMax attempts reached. Best attempt saved with status {status}.\n")

    # ---- write outputs ----
    lesson_path = f"outputs/{prefix}lesson.md"
    log_path = f"outputs/{prefix}rejection_log.json"

    with open(lesson_path, "w", encoding="utf-8") as f:
        if not shipped_ok:
            f.write("> WARNING: NEEDS_HUMAN_REVIEW. This lesson did not pass every check.\n\n")
        f.write(final_lesson)

    log = {
        "topic": topic,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "total_attempts": len(attempts),
        "demo_mode": inject,
        "attempts": attempts,
    }
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

    # ---- update memory ----
    if inject:
        print("Demo mode: memory NOT updated (injected failures are fake).")
    else:
        all_failures = [f for a in attempts for f in a["failed_checks"]]
        memory = mem.record_run(memory, all_failures)
        for tip in mem.get_evolution_suggestions(memory):
            print("SELF-EVOLUTION SUGGESTION:", tip)

    print(f"\nStatus: {status}")
    print(f"Lesson saved to: {lesson_path}")
    print(f"Rejection log saved to: {log_path}")
    print(f"Drafts saved in: outputs/drafts/")


def main():
    parser = argparse.ArgumentParser(description="Self-evaluating lesson generator")
    parser.add_argument("--topic", default=None,
                        help="Topic to teach. If omitted, you will be asked.")
    parser.add_argument("--max-retries", type=int, default=2, help="0, 1 or 2")
    parser.add_argument("--inject-error", action="store_true",
                        help="Demo: sabotage the first draft to show the evaluator catching it")
    args = parser.parse_args()

    if not 0 <= args.max_retries <= 2:
        parser.error("--max-retries must be 0, 1 or 2")

    topic = args.topic
    if topic is None:
        if sys.stdin.isatty():
            typed = input(f"Enter a topic (press Enter for '{DEFAULT_TOPIC}'): ").strip()
            topic = typed if typed else DEFAULT_TOPIC
        else:
            topic = DEFAULT_TOPIC

    if topic != DEFAULT_TOPIC:
        print("\nNOTE: grounding_facts.md only contains RAG facts. "
              "For other topics, the accuracy check is not reliable.")

    run(topic, args.max_retries, args.inject_error)


if __name__ == "__main__":
    main()