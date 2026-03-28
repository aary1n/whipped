from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from whipped.app import evaluate
from whipped.config import MARKET_DB, SAMPLE_CSV
from whipped.domain.models import Listing, WhippedVerdict
from whipped.ingest.datasets import load_csv
from whipped.ingest.market_database import load_training_frame


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    app = WhippedWebApp()
    with make_server(host, port, app) as server:
        print(f"Serving whipped UI at http://{host}:{port}")
        server.serve_forever()


class WhippedWebApp:
    def __init__(self) -> None:
        self._sample_comparables = self._load_sample_comparables()

    def __call__(self, environ: dict[str, Any], start_response: Any) -> list[bytes]:
        method = environ.get("REQUEST_METHOD", "GET").upper()
        if method == "POST":
            size = int(environ.get("CONTENT_LENGTH") or 0)
            body = environ["wsgi.input"].read(size).decode("utf-8")
            form = {key: values[0] for key, values in parse_qs(body).items()}
            html = self._render_page(form)
        else:
            html = self._render_page({})

        payload = html.encode("utf-8")
        start_response("200 OK", [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(payload)))])
        return [payload]

    def _render_page(self, form: dict[str, str]) -> str:
        verdict: WhippedVerdict | None = None
        listing: Listing | None = None
        comparables: list[Listing] = self._sample_comparables

        if form:
            listing = _listing_from_form(form)
            comparables = self._find_comparables(listing)
            verdict = evaluate(listing, comparables)

        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Whipped Car Pricing Demo</title>
  <style>
    :root {{
      --bg: #f4efe7;
      --panel: #fffaf2;
      --ink: #1f2933;
      --muted: #52606d;
      --accent: #b44d12;
      --accent-2: #0f766e;
      --border: #e8dcc7;
      --warn: #9a3412;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(180, 77, 18, 0.12), transparent 24%),
        radial-gradient(circle at bottom right, rgba(15, 118, 110, 0.12), transparent 22%),
        var(--bg);
    }}
    .shell {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }}
    .hero {{
      margin-bottom: 24px;
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: clamp(2rem, 4vw, 3.6rem);
      line-height: 0.95;
      letter-spacing: -0.04em;
    }}
    .sub {{
      max-width: 800px;
      color: var(--muted);
      font-size: 1.05rem;
      line-height: 1.5;
    }}
    .grid {{
      display: grid;
      grid-template-columns: 1.05fr 1fr;
      gap: 20px;
      align-items: start;
    }}
    .panel {{
      background: color-mix(in srgb, var(--panel) 92%, white 8%);
      border: 1px solid var(--border);
      border-radius: 22px;
      padding: 22px;
      box-shadow: 0 10px 30px rgba(31, 41, 51, 0.06);
    }}
    h2 {{
      margin: 0 0 14px;
      font-size: 1.35rem;
    }}
    form {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }}
    label {{
      display: block;
      font-size: 0.9rem;
      color: var(--muted);
      margin-bottom: 6px;
    }}
    input, select {{
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 12px 14px;
      background: white;
      color: var(--ink);
      font: inherit;
    }}
    .full {{
      grid-column: 1 / -1;
    }}
    button {{
      border: 0;
      border-radius: 999px;
      padding: 14px 20px;
      background: var(--accent);
      color: white;
      font: inherit;
      cursor: pointer;
    }}
    .stat-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      margin: 16px 0 20px;
    }}
    .stat {{
      padding: 14px;
      background: white;
      border: 1px solid var(--border);
      border-radius: 16px;
    }}
    .k {{
      display: block;
      color: var(--muted);
      font-size: 0.82rem;
      margin-bottom: 4px;
    }}
    .v {{
      font-size: 1.15rem;
      font-weight: bold;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
      font-size: 0.95rem;
    }}
    th, td {{
      text-align: left;
      padding: 10px 8px;
      border-bottom: 1px solid var(--border);
    }}
    th {{
      color: var(--muted);
      font-weight: normal;
    }}
    .pill {{
      display: inline-block;
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(15, 118, 110, 0.12);
      color: var(--accent-2);
      font-size: 0.88rem;
      margin-right: 8px;
      margin-bottom: 8px;
    }}
    .warning {{
      color: var(--warn);
    }}
    .empty {{
      color: var(--muted);
      font-style: italic;
    }}
    @media (max-width: 860px) {{
      .grid {{
        grid-template-columns: 1fr;
      }}
      form {{
        grid-template-columns: 1fr;
      }}
      .stat-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <h1>Whipped<br>Car Price Checker</h1>
      <p class="sub">Enter listing details from Auto Trader or any used-car advert. The app shows the input data, a fair-price range, ripoff score, risk score, five-year ownership estimates, suggested counteroffer, and a simple investment-style recommendation.</p>
    </section>
    <section class="grid">
      <article class="panel">
        <h2>Input Data</h2>
        <form method="post">
          {self._render_form(form)}
          <div class="full"><button type="submit">Evaluate Listing</button></div>
        </form>
      </article>
      <article class="panel">
        <h2>Output</h2>
        {self._render_output(listing, verdict, comparables)}
      </article>
    </section>
  </main>
</body>
</html>"""

    def _render_form(self, form: dict[str, str]) -> str:
        def value(name: str, default: str = "") -> str:
            return escape(form.get(name, default))

        return f"""
        <div><label for="make">Make</label><input id="make" name="make" value="{value('make', 'ford')}" required></div>
        <div><label for="model">Model</label><input id="model" name="model" value="{value('model', 'fiesta')}" required></div>
        <div><label for="year">Year</label><input id="year" name="year" type="number" min="1990" max="2035" value="{value('year', '2020')}" required></div>
        <div><label for="price_gbp">Price (GBP)</label><input id="price_gbp" name="price_gbp" type="number" min="1" value="{value('price_gbp', '9300')}" required></div>
        <div><label for="mileage_miles">Mileage</label><input id="mileage_miles" name="mileage_miles" type="number" min="0" value="{value('mileage_miles', '33000')}"></div>
        <div><label for="engine_size_l">Engine Size (L)</label><input id="engine_size_l" name="engine_size_l" type="number" min="0" step="0.1" value="{value('engine_size_l', '1.0')}"></div>
        <div><label for="fuel_type">Fuel Type</label>{_select("fuel_type", value("fuel_type", "petrol"), ["petrol", "diesel", "hybrid", "electric"])}</div>
        <div><label for="transmission">Transmission</label>{_select("transmission", value("transmission", "manual"), ["manual", "automatic"])}</div>
        <div><label for="seller_type">Seller Type</label>{_select("seller_type", value("seller_type", "dealer"), ["dealer", "private"])}</div>
        <div><label for="body_type">Body Type</label><input id="body_type" name="body_type" value="{value('body_type', 'hatchback')}"></div>
        <div class="full"><label for="variant">Variant / Trim</label><input id="variant" name="variant" value="{value('variant', 'zetec')}"></div>
        """

    def _render_output(
        self,
        listing: Listing | None,
        verdict: WhippedVerdict | None,
        comparables: list[Listing],
    ) -> str:
        if not listing or not verdict:
            return '<p class="empty">Submit a listing to see the model output here.</p>'

        investment = _investment_view(verdict)
        flags = "".join(f'<span class="pill warning">{escape(flag)}</span>' for flag in verdict.risk.flags) or '<span class="empty">No risk flags</span>'
        comp_rows = "".join(
            f"<tr><td>{escape(c.make.title())}</td><td>{escape(c.model.title())}</td><td>{c.year}</td><td>{_fmt_int(c.mileage_miles)} mi</td><td>£{_fmt_int(c.price_gbp)}</td></tr>"
            for c in comparables[:8]
        )

        return f"""
        <div class="stat-grid">
          <div class="stat"><span class="k">Fair Range</span><span class="v">£{verdict.price_range.lower_gbp:,} to £{verdict.price_range.upper_gbp:,}</span></div>
          <div class="stat"><span class="k">Mid Price</span><span class="v">£{verdict.price_range.mid_gbp:,}</span></div>
          <div class="stat"><span class="k">Ripoff Score</span><span class="v">{verdict.ripoff.ripoff_index}/100 ({escape(verdict.ripoff.ripoff_band)})</span></div>
          <div class="stat"><span class="k">Risk Score</span><span class="v">{verdict.risk.risk_score}/100 ({escape(verdict.risk.risk_band)})</span></div>
          <div class="stat"><span class="k">Insurance (5y)</span><span class="v">{_fmt_currency(verdict.ownership.estimated_insurance_5y_gbp)}</span></div>
          <div class="stat"><span class="k">Depreciation (5y)</span><span class="v">{_fmt_currency(verdict.ownership.estimated_depreciation_5y_gbp)}</span></div>
          <div class="stat"><span class="k">Repairs (5y)</span><span class="v">{_fmt_currency(verdict.ownership.estimated_repairs_5y_gbp)}</span></div>
          <div class="stat"><span class="k">Repair Likelihood</span><span class="v">{verdict.ownership.repair_risk_pct}%</span></div>
          <div class="stat"><span class="k">Counteroffer</span><span class="v">{_fmt_currency(verdict.suggested_counteroffer_gbp)}</span></div>
          <div class="stat"><span class="k">Investment View</span><span class="v">{escape(investment)}</span></div>
        </div>
        <p><strong>Input summary:</strong> {listing.year} {escape(listing.make.title())} {escape(listing.model.title())}, {escape(listing.fuel_type or "unknown fuel")}, {escape(listing.transmission or "unknown transmission")}, {_fmt_int(listing.mileage_miles)} miles, asking {_fmt_currency(listing.price_gbp)}.</p>
        <p><strong>Model explanation:</strong> {escape(verdict.explanation)}</p>
        <div><strong>Risk flags:</strong><br>{flags}</div>
        <div style="margin-top:14px;"><strong>Longevity view:</strong><br>{"".join(f'<span class="pill">{escape(note)}</span>' for note in verdict.ownership.notes)}</div>
        <h2 style="margin-top:22px;">Comparable Data Used</h2>
        <p class="sub" style="font-size:0.95rem;">Showing the first {min(len(comparables), 8)} comparable listings used to price this car.</p>
        <table>
          <thead>
            <tr><th>Make</th><th>Model</th><th>Year</th><th>Mileage</th><th>Price</th></tr>
          </thead>
          <tbody>{comp_rows}</tbody>
        </table>
        """

    def _find_comparables(self, listing: Listing) -> list[Listing]:
        db_matches = _load_market_comparables(listing, MARKET_DB)
        if len(db_matches) >= 3:
            return db_matches

        filtered = [
            candidate
            for candidate in self._sample_comparables
            if candidate.make.lower() == listing.make.lower()
            and candidate.model.lower() == listing.model.lower()
        ]
        return filtered or self._sample_comparables

    def _load_sample_comparables(self) -> list[Listing]:
        if SAMPLE_CSV.exists():
            return load_csv(SAMPLE_CSV)
        return [
            Listing(make="ford", model="fiesta", year=2020, fuel_type="petrol", mileage_miles=30_000, transmission="manual", price_gbp=9_500),
            Listing(make="ford", model="fiesta", year=2020, fuel_type="petrol", mileage_miles=35_000, transmission="manual", price_gbp=9_200),
            Listing(make="ford", model="fiesta", year=2021, fuel_type="petrol", mileage_miles=22_000, transmission="manual", price_gbp=10_800),
        ]


def _load_market_comparables(listing: Listing, db_path: Path) -> list[Listing]:
    if not db_path.exists():
        return []

    frame = load_training_frame(db_path)
    matches = frame[
        (frame["make"].str.lower() == listing.make.lower())
        & (frame["model"].str.lower() == listing.model.lower())
    ].copy()
    if listing.fuel_type:
        matches = matches[
            matches["fuel_type"].fillna("").str.lower().isin([listing.fuel_type.lower(), ""])
        ]
    matches = matches.sort_values(by=["is_overpriced", "price_gap_pct", "price_gbp"], ascending=[True, True, True])

    comparables: list[Listing] = []
    for _, row in matches.head(20).iterrows():
        comparables.append(
            Listing(
                make=str(row["make"]),
                model=str(row["model"]),
                year=int(row["year"]),
                price_gbp=int(row["price_gbp"]),
                mileage_miles=_optional_int(row.get("mileage_miles")),
                fuel_type=_optional_str(row.get("fuel_type")),
                transmission=_optional_str(row.get("transmission")),
                engine_size_l=_optional_float(row.get("engine_size_l")),
                body_type=_optional_str(row.get("body_type")),
                seller_type=_optional_str(row.get("seller_type")),
            )
        )
    return comparables


def _listing_from_form(form: dict[str, str]) -> Listing:
    return Listing(
        make=form.get("make", "unknown").strip().lower(),
        model=form.get("model", "unknown").strip().lower(),
        year=int(form.get("year", "2020")),
        price_gbp=int(form.get("price_gbp", "0")),
        mileage_miles=_optional_int(form.get("mileage_miles")),
        fuel_type=_optional_str(form.get("fuel_type")),
        transmission=_optional_str(form.get("transmission")),
        engine_size_l=_optional_float(form.get("engine_size_l")),
        variant=_optional_str(form.get("variant")),
        body_type=_optional_str(form.get("body_type")),
        seller_type=_optional_str(form.get("seller_type")),
        source="localhost_ui",
    )


def _investment_view(verdict: WhippedVerdict) -> str:
    if verdict.ripoff.ripoff_index <= 35 and verdict.risk.risk_score <= 40:
        return "Potential buy"
    if verdict.ripoff.ripoff_index <= 60 and verdict.risk.risk_score <= 60:
        return "Watchlist"
    return "Avoid"


def _select(name: str, current: str, options: list[str]) -> str:
    rendered = []
    for option in options:
        selected = ' selected' if option == current else ""
        rendered.append(f'<select id="{name}" name="{name}">' if not rendered else "")
        rendered.append(f'<option value="{option}"{selected}>{option.title()}</option>')
    rendered.append("</select>")
    return "".join(rendered)


def _optional_int(value: object) -> int | None:
    if value in (None, "", "None"):
        return None
    return int(float(str(value)))


def _optional_float(value: object) -> float | None:
    if value in (None, "", "None"):
        return None
    return float(str(value))


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _fmt_int(value: int | None) -> str:
    return f"{value:,}" if value is not None else "n/a"


def _fmt_currency(value: int | None) -> str:
    return f"£{value:,}" if value is not None else "n/a"
