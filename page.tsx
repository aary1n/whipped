import React, { useState } from 'react';
import { AlertTriangle, TrendingDown, Activity, ShieldAlert, Crosshair, Database } from 'lucide-react';

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

interface VerdictOutput {
  total_cost_5y: number;
  fair_range: [number, number];
  mid_price: number;
  ripoff_index: number;
  risk_score: number;
  counteroffer: number;
  investment_view: "Potential buy" | "Watchlist" | "Avoid";
  risk_flags: string[];
  comparables: ListingInput[];
}

const mockComparables: ListingInput[] = [
  { make: "Porsche", model: "911 Carrera S", year: 2019, price_gbp: 82000, mileage_miles: 24000, engine_size_l: 3.0, fuel_type: "Petrol", transmission: "PDK" },
  { make: "Porsche", model: "911 Carrera S", year: 2019, price_gbp: 84500, mileage_miles: 21500, engine_size_l: 3.0, fuel_type: "Petrol", transmission: "PDK" },
  { make: "Porsche", model: "911 Carrera S", year: 2020, price_gbp: 89000, mileage_miles: 18000, engine_size_l: 3.0, fuel_type: "Petrol", transmission: "PDK" },
];

const mockOutput: VerdictOutput = {
  total_cost_5y: 112450,
  fair_range: [81000, 85000],
  mid_price: 83000,
  ripoff_index: 88,
  risk_score: 74,
  counteroffer: 81500,
  investment_view: "Avoid",
  risk_flags: ["Bore scoring risk on early 991.2", "PDK service due at 40k", "High volatility in 992 allocations"],
  comparables: mockComparables
};

