'use client';

import React, { useState } from 'react';
import { useVerdict } from '../lib/verdict-context';
import Link from 'next/link';
import { AlertTriangle, TrendingDown, Activity, ShieldAlert, Crosshair, Database, Info, User, ChevronDown, FileText } from 'lucide-react';
import type { VerdictOutput, ListingInput } from '../lib/shared';
import { INPUT, LABEL, CELL, CELL_LABEL, fmt, scoreColor, recColor, recBorder } from '../lib/shared';




function Tip({ text, position = 'right' }: { text: string; position?: 'right' | 'left' }) {
  const pos = position === 'left'
    ? 'right-full top-full mt-1 mr-1'
    : 'left-full top-1/2 -translate-y-1/2 ml-2';
  return (
    <span className="relative group inline-flex ml-1 cursor-help">
      <Info size={11} className="text-slate-600 group-hover:text-slate-400 transition-colors" />
      <span className={`absolute ${pos} px-2.5 py-1.5 rounded bg-slate-800 border border-slate-700 text-[11px] text-slate-300 font-normal normal-case tracking-normal whitespace-normal w-48 text-left opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto transition-opacity z-50 shadow-lg`}>
        {text}
      </span>
    </span>
  );
}

export default function AnalyzePage() {
  const { formState, setFormState, driverState, setDriverState, verdict, setVerdict } = useVerdict();
  const [driverOpen, setDriverOpen] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormState(prev => ({
      ...prev,
      [name]: name === 'make' || name === 'model' || name === 'fuel_type' || name === 'transmission' ? value : Number(value)
    }));
  };
  const handleDriverChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setDriverState(prev => ({
      ...prev,
      [name]: ['sex', 'postcode_area', 'parking', 'cover_type'].includes(name) ? value : (value === '' ? '' : Number(value)),
    }));
  };

  const executeValuation = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsExecuting(true);
    setError(null);
    setVerdict(null);

    try {
      const response = await fetch('/api/evaluate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formState,
          driver: driverState,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: VerdictOutput = await response.json();
      setVerdict(data);
    } catch (err: any) {
      console.error("Failed to execute valuation:", err);
      setError("An error occurred while fetching the valuation. Please ensure the backend server is running and accessible.");
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="max-w-[1600px] mx-auto p-4 sm:p-6">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* LEFT COLUMN: Input Panel */}
        <div className="lg:col-span-4 xl:col-span-3 bg-slate-900 border border-slate-800 rounded-lg shadow-2xl h-fit">
          <div className="bg-slate-800/50 px-4 py-3 border-b border-slate-800 flex items-center gap-2">
            <Database size={14} className="text-teal-500" />
            <h2 className="text-xs font-bold tracking-widest text-slate-200 uppercase">Vehicle & Driver Specs</h2>
          </div>
          <form onSubmit={executeValuation} className="p-4 flex flex-col gap-4">
            {/* Form fields */}
            <div className="grid grid-cols-2 gap-3">
                <div className="col-span-2">
                    <label className={LABEL}>Make</label>
                    <input type="text" name="make" value={formState.make} onChange={handleInputChange} className={INPUT} />
                </div>
                <div className="col-span-2">
                    <label className={LABEL}>Model</label>
                    <input type="text" name="model" value={formState.model} onChange={handleInputChange} className={INPUT} />
                </div>
                <div>
                    <label className={LABEL}>Year</label>
                    <input type="number" name="year" value={formState.year} onChange={handleInputChange} className={INPUT} />
                </div>
                <div>
                    <label className={LABEL}>Listed Price (£)</label>
                    <input type="number" name="price_gbp" value={formState.price_gbp} onChange={handleInputChange} className={INPUT} />
                </div>
                <div>
                    <label className={LABEL}>Mileage</label>
                    <input type="number" name="mileage_miles" value={formState.mileage_miles} onChange={handleInputChange} className={INPUT} />
                </div>
                <div>
                    <label className={LABEL}>Engine (L)</label>
                    <input type="number" step="0.1" name="engine_size_l" value={formState.engine_size_l} onChange={handleInputChange} className={INPUT} />
                </div>
                <div className="col-span-2">
                    <label className={LABEL}>Fuel Type</label>
                    <select name="fuel_type" value={formState.fuel_type} onChange={handleInputChange} className={`${INPUT} appearance-none`}>
                        <option>Petrol</option><option>Diesel</option><option>Hybrid</option><option>Electric</option>
                    </select>
                </div>
                <div className="col-span-2">
                    <label className={LABEL}>Transmission</label>
                    <select name="transmission" value={formState.transmission} onChange={handleInputChange} className={`${INPUT} appearance-none`}>
                        <option>Manual</option><option>Auto</option><option>PDK</option><option>DSG</option>
                    </select>
                </div>
            </div>

            {/* Driver Profile — collapsible */}
            <div className="border border-slate-800 rounded-lg overflow-hidden">
              <button type="button" onClick={() => setDriverOpen(o => !o)} className="w-full flex items-center justify-between px-3 py-2.5 bg-slate-800/40 hover:bg-slate-800/70 transition-colors">
                <div className="flex items-center gap-2">
                  <User size={13} className="text-teal-500" />
                  <span className="text-[10px] font-bold text-slate-300 uppercase tracking-widest">Driver Profile</span>
                </div>
                <ChevronDown size={14} className={`text-slate-500 transition-transform duration-200 ${driverOpen ? 'rotate-180' : ''}`} />
              </button>
              {driverOpen && (
                <div className="p-3 grid grid-cols-2 gap-3 bg-slate-900/50">
                  <div className="col-span-2"><label className={LABEL}>Sex</label>
                    <select name="sex" value={driverState.sex} onChange={handleDriverChange} className={`${INPUT} appearance-none`}>
                      <option value="">— unspecified —</option><option value="male">Male</option><option value="female">Female</option>
                    </select>
                  </div>
                  <div><label className={LABEL}>Age</label><input type="number" name="age" min={17} max={99} value={driverState.age} onChange={handleDriverChange} placeholder="—" className={INPUT} /></div>
                  <div><label className={LABEL}>Yrs Licensed</label><input type="number" name="years_licensed" min={0} value={driverState.years_licensed} onChange={handleDriverChange} placeholder="—" className={INPUT} /></div>
                  <div><label className={LABEL}>No-Claims Yrs</label><input type="number" name="no_claims_years" min={0} value={driverState.no_claims_years} onChange={handleDriverChange} placeholder="—" className={INPUT} /></div>
                  <div><label className={LABEL}>Claims (5y)</label><input type="number" name="claims_last_5y" min={0} max={10} value={driverState.claims_last_5y} onChange={handleDriverChange} className={INPUT} /></div>
                  <div><label className={LABEL}>Annual Miles</label><input type="number" name="annual_mileage" min={0} value={driverState.annual_mileage} onChange={handleDriverChange} placeholder="—" className={INPUT} /></div>
                  <div><label className={LABEL}>Postcode Area</label><input type="text" name="postcode_area" value={driverState.postcode_area} onChange={handleDriverChange} placeholder="e.g. SW1" maxLength={4} className={`${INPUT} uppercase`} /></div>
                  <div className="col-span-2"><label className={LABEL}>Parking</label>
                    <select name="parking" value={driverState.parking} onChange={handleDriverChange} className={`${INPUT} appearance-none`}>
                      <option value="">— unspecified —</option><option value="street">Street</option><option value="driveway">Driveway</option><option value="garage">Garage</option>
                    </select>
                  </div>
                  <div className="col-span-2"><label className={LABEL}>Cover Type</label>
                    <select name="cover_type" value={driverState.cover_type} onChange={handleDriverChange} className={`${INPUT} appearance-none`}>
                      <option value="">— unspecified —</option><option value="third_party">Third Party</option><option value="third_party_fire_theft">TP Fire &amp; Theft</option><option value="comprehensive">Comprehensive</option>
                    </select>
                  </div>
                </div>
              )}
            </div>

            <div className="mt-4 pt-4 border-t border-slate-800">
              <button
                type="submit" 
                disabled={isExecuting}
                className={`w-full flex items-center justify-center gap-2 py-3 rounded text-xs font-bold tracking-[0.2em] uppercase transition-all ${isExecuting ? 'bg-slate-800 text-slate-500' : 'bg-teal-900 hover:bg-teal-800 text-teal-400 border border-teal-800 hover:border-teal-600 shadow-[0_0_15px_rgba(20,184,166,0.15)]'}`}
              >
                <Crosshair size={16} className={isExecuting ? 'animate-spin' : ''} />
                {isExecuting ? 'Processing...' : 'Run Valuation'}
              </button>
            </div>
          </form>
        </div>

        {/* RIGHT COLUMN: Output */}
        <div className="lg:col-span-8 xl:col-span-9 flex flex-col gap-6">
          {error && (
            <div className="bg-rose-900/30 border border-rose-800 text-rose-400 p-4 rounded-lg text-sm">
              <p className="font-bold flex items-center gap-2"><AlertTriangle size={16} />Error</p>
              <p className="mt-1">{error}</p>
            </div>
          )}

          {verdict ? (
            <>
              {/* Main Analysis Grid */}
              <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-px bg-slate-800 rounded-lg overflow-hidden border border-slate-800">
                <div className={`${CELL} col-span-2 md:col-span-1 xl:col-span-1`} style={{ borderTop: `2px solid ${recBorder(verdict.investment_view)}`}}>
                    <span className={CELL_LABEL}>Recommendation<Tip text="Our overall buy/watch/avoid signal based on pricing, risk, and market position." /></span>
                    <span className={`text-xl font-bold uppercase tracking-wider ${recColor(verdict.investment_view)}`}>{verdict.investment_view}</span>
                </div>
                 <div className={CELL}>
                    <span className={CELL_LABEL}>Fair Market Range<Tip text="The price range for comparable vehicles based on make, model, year, mileage, and spec." /></span>
                    <span className="text-lg font-mono text-slate-300">{fmt(verdict.fair_range[0])} - {fmt(verdict.fair_range[1])}</span>
                </div>
                <div className={CELL}>
                    <span className={CELL_LABEL}>Market Midpoint<Tip text="The median price of comparable listings — our best estimate of fair value." /></span>
                    <span className="text-lg font-mono text-slate-300">{fmt(verdict.mid_price)}</span>
                </div>
                <div className={`${CELL} text-teal-400`}>
                    <span className={CELL_LABEL}>Target Counteroffer<Tip text="A suggested negotiation price based on market position and risk. N/A for bargains or low-confidence results." position="left" /></span>
                    <span className="text-xl font-mono">{verdict.counteroffer ? fmt(verdict.counteroffer) : "N/A"}</span>
                </div>
                <div className={CELL}>
                    <span className={CELL_LABEL}>Price Fairness<Tip text="How fairly priced this listing is vs the market. 100 = bargain, 0 = extremely overpriced." /></span>
                    <span className={`text-2xl font-mono ${(100 - verdict.ripoff_index) >= 60 ? 'text-emerald-500' : (100 - verdict.ripoff_index) >= 40 ? 'text-amber-500' : 'text-rose-500'}`}>{100 - verdict.ripoff_index}<span className="text-sm text-slate-600">/100</span></span>
                </div>
                <div className={CELL}>
                    <span className={CELL_LABEL}>Comparables Found<Tip text="Number of similar listings used to estimate the fair price range." /></span>
                    <span className="text-lg font-mono text-slate-300">{verdict.comparable_count}</span>
                </div>
              </div>

              {/* Risk Flags */}
              <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                  <ShieldAlert size={14} className="text-rose-500" /> Active Risk Flags
                </h3>
                {verdict.risk_flags.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                        {verdict.risk_flags.map((flag, idx) => (
                        <div key={idx} className="bg-rose-950/30 border border-rose-900/50 text-rose-400 px-3 py-1.5 rounded flex items-center gap-2 text-xs font-mono">
                            <AlertTriangle size={12} />
                            {flag}
                        </div>
                        ))}
                    </div>
                ) : (
                    <p className="text-sm text-emerald-500 font-mono">No specific risk flags identified.</p>
                )}
              </div>

              {/* Verdict Summary */}
              <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                  <FileText size={14} className="text-teal-500" /> Verdict Summary
                </h3>
                <p className="text-sm font-mono text-slate-400 leading-relaxed">{verdict.explanation}</p>
                {verdict.pricing_position && (
                  <div className="mt-3 flex items-center gap-3">
                    <span className="text-[10px] font-bold text-slate-600 uppercase tracking-widest">Position:</span>
                    <span className="text-xs font-mono text-slate-400">{verdict.pricing_position}</span>
                    <span className="text-[10px] font-bold text-slate-600 uppercase tracking-widest ml-2">vs Mid:</span>
                    {(() => {
                      const delta = formState.price_gbp - verdict.mid_price;
                      return <span className={`text-xs font-mono ${delta > 0 ? 'text-rose-500' : 'text-emerald-500'}`}>{delta > 0 ? '+' : ''}{fmt(delta)}</span>;
                    })()}
                  </div>
                )}
              </div>

              {/* Navigation to other pages */}
              <div className="grid grid-cols-2 gap-4">
                <Link href="/ownership" className="bg-slate-900 border border-slate-800 rounded-lg p-5 hover:border-teal-800 transition-colors group">
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">5-Year Ownership Forecast</p>
                  <p className="text-lg font-mono text-slate-300">{fmt(verdict.total_cost_5y)} <span className="text-sm text-slate-600">total cost</span></p>
                  <p className="text-xs text-teal-600 mt-2 group-hover:text-teal-400 transition-colors">View full breakdown &rarr;</p>
                </Link>
                <Link href="/market" className="bg-slate-900 border border-slate-800 rounded-lg p-5 hover:border-teal-800 transition-colors group">
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Market Evidence</p>
                  <p className="text-lg font-mono text-slate-300">{(verdict.comparables ?? []).length} <span className="text-sm text-slate-600">similar listings</span></p>
                  <p className="text-xs text-teal-600 mt-2 group-hover:text-teal-400 transition-colors">View comparables &amp; brand tax &rarr;</p>
                </Link>
              </div>
            </>
          ) : (
            <div className="h-full min-h-[400px] flex items-center justify-center border border-dashed border-slate-800 rounded-lg">
              <div className="text-center">
                <p className="text-slate-500 font-mono text-sm">Awaiting execution...</p>
                <p className="text-slate-600 text-xs mt-1">Fill in the form and run the valuation model.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}