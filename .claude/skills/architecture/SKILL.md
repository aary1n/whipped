Read this when: modifying repo structure, adding modules, resolving ownership questions.

## Module boundaries
- `domain/` — dataclasses only, no logic, no imports from other `whipped` modules
- `ingest/` — raw text → `Listing` dataclass; dataset CSV → list of `Listing`
- `features/` — `Listing` → `FeatureVector` (flat dict or dataclass)
- `pricing/` — `FeatureVector` → `PriceRange` with confidence
- `scoring/` — `FeatureVector` + `PriceRange` + asking price → `RipoffIndex`, `RiskScore`
- `scoring/explain.py` — all outputs → human explanation + counteroffer
- `app.py` — orchestrates the pipeline, no business logic

## Adding a new module
- Must fit one pipeline stage
- Import only from `domain/` and the stage directly upstream
- Add to ownership table in README
- Add tests in `tests/`

## Parallel safety
- Each team owns one directory; interfaces are the dataclasses in `domain/`
- Merge conflicts happen only in `domain/models.py` and `app.py` — keep both small

## Extension rules
- New data sources: add to `ingest/`, never `features/`
- New scores: add to `scoring/`, import `FeatureVector` + `PriceRange`
- New output formats: add to `app.py` or a new top-level entrypoint
