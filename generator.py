from llm import call_gemini, strip_fences


def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def generate_lesson(topic, mistakes_text, previous_lesson=None, failures=None):
    """
    First attempt: previous_lesson and failures are None.
    Retry: pass the rejected lesson and the list of failed checks so the model fixes them.
    failures = list of {"id": ..., "reason": ...}
    """
    prompt = _read("prompts/generator.txt")
    facts = _read("grounding_facts.md")

    if previous_lesson and failures:
        fail_lines = "\n".join(f"- {f['id']}: {f['reason']}" for f in failures)
        retry_section = (
            "YOUR PREVIOUS DRAFT WAS REJECTED.\n"
            "Fix ALL of these problems, and keep everything that already worked:\n"
            f"{fail_lines}\n\n"
            "PREVIOUS DRAFT:\n"
            f"{previous_lesson}"
        )
    else:
        retry_section = ""

    prompt = (
        prompt.replace("<<TOPIC>>", topic)
        .replace("<<FACTS>>", facts)
        .replace("<<MISTAKES>>", mistakes_text)
        .replace("<<RETRY_SECTION>>", retry_section)
    )

    lesson = call_gemini(prompt, temperature=0.7)
    return strip_fences(lesson)


if __name__ == "__main__":
    from checks import word_count

    text = generate_lesson("Introduction to RAG (Retrieval-Augmented Generation)", "None yet.")
    print(text)
    print("\n---\nWord count:", word_count(text))