# whipped

UK used-car pricing intelligence engine. Paste a listing, get a fair price band, ripoff index, hidden-risk score, and suggested counteroffer.

## Quickstart

```bash
pip install -e ".[dev]"
python scripts/prepare_sample_data.py
python scripts/run_demo.py
```

## Flow

```
listing text → parsed listing → feature extraction → fair price range
                                                   → risk score
                                                   → ripoff index
                                                   → explanation + counteroffer
```

## Layout

| Path | Owner | Purpose |
|------|-------|---------|
| `src/whipped/domain/` | shared | Data models |
| `src/whipped/ingest/` | data team | Parsing & dataset loading |
| `src/whipped/features/` | data team | Feature extraction |
| `src/whipped/pricing/` | pricing team | Fair price range estimation |
| `src/whipped/scoring/` | scoring team | Ripoff index, risk score, explanations |
| `src/whipped/app.py` | app team | Demo entrypoint |