export default function WhippedTerminal() {
  const [formState, setFormState] = useState<ListingInput>({
    make: 'Porsche',
    model: '911 Carrera S',
    year: 2019,
    price_gbp: 87500,
    mileage_miles: 22000,
    engine_size_l: 3.0,
    fuel_type: 'Petrol',
    transmission: 'PDK'
  });

  const [verdict, setVerdict] = useState<VerdictOutput | null>(mockOutput);
  const [isExecuting, setIsExecuting] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormState(prev => ({
      ...prev,
      [name]: name === 'make' || name === 'model' || name === 'fuel_type' || name === 'transmission' ? value : Number(value)
    }));
  };

  const executeArbitrage = (e: React.FormEvent) => {
    e.preventDefault();
    setIsExecuting(true);
    setTimeout(() => {
      setVerdict(mockOutput);
      setIsExecuting(false);
    }, 600);
  };

  const getScoreColor = (score: number, inverse: boolean = false) => {
    const isBad = inverse ? score < 40 : score > 60;
    const isGood = inverse ? score > 70 : score < 40;
    if (isBad) return "text-rose-500";
    if (isGood) return "text-emerald-500";
    return "text-amber-500";
  };

  const formatGBP = (val: number) => new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', maximumFractionDigits: 0 }).format(val);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 font-sans p-4 selection:bg-teal-900 selection:text-teal-100">
      <div className="max-w-[1600px] mx-auto h-[calc(100vh-2rem)] flex flex-col">
        
        {/* Header bar */}
        <header className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
          <div className="flex items-center gap-2 text-slate-100">
            <Activity size={20} className="text-teal-500" />
            <h1 className="font-bold tracking-widest text-sm uppercase">Whipped <span className="text-slate-500 font-normal">| Quant Arb Engine v2.1.0</span></h1>
          </div>
          <div className="text-xs font-mono text-slate-500 flex items-center gap-4">
            <span>SYS: <span className="text-emerald-500">ONLINE</span></span>
            <span>LATENCY: 12ms</span>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-0">
          
          {/* LEFT COLUMN: Input Panel */}
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
                    <option>Auto</option>
                    <option>PDK</option>
                    <option>DSG</option>
                  </select>
                </div>
              </div>

              <div className="mt-auto pt-6">
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

          {/* RIGHT COLUMN: Terminal / Output */}
          <div className="lg:col-span-8 xl:col-span-9 flex flex-col gap-6 overflow-y-auto min-h-0">
            
            {verdict ? (
              <>
                {/* Top Section: Hero & Grid */}
                <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                  
                  {/* Hero Metric */}
                  <div className="xl:col-span-1 bg-slate-900 border border-slate-800 rounded-lg p-6 flex flex-col justify-center relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-teal-900/10 rounded-bl-full -mr-8 -mt-8 transition-transform group-hover:scale-110"></div>
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2 flex items-center gap-2">
                      <TrendingDown size={14} /> Total 5Y TCO
                    </h3>
                    <div className="text-4xl lg:text-5xl font-mono text-slate-100 tracking-tight">
                      {formatGBP(verdict.total_cost_5y)}
                    </div>
                    <div className="mt-4 text-xs font-mono text-slate-500">
                      Delta vs Asset Price: <span className="text-rose-500">+{formatGBP(verdict.total_cost_5y - formState.price_gbp)}</span>
                    </div>
                  </div>

                  {/* Deal Analysis Grid */}
                  <div className="xl:col-span-2 grid grid-cols-2 md:grid-cols-3 gap-px bg-slate-800 rounded-lg overflow-hidden border border-slate-800">
                    <div className="bg-slate-900 p-4 flex flex-col justify-center">
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Fair Range</span>
                      <span className="text-lg font-mono text-slate-300">{formatGBP(verdict.fair_range[0])} - {formatGBP(verdict.fair_range[1])}</span>
                    </div>
                    <div className="bg-slate-900 p-4 flex flex-col justify-center">
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Mid Price</span>
                      <span className="text-lg font-mono text-slate-300">{formatGBP(verdict.mid_price)}</span>
                    </div>
                    <div className="bg-slate-900 p-4 flex flex-col justify-center">
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Ripoff Score</span>
                      <span className={`text-2xl font-mono ${getScoreColor(verdict.ripoff_index)}`}>{verdict.ripoff_index}<span className="text-sm text-slate-600">/100</span></span>
                    </div>
                    <div className="bg-slate-900 p-4 flex flex-col justify-center">
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Risk Score</span>
                      <span className={`text-2xl font-mono ${getScoreColor(verdict.risk_score)}`}>{verdict.risk_score}<span className="text-sm text-slate-600">/100</span></span>
                    </div>
                    <div className="bg-slate-900 p-4 flex flex-col justify-center">
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Max Bid (Counter)</span>
                      <span className="text-xl font-mono text-teal-400">{formatGBP(verdict.counteroffer)}</span>
                    </div>
                    <div className="bg-slate-900 p-4 flex flex-col justify-center border-t-2 border-t-transparent data-[view=Avoid]:border-t-rose-500 data-[view=Watchlist]:border-t-amber-500 data-[view='Potential buy']:border-t-emerald-500" data-view={verdict.investment_view}>
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Terminal View</span>
                      <span className={`text-lg font-bold uppercase tracking-wider ${verdict.investment_view === 'Avoid' ? 'text-rose-500' : verdict.investment_view === 'Watchlist' ? 'text-amber-500' : 'text-emerald-500'}`}>
                        {verdict.investment_view}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Risk & Longevity */}
                <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
                  <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                    <ShieldAlert size={14} className="text-rose-500" /> Active Risk Flags
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {verdict.risk_flags.map((flag, idx) => (
                      <div key={idx} className="bg-rose-950/30 border border-rose-900/50 text-rose-400 px-3 py-1.5 rounded flex items-center gap-2 text-xs font-mono">
                        <AlertTriangle size={12} />
                        {flag}
                      </div>
                    ))}
                    {verdict.risk_flags.length === 0 && (
                      <span className="text-sm font-mono text-emerald-500">No active risk flags detected.</span>
                    )}
                  </div>
                </div>

                {/* Order Book / Comparables */}
                <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden flex-1 flex flex-col">
                  <div className="bg-slate-800/50 px-5 py-3 border-b border-slate-800">
                    <h3 className="text-xs font-bold text-slate-200 uppercase tracking-widest">Order Book (Comparables)</h3>
                  </div>
                  <div className="overflow-auto flex-1 p-0">
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
                              <td className="px-5 py-3">{comp.engine_size_l}L {comp.fuel_type.charAt(0)} / {comp.transmission}</td>
                              <td className="px-5 py-3 text-right text-slate-100">{formatGBP(comp.price_gbp)}</td>
                              <td className={`px-5 py-3 text-right ${spread > 0 ? 'text-rose-500' : 'text-emerald-500'}`}>
                                {spread > 0 ? '+' : ''}{formatGBP(spread)}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center border border-dashed border-slate-800 rounded-lg text-slate-600 font-mono text-sm">
                Awaiting Execution...
              </div>
            )}
            
          </div>
        </div>
      </div>
    </div>
  );
}