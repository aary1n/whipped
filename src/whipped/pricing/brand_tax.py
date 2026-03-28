from __future__ import annotations

import numpy as np

from whipped.domain.models import BrandTaxResult, Listing

_N_NEIGHBORS = 5
<<<<<<< HEAD
_MAX_YEAR_DELTA = 1
_RECOMMENDATION_POOL = 12


def compute(target: Listing, comparables: list[Listing]) -> BrandTaxResult | None:
    """Find DNA twins (similar year/spec, different make) and compute brand tax."""
=======


def compute(target: Listing, comparables: list[Listing]) -> BrandTaxResult | None:
    """Find DNA twins (same year, similar engine/mileage, different make) and compute brand tax."""
>>>>>>> origin/tam/clustering
    if target.price_gbp is None or target.engine_size_l is None or target.mileage_miles is None:
        return None

    pool = [
        c for c in comparables
<<<<<<< HEAD
        if abs(c.year - target.year) <= _MAX_YEAR_DELTA
=======
        if c.year == target.year
>>>>>>> origin/tam/clustering
        and c.make.lower() != target.make.lower()
        and c.price_gbp is not None
        and c.engine_size_l is not None
        and c.mileage_miles is not None
    ]
    if not pool:
        return None

<<<<<<< HEAD
    pool_vecs = np.array(
        [
            (
                c.engine_size_l,
                c.mileage_miles,
                abs(c.year - target.year),
                0.0 if (c.fuel_type or "").lower() == (target.fuel_type or "").lower() else 1.0,
                0.0 if (c.transmission or "").lower() == (target.transmission or "").lower() else 1.0,
                0.0 if (c.body_type or "").lower() == (target.body_type or "").lower() else 1.0,
            )
            for c in pool
        ],
        dtype=float,
    )
    target_arr = np.array([target.engine_size_l, target.mileage_miles, 0.0, 0.0, 0.0, 0.0], dtype=float)
=======
    pool_vecs = np.array([(c.engine_size_l, c.mileage_miles) for c in pool], dtype=float)
    target_arr = np.array([target.engine_size_l, target.mileage_miles], dtype=float)
>>>>>>> origin/tam/clustering

    # Normalise each feature column to [0,1] range
    col_min = pool_vecs.min(axis=0)
    col_max = pool_vecs.max(axis=0)
    spread = np.where(col_max > col_min, col_max - col_min, 1.0)
    norm_pool = (pool_vecs - col_min) / spread
    norm_target = (target_arr - col_min) / spread

    dists = np.linalg.norm(norm_pool - norm_target, axis=1)
<<<<<<< HEAD
    ordering = np.argsort(dists)
    k = min(_N_NEIGHBORS, len(pool))
    twin_idx = ordering[:k]
=======
    k = min(_N_NEIGHBORS, len(pool))
    twin_idx = np.argsort(dists)[:k]
>>>>>>> origin/tam/clustering

    twins = [pool[i] for i in twin_idx]
    avg_twin_price = int(round(sum(t.price_gbp for t in twins) / k))
    brand_tax = target.price_gbp - avg_twin_price

<<<<<<< HEAD
    recommendation_idx = ordering[: min(_RECOMMENDATION_POOL, len(pool))]
    recommendation_candidates = [pool[i] for i in recommendation_idx]

    # Recommendations: nearby cluster members cheaper than target, sorted by price ascending
=======
    # Recommendations: cluster members cheaper than target, sorted by price ascending
>>>>>>> origin/tam/clustering
    recommendations = sorted(
        [
            {
                "make": c.make,
                "model": c.model,
                "year": c.year,
                "price_gbp": c.price_gbp,
                "brand_tax_gbp": c.price_gbp - avg_twin_price,
            }
<<<<<<< HEAD
            for c in recommendation_candidates
            if c.price_gbp < target.price_gbp
        ],
        key=lambda r: (r["price_gbp"], abs(r["year"] - target.year)),
=======
            for c in twins
            if c.price_gbp < target.price_gbp
        ],
        key=lambda r: r["price_gbp"],
>>>>>>> origin/tam/clustering
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
