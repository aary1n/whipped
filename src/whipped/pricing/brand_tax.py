from __future__ import annotations

import numpy as np

from whipped.domain.models import BrandTaxResult, Listing

_N_NEIGHBORS = 5


def compute(target: Listing, comparables: list[Listing]) -> BrandTaxResult | None:
    """Find DNA twins (same year, similar engine/mileage, different make) and compute brand tax."""
    if target.price_gbp is None or target.engine_size_l is None or target.mileage_miles is None:
        return None

    pool = [
        c for c in comparables
        if c.year == target.year
        and c.make.lower() != target.make.lower()
        and c.price_gbp is not None
        and c.engine_size_l is not None
        and c.mileage_miles is not None
    ]
    if not pool:
        return None

    pool_vecs = np.array([(c.engine_size_l, c.mileage_miles) for c in pool], dtype=float)
    target_arr = np.array([target.engine_size_l, target.mileage_miles], dtype=float)

    # Normalise each feature column to [0,1] range
    col_min = pool_vecs.min(axis=0)
    col_max = pool_vecs.max(axis=0)
    spread = np.where(col_max > col_min, col_max - col_min, 1.0)
    norm_pool = (pool_vecs - col_min) / spread
    norm_target = (target_arr - col_min) / spread

    dists = np.linalg.norm(norm_pool - norm_target, axis=1)
    k = min(_N_NEIGHBORS, len(pool))
    twin_idx = np.argsort(dists)[:k]

    twins = [pool[i] for i in twin_idx]
    avg_twin_price = int(round(sum(t.price_gbp for t in twins) / k))
    brand_tax = target.price_gbp - avg_twin_price

    # Recommendations: cluster members cheaper than target, sorted by price ascending
    recommendations = sorted(
        [
            {
                "make": c.make,
                "model": c.model,
                "year": c.year,
                "price_gbp": c.price_gbp,
                "brand_tax_gbp": c.price_gbp - avg_twin_price,
            }
            for c in twins
            if c.price_gbp < target.price_gbp
        ],
        key=lambda r: r["price_gbp"],
    )

    return BrandTaxResult(
        brand_tax_gbp=brand_tax,
        avg_twin_price_gbp=avg_twin_price,
        twin_count=k,
        twins=[
            {
                "make": t.make,
                "model": t.model,
                "year": t.year,
                "price_gbp": t.price_gbp,
                "brand_tax_gbp": t.price_gbp - avg_twin_price,
            }
            for t in twins
        ],
        is_good_deal=brand_tax < 0,
        recommendations=recommendations,
    )
