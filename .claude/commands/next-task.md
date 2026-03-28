Start a focused work session.

Steps:
- Read `CLAUDE.md` for repo rules and skill routing
- Identify which skill file covers the task scope — read only that one
- Read only the files you will directly modify
- Do not read the full repo or all skills
- Check `domain/models.py` if your work touches data flowing between modules
- After changes: run `pytest` and fix any failures
- Keep modules under 150 lines
- Do not add dependencies without justification

If task is ambiguous, pick the smallest useful increment and do it.
