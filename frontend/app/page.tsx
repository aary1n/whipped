'use client';

import React, { useState } from 'react';
import { AlertTriangle, TrendingDown, Activity, ShieldAlert, Crosshair, Database, User, ChevronDown, DollarSign, Wrench, FileText } from 'lucide-react';

interface ListingInput {
  make: string;
  model: string;
  year: number;
  price_gbp: number;
  mileage_miles: number;
  engine_size_l: number;
  fuel_type: string;
  transmission: string;
}

interface ComparableListing {
  make: string;
  model: string;
  year: number;
  price_gbp: number;
  mileage_miles: number;
  engine_size_l: number;
  fuel_type: string;
  transmission: string;
}

interface DriverProfile {
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

interface Ownership {
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

interface VerdictOutput {
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
  comparables: ComparableListing[];
}

/* ── shared styles ─────────────────────────────────────────── */
const INPUT = "w-full bg-slate-950 border border-slate-800 rounded px-2 py-1.5 text-sm font-mono focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all";
const LABEL = "block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1";
const CELL = "bg-slate-900 p-4 flex flex-col justify-center";
const CELL_LABEL = "text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1";

export default function WhippedTerminal() {
  const [formState, setFormState] = useState<ListingInput>({
    make: 'Ford', model: 'Fiesta', year: 2020, price_gbp: 9300,
    mileage_miles: 33000, engine_size_l: 1.0, fuel_type: 'Petrol', transmission: 'Manual',
  });
  const [driverState, setDriverState] = useState<DriverProfile>({
    sex: '', age: '', years_licensed: '', no_claims_years: '',
    claims_last_5y: 0, annual_mileage: '', postcode_area: '', parking: '', cover_type: '',
  });
  const [driverOpen, setDriverOpen] = useState(false);
  const [verdict, setVerdict] = useState<VerdictOutput | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormState(prev => ({
      ...prev,
      [name]: ['make', 'model', 'fuel_type', 'transmission'].includes(name) ? value : Number(value),
    }));
  };
  const handleDriverChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setDriverState(prev => ({
      ...prev,
      [name]: ['sex', 'postcode_area', 'parking', 'cover_type'].includes(name) ? value : (value === '' ? '' : Number(value)),
    }));
  };

  const runAnalysis = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsExecuting(true);
    setError(null);
    try {
      const hasDriver = driverOpen && (driverState.age !== '' || driverState.years_licensed !== '' || driverState.postcode_area !== '');
      const res = await fetch('/api/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formState, driver: hasDriver ? driverState : undefined }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
        throw new Error(err.error ?? `HTTP ${res.status}`);
      }
      setVerdict(await res.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsExecuting(false);
    }
  };

  const scoreColor = (score: number) => score > 60 ? "text-rose-500" : score < 40 ? "text-emerald-500" : "text-amber-500";
  const fmt = (val: number) => new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', maximumFractionDigits: 0 }).format(val);
  const pct = (val: number) => `${Math.round(val * 100)}%`;
  const bandColor = (band: string) => {
    if (['bargain', 'good_deal', 'low'].includes(band)) return 'text-emerald-500';
    if (['fair', 'medium', 'within range'].includes(band)) return 'text-amber-500';
    return 'text-rose-500';
  };
  const recColor = (v: string) => v === 'Avoid' ? 'text-rose-500' : v === 'Watchlist' ? 'text-amber-500' : 'text-emerald-500';
  const recBorder = (v: string) => v === 'Avoid' ? 'rgb(244,63,94)' : v === 'Watchlist' ? 'rgb(245,158,11)' : 'rgb(16,185,129)';

  const v = verdict; // shorthand
  const own = v?.ownership;
  const hasOwn = own != null && own.insurance_annual_gbp !== 0;
  const fmtOwn = (val: number | undefined) => val != null && val !== 0 ? fmt(val) : '—';

  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 font-sans p-4 selection:bg-teal-900 selection:text-teal-100">
      <div className="max-w-[1600px] mx-auto h-[calc(100vh-2rem)] flex flex-col">

        {/* ── Header ── */}
        <header className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
          <div className="flex items-center gap-2 text-slate-100">
            <Activity size={20} className="text-teal-500" />
            <h1 className="font-bold tracking-widest text-sm uppercase">
              Whipped <span className="text-slate-500 font-normal">| Used Car Pricing</span>
            </h1>
          </div>
          <div className="text-xs font-mono text-slate-500 flex items-center gap-4">
            <span>SYS: <span className="text-emerald-500">ONLINE</span></span>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 lg:grid-rows-[minmax(0,1fr)] gap-6 flex-1 min-h-0">

