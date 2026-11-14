# Self-Evaluating Lesson Content Generator

An agentic system that generates a beginner lesson, judges it against a pass/fail rubric,
and regenerates until it is good enough to ship. 

## Architecture

Topic -> Memory ("mistakes to avoid") -> Generator Agent -> Code Checker + Evaluator Agent
-> Controller (pass? ship : retry with reasons, max 2 retries) -> lesson + rejection log -> Memory update


## Components

| File | Role |
|---|---|
| main.py | Controller: loop, retry cap, rejection log, outputs |
| generator.py | Generator agent: writes and rewrites the lesson |
| evaluator.py | Evaluator agent: strict pass/fail judge (temperature 0, JSON output) |
| checks.py | Deterministic checks: sentence length, word count, recap section |
| memory.py | Persistent memory of failures, injected into future prompts |
| rubric.json | 11 hard pass/fail checkpoints (8 LLM, 3 code) |
| grounding_facts.md | Verified facts used to judge accuracy |
| llm.py | Gemini client with retry and model fallback |

## Design decisions and trade-offs

- **Separate writer and judge.** One model grading its own output in the same call is too lenient.
  The evaluator has its own prompt and runs at temperature 0.
- **Hard pass/fail, no scores.** Gives an unambiguous ship/retry decision and specific feedback.
- **Code checks plus LLM checks.** Measurable things (length, sentence length) are checked in code
  because it is cheaper and more reliable than asking an LLM.
- **Grounding facts.** Accuracy means "consistent with verified facts", not "the model thinks it is right".
- **Guaranteed termination.** Max 3 attempts. If all fail, the best draft ships flagged NEEDS_HUMAN_REVIEW.
- **Fail-safe evaluator.** If the evaluator returns invalid JSON twice, all checks count as failed.
- **Plain Python instead of a framework.** The loop is small and well defined, so I chose full control
  and easy debugging. It maps onto LangGraph (nodes: generate, evaluate, update memory;
  conditional edge: retry).

## Self-evolving memory

After each run, every failed check and its reason is saved to memory.json. Before the next run,
the top recurring failures are added to the generator prompt as "mistakes to avoid".
If a check fails 3 or more times across runs, the system prints a suggestion to strengthen the
prompt or review the rubric. Demo runs do not write to memory, so fake errors cannot pollute learning.

## Setup

1. Python 3.10+
2. `python -m venv venv` then activate it
3. `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add your Gemini API key

## Run

- `python main.py` : asks for a topic (Enter = RAG)
- `python main.py --topic "..."` : custom topic
- `python main.py --inject-error` : demo; plants a false statement to show the evaluator catching it
- `python main.py --max-retries 1` : limit retries (0, 1 or 2)

## Outputs

- outputs/lesson.md : the passing lesson
- outputs/rejection_log.json : what failed, why, what changed on retry
- outputs/drafts/ : every attempt saved for comparison
- outputs/demo_* : files from the error-injection demo

## Known limitations

- grounding_facts.md covers RAG only; other topics need their own facts file.
- The LLM evaluator can miss subtle problems. It is a strong filter, not a replacement for human review.
- The free Gemini tier has a small daily request limit, handled with retry and model fallback.

## Next steps

- Auto-fetch grounding facts from trusted sources (RAG applied to this system)
- Auto-apply rubric and prompt improvements after repeated failures
- Human review queue for NEEDS_HUMAN_REVIEW lessons
- Streamlit UI
