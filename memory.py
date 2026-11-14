import json
import os

MEMORY_FILE = "memory.json"


def load_memory():
    """Load memory from disk. Creates a fresh memory if the file is missing or broken."""
    default = {"runs": 0, "failure_counts": {}, "last_reasons": {}}
    if not os.path.exists(MEMORY_FILE):
        return default
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return default
    for key, value in default.items():
        data.setdefault(key, value)
    return data


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)


def build_mistakes_text(memory, top_n=3):
    """Turn past failures into a short 'mistakes to avoid' note for the generator."""
    counts = memory.get("failure_counts", {})
    if not counts:
        return "None yet. This is the first run."
    top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    lines = []
    for check_id, count in top:
        reason = memory.get("last_reasons", {}).get(check_id, "")
        lines.append(f"- '{check_id}' failed {count} time(s) before. Last problem: {reason}")
    return "\n".join(lines)


def record_run(memory, failed_checks):
    """
    Update memory after a run.
    failed_checks = list of dicts like {"id": "has_example", "reason": "No example given"}
    Include every failure from every attempt in the run.
    """
    memory["runs"] += 1
    for item in failed_checks:
        cid = item["id"]
        memory["failure_counts"][cid] = memory["failure_counts"].get(cid, 0) + 1
        memory["last_reasons"][cid] = item["reason"]
    save_memory(memory)
    return memory


def get_evolution_suggestions(memory, threshold=3):
    """Self-evolving part: flag checks that keep failing so the prompt or rubric can be improved."""
    suggestions = []
    for cid, count in memory.get("failure_counts", {}).items():
        if count >= threshold:
            suggestions.append(
                f"Check '{cid}' has failed {count} times. "
                f"Strengthen the generator prompt for it, or review whether the rubric is too strict."
            )
    return suggestions