          {/* ══════════════ LEFT: Input ══════════════ */}
          <div className="lg:col-span-4 xl:col-span-3 bg-slate-900 border border-slate-800 rounded-lg flex flex-col overflow-hidden shadow-2xl min-h-0">
            <div className="bg-slate-800/50 px-4 py-3 border-b border-slate-800 flex items-center gap-2">
              <Database size={14} className="text-teal-500" />
              <h2 className="text-xs font-bold tracking-widest text-slate-200 uppercase">Car Details</h2>
            </div>

            <form onSubmit={runAnalysis} className="flex flex-col flex-1 min-h-0">
              <div className="flex-1 overflow-y-auto min-h-0 p-4 flex flex-col gap-4">
                <div className="grid grid-cols-2 gap-3">
                  <div className="col-span-2"><label className={LABEL}>Make</label><input type="text" name="make" value={formState.make} onChange={handleInputChange} className={INPUT} /></div>
                  <div className="col-span-2"><label className={LABEL}>Model</label><input type="text" name="model" value={formState.model} onChange={handleInputChange} className={INPUT} /></div>
                  <div><label className={LABEL}>Year</label><input type="number" name="year" value={formState.year} onChange={handleInputChange} className={INPUT} /></div>
                  <div><label className={LABEL}>Ask Price (£)</label><input type="number" name="price_gbp" value={formState.price_gbp} onChange={handleInputChange} className={INPUT} /></div>
                  <div><label className={LABEL}>Mileage</label><input type="number" name="mileage_miles" value={formState.mileage_miles} onChange={handleInputChange} className={INPUT} /></div>
                  <div><label className={LABEL}>Engine (L)</label><input type="number" step="0.1" name="engine_size_l" value={formState.engine_size_l} onChange={handleInputChange} className={INPUT} /></div>
                  <div className="col-span-2"><label className={LABEL}>Fuel Type</label>
                    <select name="fuel_type" value={formState.fuel_type} onChange={handleInputChange} className={INPUT + " appearance-none"}>
                      <option>Petrol</option><option>Diesel</option><option>Hybrid</option><option>Electric</option>
                    </select>
                  </div>
                  <div className="col-span-2"><label className={LABEL}>Transmission</label>
                    <select name="transmission" value={formState.transmission} onChange={handleInputChange} className={INPUT + " appearance-none"}>
                      <option>Manual</option><option>Automatic</option><option>PDK</option><option>DSG</option>
                    </select>
                  </div>
                </div>

                {/* Driver Profile — collapsible */}
                <div className="border border-slate-800 rounded-lg overflow-hidden">
                  <button type="button" onClick={() => setDriverOpen(o => !o)} className="w-full flex items-center justify-between px-3 py-2.5 bg-slate-800/40 hover:bg-slate-800/70 transition-colors">
                    <div className="flex items-center gap-2">
                      <User size={13} className="text-teal-500" />
                      <span className="text-[10px] font-bold text-slate-300 uppercase tracking-widest">Driver Profile</span>
                      {!driverOpen && (driverState.age !== '' || driverState.postcode_area !== '') && <span className="text-[9px] text-teal-500 font-mono">● set</span>}
                    </div>
                    <ChevronDown size={14} className={`text-slate-500 transition-transform duration-200 ${driverOpen ? 'rotate-180' : ''}`} />
                  </button>
                  {driverOpen && (
                    <div className="p-3 grid grid-cols-2 gap-3 bg-slate-900/50">
                      <div className="col-span-2"><label className={LABEL}>Sex</label>
                        <select name="sex" value={driverState.sex} onChange={handleDriverChange} className={INPUT + " appearance-none"}>
                          <option value="">— unspecified —</option><option value="male">Male</option><option value="female">Female</option>
                        </select>
                      </div>
                      <div><label className={LABEL}>Age</label><input type="number" name="age" min={17} max={99} value={driverState.age} onChange={handleDriverChange} placeholder="—" className={INPUT} /></div>
                      <div><label className={LABEL}>Yrs Licensed</label><input type="number" name="years_licensed" min={0} value={driverState.years_licensed} onChange={handleDriverChange} placeholder="—" className={INPUT} /></div>
                      <div><label className={LABEL}>No-Claims Yrs</label><input type="number" name="no_claims_years" min={0} value={driverState.no_claims_years} onChange={handleDriverChange} placeholder="—" className={INPUT} /></div>
                      <div><label className={LABEL}>Claims (5y)</label><input type="number" name="claims_last_5y" min={0} max={10} value={driverState.claims_last_5y} onChange={handleDriverChange} className={INPUT} /></div>
                      <div><label className={LABEL}>Annual Miles</label><input type="number" name="annual_mileage" min={0} value={driverState.annual_mileage} onChange={handleDriverChange} placeholder="—" className={INPUT} /></div>
                      <div><label className={LABEL}>Postcode Area</label><input type="text" name="postcode_area" value={driverState.postcode_area} onChange={handleDriverChange} placeholder="e.g. SW1" maxLength={4} className={INPUT + " uppercase"} /></div>
                      <div className="col-span-2"><label className={LABEL}>Parking</label>
                        <select name="parking" value={driverState.parking} onChange={handleDriverChange} className={INPUT + " appearance-none"}>
                          <option value="">— unspecified —</option><option value="street">Street</option><option value="driveway">Driveway</option><option value="garage">Garage</option>
                        </select>
                      </div>
                      <div className="col-span-2"><label className={LABEL}>Cover Type</label>
                        <select name="cover_type" value={driverState.cover_type} onChange={handleDriverChange} className={INPUT + " appearance-none"}>
                          <option value="">— unspecified —</option><option value="third_party">Third Party</option><option value="third_party_fire_theft">TP Fire & Theft</option><option value="comprehensive">Comprehensive</option>
                        </select>
                      </div>
                    </div>
                  )}
                </div>

