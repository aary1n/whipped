// Shared types, styles, and helpers used across pages

export interface ListingInput {
  make: string;
  model: string;
  year: number;
  price_gbp: number;
  mileage_miles: number;
  engine_size_l: number;
  fuel_type: string;
  transmission: string;
}

export interface ComparableListing {
  make: string;
  model: string;
  year: number;
  price_gbp: number;
  mileage_miles: number;
  engine_size_l: number;
  fuel_type: string;
  transmission: string;
}

export interface DriverProfile {
  sex: string;
  age: number | '';
  years_licensed: number | '';
  no_claims_years: number | '';
  claims_last_5y: number;
  annual_mileage: number | '';
  postcode_area: string;
  parking: string;
  cover_type: string;
}

export interface Ownership {
  insurance_annual_gbp: number;
  insurance_5y_gbp: number;
  depreciation_5y_gbp: number;
  repairs_5y_gbp: number;
  repair_risk_pct: number;
  annual_running_cost_gbp: number;
  ownership_band: string;
  insurance_band: string;
  notes: string[];
}

export interface BrandTaxEntry {
  make: string;
  model: string;
  year: number;
  price_gbp: number;
  brand_tax_gbp: number;
}

export interface BrandTax {
  brand_tax_gbp: number;
  avg_twin_price_gbp: number;
  twin_count: number;
  is_good_deal: boolean;
  twins: BrandTaxEntry[];
  recommendations: BrandTaxEntry[];
}

export interface VerdictOutput {
  total_cost_5y: number;
  fair_range: [number, number];
  mid_price: number;
  confidence: number;
  comparable_count: number;
  strategy_used: string;
  ripoff_index: number;
  ripoff_band: string;
  pricing_position: string;
  risk_score: number;
  risk_band: string;
  risk_notes: string;
  counteroffer: number | null;
  action_recommendation: string;
  investment_view: "Potential buy" | "Watchlist" | "Avoid";
  risk_flags: string[];
  ownership: Ownership;
  explanation: string;
  brand_tax: BrandTax | null;
  comparables: ComparableListing[];
}

// ── Shared CSS classes ──
export const INPUT = "w-full bg-slate-950 border border-slate-800 rounded px-2 py-1.5 text-sm font-mono focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all";
export const LABEL = "block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1";
export const CELL = "bg-slate-900 p-4 flex flex-col justify-center";
export const CELL_LABEL = "text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1";

// ── Helpers ──
export const fmt = (val: number) =>
  new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', maximumFractionDigits: 0 }).format(val);

export const scoreColor = (score: number) =>
  score > 60 ? "text-rose-500" : score < 40 ? "text-emerald-500" : "text-amber-500";

export const bandColor = (band: string) => {
  if (['bargain', 'good_deal', 'low'].includes(band)) return 'text-emerald-500';
  if (['fair', 'medium', 'within range'].includes(band)) return 'text-amber-500';
  return 'text-rose-500';
};

export const recColor = (v: string) =>
  v === 'Avoid' ? 'text-rose-500' : v === 'Watchlist' ? 'text-amber-500' : 'text-emerald-500';

export const recBorder = (v: string) =>
  v === 'Avoid' ? 'rgb(244,63,94)' : v === 'Watchlist' ? 'rgb(245,158,11)' : 'rgb(16,185,129)';

export const DEFAULT_LISTING: ListingInput = {
  make: 'Ford', model: 'Fiesta', year: 2020, price_gbp: 9300,
  mileage_miles: 33000, engine_size_l: 1.0, fuel_type: 'Petrol', transmission: 'Manual',
};

export const DEFAULT_DRIVER: DriverProfile = {
  sex: 'male', age: 30, years_licensed: 10, no_claims_years: 5,
  claims_last_5y: 0, annual_mileage: 10000, postcode_area: 'SW', parking: 'driveway', cover_type: 'comprehensive',
};
