'use client';

import React, { useState } from 'react';
import { AlertTriangle, TrendingDown, Activity, ShieldAlert, Crosshair, Database, User, ChevronDown } from 'lucide-react';

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
  age: number | '';
  years_licensed: number | '';
  no_claims_years: number | '';
  claims_last_5y: number;
  annual_mileage: number | '';
  postcode_area: string;
  parking: string;
  cover_type: string;
}

interface VerdictOutput {
  total_cost_5y: number;
  fair_range: [number, number];
  mid_price: number;
  ripoff_index: number;
  risk_score: number;
  counteroffer: number | null;
  action_recommendation: string;
  investment_view: "Potential buy" | "Watchlist" | "Avoid";
  risk_flags: string[];
  comparables: ComparableListing[];
}

export default function WhippedTerminal() {
  const [formState, setFormState] = useState<ListingInput>({
    make: 'Ford',
    model: 'Fiesta',
    year: 2020,
    price_gbp: 9300,
    mileage_miles: 33000,
    engine_size_l: 1.0,
    fuel_type: 'Petrol',
    transmission: 'Manual',
  });

  const [driverState, setDriverState] = useState<DriverProfile>({
    age: '',
    years_licensed: '',
    no_claims_years: '',
    claims_last_5y: 0,
    annual_mileage: '',
    postcode_area: '',
    parking: '',
    cover_type: '',
  });
  const [driverOpen, setDriverOpen] = useState(false);

  const [verdict, setVerdict] = useState<VerdictOutput | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormState(prev => ({
      ...prev,
      [name]: name === 'make' || name === 'model' || name === 'fuel_type' || name === 'transmission'
        ? value
        : Number(value),
    }));
  };

  const handleDriverChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    const strFields = ['postcode_area', 'parking', 'cover_type'];
    setDriverState(prev => ({
      ...prev,
      [name]: strFields.includes(name) ? value : (value === '' ? '' : Number(value)),
    }));
  };

  const executeArbitrage = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsExecuting(true);
    setError(null);
    try {
      const hasDriver = driverOpen && (
        driverState.age !== '' || driverState.years_licensed !== '' || driverState.postcode_area !== ''
      );
      const payload = {
        ...formState,
        driver: hasDriver ? driverState : undefined,
      };
      const res = await fetch('/api/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
        throw new Error(err.error ?? `HTTP ${res.status}`);
      }
      const data: VerdictOutput = await res.json();
      setVerdict(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsExecuting(false);
    }
  };

  const getScoreColor = (score: number, inverse: boolean = false) => {
    const isBad = inverse ? score < 40 : score > 60;
    const isGood = inverse ? score > 70 : score < 40;
    if (isBad) return "text-rose-500";
    if (isGood) return "text-emerald-500";
    return "text-amber-500";
  };

  const formatGBP = (val: number) =>
    new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', maximumFractionDigits: 0 }).format(val);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 font-sans p-4 selection:bg-teal-900 selection:text-teal-100">
      <div className="max-w-[1600px] mx-auto h-[calc(100vh-2rem)] flex flex-col">

        {/* Header */}
        <header className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
          <div className="flex items-center gap-2 text-slate-100">
            <Activity size={20} className="text-teal-500" />
            <h1 className="font-bold tracking-widest text-sm uppercase">
              Whipped <span className="text-slate-500 font-normal">| Quant Arb Engine v2.1.0</span>
            </h1>
          </div>
          <div className="text-xs font-mono text-slate-500 flex items-center gap-4">
            <span>SYS: <span className="text-emerald-500">ONLINE</span></span>
            <span>LATENCY: 12ms</span>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-0">

          {/* LEFT: Input */}
          <div className="lg:col-span-4 xl:col-span-3 bg-slate-900 border border-slate-800 rounded-lg flex flex-col overflow-hidden shadow-2xl">
            <div className="bg-slate-800/50 px-4 py-3 border-b border-slate-800 flex items-center gap-2">
              <Database size={14} className="text-teal-500" />
              <h2 className="text-xs font-bold tracking-widest text-slate-200 uppercase">Asset Parameters</h2>
            </div>

            <form onSubmit={executeArbitrage} className="p-4 flex flex-col flex-1 gap-4 overflow-y-auto">
              <div className="grid grid-cols-2 gap-3">
                <div className="col-span-2">
                  <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Make</label>
                  <input type="text" name="make" value={formState.make} onChange={handleInputChange} className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1.5 text-sm font-mono focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all" />
                </div>
                <div className="col-span-2">
                  <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Model</label>
                  <input type="text" name="model" value={formState.model} onChange={handleInputChange} className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1.5 text-sm font-mono focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all" />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Year</label>
                  <input type="number" name="year" value={formState.year} onChange={handleInputChange} className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1.5 text-sm font-mono focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all" />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Ask Price (£)</label>
                  <input type="number" name="price_gbp" value={formState.price_gbp} onChange={handleInputChange} className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1.5 text-sm font-mono focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all" />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Mileage</label>
                  <input type="number" name="mileage_miles" value={formState.mileage_miles} onChange={handleInputChange} className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1.5 text-sm font-mono focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all" />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Engine (L)</label>
                  <input type="number" step="0.1" name="engine_size_l" value={formState.engine_size_l} onChange={handleInputChange} className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1.5 text-sm font-mono focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all" />
                </div>
                <div className="col-span-2">
                  <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Fuel Type</label>
                  <select name="fuel_type" value={formState.fuel_type} onChange={handleInputChange} className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1.5 text-sm font-mono focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all appearance-none">
                    <option>Petrol</option>
                    <option>Diesel</option>
                    <option>Hybrid</option>
                    <option>Electric</option>
                  </select>
                </div>
                <div className="col-span-2">
                  <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Transmission</label>
                  <select name="transmission" value={formState.transmission} onChange={handleInputChange} className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1.5 text-sm font-mono focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all appearance-none">
                    <option>Manual</option>
                    <option>Automatic</option>
                    <option>PDK</option>
                    <option>DSG</option>
                  </select>
                </div>
              </div>

              {/* Driver Profile — collapsible */}
              <div className="border border-slate-800 rounded-lg overflow-hidden">
                <button
                  type="button"
                  onClick={() => setDriverOpen(o => !o)}
                  className="w-full flex items-center justify-between px-3 py-2.5 bg-slate-800/40 hover:bg-slate-800/70 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <User size={13} className="text-teal-500" />
                    <span className="text-[10px] font-bold text-slate-300 uppercase tracking-widest">Driver Profile</span>
                    {!driverOpen && (driverState.age !== '' || driverState.postcode_area !== '') && (
                      <span className="text-[9px] text-teal-500 font-mono">● set</span>
                    )}
                  </div>
                  <ChevronDown
                    size={14}
                    className={`text-slate-500 transition-transform duration-200 ${driverOpen ? 'rotate-180' : ''}`}
                  />
                </button>

                {driverOpen && (
                  <div className="p-3 grid grid-cols-2 gap-3 bg-slate-900/50">
                    <div>
                      <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Age</label>
                      <input type="number" name="age" min={17} max={99} value={driverState.age} onChange={handleDriverChange} placeholder="—" className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1.5 text-sm font-mono focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all" />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Yrs Licensed</label>
                      <input type="number" name="years_licensed" min={0} value={driverState.years_licensed} onChange={handleDriverChange} placeholder="—" className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1.5 text-sm font-mono focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all" />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">No-Claims Yrs</label>
                      <input type="number" name="no_claims_years" min={0} value={driverState.no_claims_years} onChange={handleDriverChange} placeholder="—" className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1.5 text-sm font-mono focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all" />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Claims (5y)</label>
                      <input type="number" name="claims_last_5y" min={0} max={10} value={driverState.claims_last_5y} onChange={handleDriverChange} className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1.5 text-sm font-mono focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all" />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Annual Miles</label>
                      <input type="number" name="annual_mileage" min={0} value={driverState.annual_mileage} onChange={handleDriverChange} placeholder="—" className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1.5 text-sm font-mono focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all" />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Postcode Area</label>
                      <input type="text" name="postcode_area" value={driverState.postcode_area} onChange={handleDriverChange} placeholder="e.g. SW1" maxLength={4} className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1.5 text-sm font-mono focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all uppercase" />
                    </div>
                    <div className="col-span-2">
                      <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Parking</label>
                      <select name="parking" value={driverState.parking} onChange={handleDriverChange} className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1.5 text-sm font-mono focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all appearance-none">
                        <option value="">— unspecified —</option>
                        <option value="street">Street</option>
                        <option value="driveway">Driveway</option>
                        <option value="garage">Garage</option>
                      </select>
                    </div>
                    <div className="col-span-2">
                      <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Cover Type</label>
                      <select name="cover_type" value={driverState.cover_type} onChange={handleDriverChange} className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1.5 text-sm font-mono focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none transition-all appearance-none">
                        <option value="">— unspecified —</option>
                        <option value="third_party">Third Party</option>
                        <option value="third_party_fire_theft">TP Fire & Theft</option>
                        <option value="comprehensive">Comprehensive</option>
                      </select>
                    </div>
                  </div>
                )}
              </div>

              {error && (
                <div className="bg-rose-950/40 border border-rose-900/50 text-rose-400 px-3 py-2 rounded text-xs font-mono">
                  {error}
                </div>
              )}

              <div className="mt-auto pt-4">
                <button
                  type="submit"
                  disabled={isExecuting}
                  className={`w-full flex items-center justify-center gap-2 py-3 rounded text-xs font-bold tracking-[0.2em] uppercase transition-all ${isExecuting ? 'bg-slate-800 text-slate-500' : 'bg-teal-900 hover:bg-teal-800 text-teal-400 border border-teal-800 hover:border-teal-600 shadow-[0_0_15px_rgba(20,184,166,0.15)]'}`}
                >
                  <Crosshair size={16} className={isExecuting ? 'animate-spin' : ''} />
                  {isExecuting ? 'Computing...' : 'Execute Arbitrage'}
                </button>
              </div>
            </form>
          </div>

          {/* RIGHT: Output */}
          <div className="lg:col-span-8 xl:col-span-9 flex flex-col gap-6 overflow-y-auto min-h-0">

            {verdict ? (
              <>
                {/* Hero + grid */}
                <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                  <div className="xl:col-span-1 bg-slate-900 border border-slate-800 rounded-lg p-6 flex flex-col justify-center relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-teal-900/10 rounded-bl-full -mr-8 -mt-8 transition-transform group-hover:scale-110" />
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2 flex items-center gap-2">
                      <TrendingDown size={14} /> Total 5Y TCO
                    </h3>
                    <div className="text-4xl lg:text-5xl font-mono text-slate-100 tracking-tight">
                      {formatGBP(verdict.total_cost_5y)}
                    </div>
                    <div className="mt-4 text-xs font-mono text-slate-500">
                      Delta vs Asset Price:{' '}
                      <span className="text-rose-500">
                        +{formatGBP(verdict.total_cost_5y - formState.price_gbp)}
                      </span>
                    </div>
                  </div>

                  <div className="xl:col-span-2 grid grid-cols-2 md:grid-cols-3 gap-px bg-slate-800 rounded-lg overflow-hidden border border-slate-800">
                    <div className="bg-slate-900 p-4 flex flex-col justify-center">
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Fair Range</span>
                      <span className="text-lg font-mono text-slate-300">
                        {formatGBP(verdict.fair_range[0])} – {formatGBP(verdict.fair_range[1])}
                      </span>
                    </div>
                    <div className="bg-slate-900 p-4 flex flex-col justify-center">
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Mid Price</span>
                      <span className="text-lg font-mono text-slate-300">{formatGBP(verdict.mid_price)}</span>
                    </div>
                    <div className="bg-slate-900 p-4 flex flex-col justify-center">
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Ripoff Score</span>
                      <span className={`text-2xl font-mono ${getScoreColor(verdict.ripoff_index)}`}>
                        {verdict.ripoff_index}<span className="text-sm text-slate-600">/100</span>
                      </span>
                    </div>
                    <div className="bg-slate-900 p-4 flex flex-col justify-center">
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Risk Score</span>
                      <span className={`text-2xl font-mono ${getScoreColor(verdict.risk_score)}`}>
                        {verdict.risk_score}<span className="text-sm text-slate-600">/100</span>
                      </span>
                    </div>
                    <div className="bg-slate-900 p-4 flex flex-col justify-center">
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Max Bid (Counter)</span>
                      <span className="text-xl font-mono text-teal-400">
                        {verdict.counteroffer != null ? formatGBP(verdict.counteroffer) : '—'}
                      </span>
                    </div>
                    <div
                      className="bg-slate-900 p-4 flex flex-col justify-center border-t-2"
                      style={{
                        borderTopColor:
                          verdict.investment_view === 'Avoid' ? 'rgb(244,63,94)' :
                          verdict.investment_view === 'Watchlist' ? 'rgb(245,158,11)' :
                          'rgb(16,185,129)',
                      }}
                    >
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Terminal View</span>
                      <span className={`text-lg font-bold uppercase tracking-wider ${
                        verdict.investment_view === 'Avoid' ? 'text-rose-500' :
                        verdict.investment_view === 'Watchlist' ? 'text-amber-500' :
                        'text-emerald-500'
                      }`}>
                        {verdict.investment_view}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Risk flags */}
                <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
                  <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                    <ShieldAlert size={14} className="text-rose-500" /> Active Risk Flags
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {verdict.risk_flags.length > 0 ? verdict.risk_flags.map((flag, idx) => (
                      <div key={idx} className="bg-rose-950/30 border border-rose-900/50 text-rose-400 px-3 py-1.5 rounded flex items-center gap-2 text-xs font-mono">
                        <AlertTriangle size={12} />
                        {flag}
                      </div>
                    )) : (
                      <span className="text-sm font-mono text-emerald-500">No active risk flags detected.</span>
                    )}
                  </div>
                </div>

                {/* Comparables */}
                <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden flex-1 flex flex-col">
                  <div className="bg-slate-800/50 px-5 py-3 border-b border-slate-800">
                    <h3 className="text-xs font-bold text-slate-200 uppercase tracking-widest">
                      Order Book (Comparables · {verdict.comparables.length})
                    </h3>
                  </div>
                  <div className="overflow-auto flex-1">
                    {verdict.comparables.length > 0 ? (
                      <table className="w-full text-left text-sm whitespace-nowrap">
                        <thead className="bg-slate-950/50 text-[10px] uppercase tracking-wider text-slate-500 font-bold sticky top-0">
                          <tr>
                            <th className="px-5 py-3">Asset</th>
                            <th className="px-5 py-3">Year</th>
                            <th className="px-5 py-3">Mileage</th>
                            <th className="px-5 py-3">Engine / Trans</th>
                            <th className="px-5 py-3 text-right">Listed Price</th>
                            <th className="px-5 py-3 text-right">Spread</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800 font-mono text-slate-300">
                          {verdict.comparables.map((comp, idx) => {
                            const spread = formState.price_gbp - comp.price_gbp;
                            return (
                              <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                                <td className="px-5 py-3">{comp.make} {comp.model}</td>
                                <td className="px-5 py-3">{comp.year}</td>
                                <td className="px-5 py-3">{comp.mileage_miles.toLocaleString()} mi</td>
                                <td className="px-5 py-3">{comp.engine_size_l}L {comp.fuel_type.charAt(0).toUpperCase()} / {comp.transmission}</td>
                                <td className="px-5 py-3 text-right text-slate-100">{formatGBP(comp.price_gbp)}</td>
                                <td className={`px-5 py-3 text-right ${spread > 0 ? 'text-rose-500' : 'text-emerald-500'}`}>
                                  {spread > 0 ? '+' : ''}{formatGBP(spread)}
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    ) : (
                      <div className="p-8 text-center text-slate-600 font-mono text-sm">
                        No comparable listings found for this vehicle.
                      </div>
                    )}
                  </div>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center border border-dashed border-slate-800 rounded-lg text-slate-600 font-mono text-sm">
                {isExecuting ? 'Computing...' : 'Awaiting Execution...'}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