                {error && <div className="bg-rose-950/40 border border-rose-900/50 text-rose-400 px-3 py-2 rounded text-xs font-mono">{error}</div>}
              </div>{/* end scrollable area */}

              <div className="p-4 border-t border-slate-800/60">
                <button type="submit" disabled={isExecuting} className={`w-full flex items-center justify-center gap-2 py-3 rounded text-xs font-bold tracking-[0.2em] uppercase transition-all ${isExecuting ? 'bg-slate-800 text-slate-500' : 'bg-teal-900 hover:bg-teal-800 text-teal-400 border border-teal-800 hover:border-teal-600 shadow-[0_0_15px_rgba(20,184,166,0.15)]'}`}>
                  <Crosshair size={16} className={isExecuting ? 'animate-spin' : ''} />
                  {isExecuting ? 'Analysing...' : 'Analyse Listing'}
                </button>
              </div>
            </form>
          </div>

          {/* ══════════════ RIGHT: Output ══════════════ */}
          <div className="lg:col-span-8 xl:col-span-9 flex flex-col gap-5 overflow-y-auto min-h-0">
            {v ? (
              <>
                {/* ── 1. Deal Analysis ── */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-slate-800 rounded-lg overflow-hidden border border-slate-800">
                  <div className={CELL}>
                    <span className={CELL_LABEL}>Fair Range</span>
                    <span className="text-lg font-mono text-slate-300">{fmt(v.fair_range[0])} – {fmt(v.fair_range[1])}</span>
                  </div>
                  <div className={CELL}>
                    <span className={CELL_LABEL}>Market Midpoint</span>
                    <span className="text-lg font-mono text-slate-300">{fmt(v.mid_price)}</span>
                  </div>
                  <div className={CELL}>
                    <span className={CELL_LABEL}>Comparables</span>
                    <span className="text-lg font-mono text-slate-300">{v.comparable_count ?? 0} <span className="text-sm text-slate-600">found</span></span>
                    <span className={`text-[10px] font-mono mt-0.5 ${(v.confidence ?? 0) >= 0.7 ? 'text-emerald-500' : (v.confidence ?? 0) >= 0.4 ? 'text-amber-500' : 'text-rose-500'}`}>
                      {(v.confidence ?? 0) >= 0.7 ? 'high' : (v.confidence ?? 0) >= 0.4 ? 'medium' : 'low'} confidence · {v.strategy_used?.replace(/_/g, ' ') ?? ''}
                    </span>
                  </div>
                  <div className={CELL} style={{ borderTop: `2px solid ${recBorder(v.investment_view)}` }}>
                    <span className={CELL_LABEL}>Recommendation</span>
                    <span className={`text-lg font-bold uppercase tracking-wider ${recColor(v.investment_view)}`}>{v.investment_view}</span>
                    <span className="text-[10px] font-mono text-slate-600">{v.action_recommendation?.replace(/_/g, ' ') ?? ''}</span>
                  </div>
                </div>

                {/* ── 2. Pricing Verdict ── */}
                <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
                  {/* Scores */}
                  <div className="grid grid-cols-2 gap-px bg-slate-800 rounded-lg overflow-hidden border border-slate-800">
                    <div className={CELL}>
                      <span className={CELL_LABEL}>Overpricing</span>
                      <span className={`text-2xl font-mono ${scoreColor(v.ripoff_index)}`}>{v.ripoff_index}<span className="text-sm text-slate-600">/100</span></span>
                      <span className={`text-[10px] font-mono mt-0.5 ${bandColor(v.ripoff_band)}`}>{v.ripoff_band?.replace(/_/g, ' ') ?? ''} · {v.pricing_position ?? ''}</span>
                    </div>
                    <div className={CELL}>
                      <span className={CELL_LABEL}>Risk</span>
                      <span className={`text-2xl font-mono ${scoreColor(v.risk_score)}`}>{v.risk_score}<span className="text-sm text-slate-600">/100</span></span>
                      <span className={`text-[10px] font-mono mt-0.5 ${bandColor(v.risk_band)}`}>{v.risk_band}</span>
                    </div>
                    <div className={CELL}>
                      <span className={CELL_LABEL}>Suggested Offer</span>
                      <span className="text-xl font-mono text-teal-400">{v.counteroffer != null ? fmt(v.counteroffer) : '—'}</span>
                    </div>
                    <div className={CELL}>
                      <span className={CELL_LABEL}>Price vs Mid</span>
                      {(() => {
                        const delta = formState.price_gbp - v.mid_price;
                        return <span className={`text-xl font-mono ${delta > 0 ? 'text-rose-500' : 'text-emerald-500'}`}>{delta > 0 ? '+' : ''}{fmt(delta)}</span>;
                      })()}
                    </div>
                  </div>

                  {/* Explanation */}
                  <div className="xl:col-span-2 bg-slate-900 border border-slate-800 rounded-lg p-5 flex flex-col">
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                      <FileText size={14} className="text-teal-500" /> Verdict Summary
                    </h3>
                    <p className="text-sm font-mono text-slate-400 leading-relaxed flex-1">{v.explanation}</p>
                  </div>
                </div>

                {/* ── 3. 5-Year Ownership Forecast ── */}
                <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
                  <div className="bg-slate-800/50 px-5 py-3 border-b border-slate-800 flex items-center gap-2">
                    <Wrench size={14} className="text-teal-500" />
                    <h3 className="text-xs font-bold text-slate-200 uppercase tracking-widest">5-Year Ownership Forecast</h3>
                    {hasOwn && <span className={`ml-auto text-[10px] font-mono ${bandColor(own.ownership_band)}`}>{own.ownership_band} running costs</span>}
                  </div>
                  {hasOwn ? (
                    <>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-slate-800">
                        <div className={CELL}>
                          <span className={CELL_LABEL}>Insurance (annual)</span>
                          <span className="text-lg font-mono text-slate-300">{fmtOwn(own.insurance_annual_gbp)}</span>
                          <span className={`text-[10px] font-mono mt-0.5 ${bandColor(own.insurance_band)}`}>{own.insurance_band} band</span>
                        </div>
                        <div className={CELL}>
                          <span className={CELL_LABEL}>Insurance (5yr total)</span>
                          <span className="text-lg font-mono text-slate-300">{fmtOwn(own.insurance_5y_gbp)}</span>
                          <span className="text-[10px] font-mono text-slate-600 mt-0.5">inc. ~12% annual inflation</span>
                        </div>
                        <div className={CELL}>
                          <span className={CELL_LABEL}>Depreciation (5yr)</span>
                          <span className="text-lg font-mono text-slate-300">{fmtOwn(own.depreciation_5y_gbp)}</span>
                          <span className="text-[10px] font-mono text-slate-600 mt-0.5">{own.depreciation_5y_gbp && formState.price_gbp ? `~${Math.round(own.depreciation_5y_gbp / formState.price_gbp * 100)}% of purchase price` : ''}</span>
                        </div>
                        <div className={CELL}>
                          <span className={CELL_LABEL}>Repairs (5yr)</span>
                          <span className="text-lg font-mono text-slate-300">{fmtOwn(own.repairs_5y_gbp)}</span>
                          <span className="text-[10px] font-mono text-amber-600 mt-0.5">{own.repair_risk_pct}% repair likelihood</span>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-slate-800">
                        <div className={CELL}>
                          <span className={CELL_LABEL}>Annual Running Cost</span>
                          <span className="text-lg font-mono text-slate-300">{fmtOwn(own.annual_running_cost_gbp)}</span>
                          <span className="text-[10px] font-mono text-slate-600 mt-0.5">insurance + depreciation + repairs</span>
                        </div>
                        <div className={CELL}>
                          <span className={CELL_LABEL}>Total 5-Year Cost</span>
                          <span className="text-lg font-mono text-slate-100 font-bold">{fmt(v.total_cost_5y)}</span>
                          <span className="text-[10px] font-mono text-slate-600 mt-0.5">purchase + all running costs</span>
                        </div>
                        <div className={CELL}>
                          <span className={CELL_LABEL}>Cost on Top of Purchase</span>
                          <span className="text-lg font-mono text-rose-500">+{fmt(v.total_cost_5y - formState.price_gbp)}</span>
                          <span className="text-[10px] font-mono text-slate-600 mt-0.5">extra you'll spend over 5 years</span>
                        </div>
                        <div className={CELL}>
                          <span className={CELL_LABEL}>Ownership Band</span>
                          <span className={`text-lg font-mono font-bold ${bandColor(own.ownership_band)}`}>{own.ownership_band}</span>
                        </div>
                      </div>
                      {(own.notes ?? []).length > 0 && (
                        <div className="px-5 py-3 border-t border-slate-800 space-y-1">
                          {own.notes.map((note, i) => (
                            <p key={i} className="text-xs font-mono text-slate-500">{note}</p>
                          ))}
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="p-6 text-center text-sm font-mono text-slate-600">
                      Ownership data unavailable — try restarting the backend server.
                    </div>
                  )}
                </div>

                {/* ── 4. Risk Flags ── */}
                <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
                  <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                    <ShieldAlert size={14} className="text-rose-500" /> Risk Flags
                    <span className={`ml-auto text-[10px] font-mono ${bandColor(v.risk_band ?? '')}`}>{v.risk_band ?? ''} risk</span>
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {(v.risk_flags ?? []).length > 0 ? (v.risk_flags ?? []).map((flag, idx) => (
                      <div key={idx} className="bg-rose-950/30 border border-rose-900/50 text-rose-400 px-3 py-1.5 rounded flex items-center gap-2 text-xs font-mono">
                        <AlertTriangle size={12} />{flag}
                      </div>
                    )) : (
                      <span className="text-sm font-mono text-emerald-500">No risk flags identified.</span>
                    )}
                  </div>
                </div>

                {/* ── 5. Comparables Table ── */}
                <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden flex-1 flex flex-col min-h-[200px]">
                  <div className="bg-slate-800/50 px-5 py-3 border-b border-slate-800">
                    <h3 className="text-xs font-bold text-slate-200 uppercase tracking-widest">
                      Similar Listings · {(v.comparables ?? []).length} found
                    </h3>
                  </div>
                  <div className="overflow-auto flex-1">
                    {(v.comparables ?? []).length > 0 ? (
                      <table className="w-full text-left text-sm whitespace-nowrap">
                        <thead className="bg-slate-950/50 text-[10px] uppercase tracking-wider text-slate-500 font-bold sticky top-0">
                          <tr>
                            <th className="px-5 py-3">Car</th>
                            <th className="px-5 py-3">Year</th>
                            <th className="px-5 py-3">Mileage</th>
                            <th className="px-5 py-3">Engine / Trans</th>
                            <th className="px-5 py-3 text-right">Listed Price</th>
                            <th className="px-5 py-3 text-right">vs Asking</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800 font-mono text-slate-300">
                          {(v.comparables ?? []).map((comp, idx) => {
                            const spread = formState.price_gbp - comp.price_gbp;
                            return (
                              <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                                <td className="px-5 py-3">{comp.make} {comp.model}</td>
                                <td className="px-5 py-3">{comp.year}</td>
                                <td className="px-5 py-3">{comp.mileage_miles?.toLocaleString() ?? '—'} mi</td>
                                <td className="px-5 py-3">{comp.engine_size_l ?? '—'}L {(comp.fuel_type ?? '?').charAt(0).toUpperCase()} / {comp.transmission ?? '—'}</td>
                                <td className="px-5 py-3 text-right text-slate-100">{fmt(comp.price_gbp)}</td>
                                <td className={`px-5 py-3 text-right ${spread > 0 ? 'text-rose-500' : 'text-emerald-500'}`}>
                                  {spread > 0 ? '+' : ''}{fmt(spread)}
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    ) : (
                      <div className="p-8 text-center text-slate-600 font-mono text-sm">No comparable listings found for this vehicle.</div>
                    )}
                  </div>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center border border-dashed border-slate-800 rounded-lg text-slate-600 font-mono text-sm">
                {isExecuting ? 'Analysing...' : 'Enter a car above and click Analyse Listing'}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
