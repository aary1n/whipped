# whipped — Claude rules

## Architecture
- Pipeline: listing text → `ingest/` → `features/` → `pricing/` → `scoring/` → explanation
- Domain models in `domain/models.py` — shared, import from here
- Each module has one job; no cross-layer imports except domain

## File ownership
- `ingest/`, `features/` → data team
- `pricing/` → pricing team
- `scoring/` → scoring team
- `app.py` → app team

## Coding rules
- Typed Python, dataclasses for models
- No class hierarchies unless forced
- Keep modules < 150 lines
- Minimal docstrings (only non-obvious)
- Tests mirror `src/` structure

## Dependencies
- stdlib + pandas only; justify any addition
- No web framework until demo needs it

## Skill routing
- Repo structure / ownership / extension → `.claude/skills/architecture/SKILL.md`
- Datasets / ingestion / sample data → `.claude/skills/data-ingestion/SKILL.md`
- Pricing / scoring / explanation logic → `.claude/skills/pricing-and-scoring/SKILL.md`

## Token efficiency
- Read only CLAUDE.md + one skill + touched files per task
- Use `/next-task` command to start work sessions
