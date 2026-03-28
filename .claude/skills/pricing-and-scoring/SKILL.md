Read this when: working on fair price estimation, ripoff index, risk scoring, or explanation/counteroffer generation.

## Fair price range (`pricing/fair_range.py`)
- Input: `FeatureVector` + comparable listings from dataset
- Output: `PriceRange(low, mid, high, confidence)`
- Method: percentile-based on filtered comparables (start simple, refine later)
- Confidence: based on number and tightness of comparables

## Ripoff index (`scoring/ripoff.py`)
- Input: asking price + `PriceRange`
- Output: `RipoffIndex(score, label)` where score is 0-100
- 0 = great deal, 50 = fair, 100 = extreme ripoff
- Formula: position of asking price within range, clamped and scaled

## Risk score (`scoring/risk.py`)
- Input: `Listing` + `FeatureVector`
- Output: `RiskScore(score, factors)` where factors is list of strings
- Flags: high mileage for age, uncommon fuel/transmission combos, missing data, price outliers

## Explanation (`scoring/explain.py`)
- Input: all scores + `PriceRange` + `Listing`
- Output: human-readable summary + suggested counteroffer
- Counteroffer: derived from `PriceRange.mid`, adjusted by risk
- Keep explanations short (3-5 sentences)

## Testing
- `test_ripoff_index.py` — unit test ripoff score calculation with known inputs
- Test edge cases: no comparables, missing fields, extreme prices
