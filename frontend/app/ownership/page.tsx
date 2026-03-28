'use client';

import React from 'react';
import { useVerdict } from '../lib/verdict-context';
import { TrendingDown, Shield, Wrench, Info } from 'lucide-react';
import Link from 'next/link';
import { CELL, CELL_LABEL, fmt, bandColor } from '../lib/shared';

export default function OwnershipPage() {
  const { verdict, formState } = useVerdict();

  if (!verdict) {
    return (
      <div className="max-w-3xl mx-auto text-center py-20">
        <h2 className="text-2xl font-bold text-slate-300 mb-2">No analysis found.</h2>
        <p className="text-slate-500 mb-6">
          Please run a valuation on the analysis page to see the ownership forecast.
        </p>
        <Link
          href="/analyze"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-md bg-teal-600 hover:bg-teal-500 text-white text-sm font-semibold tracking-wide uppercase transition-colors"
        >
          Go to Analysis
        </Link>
      </div>
    );
  }

  const { ownership } = verdict;

  return (
    <div className="max-w-4xl mx-auto p-4 sm:p-6">
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-slate-100 tracking-tight">5-Year Ownership Forecast</h1>
        <p className="text-lg text-slate-400 mt-2">
          An estimate of what it might cost to own a {formState.year} {formState.make} {formState.model} over the next five years.
        </p>
      </header>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 flex flex-col justify-center items-center text-center">
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2 flex items-center gap-2">
            <TrendingDown size={14} /> Total Cost of Ownership
          </h3>
          <div className="text-5xl font-mono text-slate-100 tracking-tight">
            {fmt(verdict.total_cost_5y)}
          </div>
          <div className="mt-2 text-sm font-mono text-slate-500">
            (Listed Price + 5-Year Costs)
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-px bg-slate-800 rounded-lg overflow-hidden border border-slate-800">
          <div className={`${CELL} items-center text-center`}>
            <span className={CELL_LABEL}>Annual Running Cost</span>
            <span className="text-2xl font-mono text-slate-300">{fmt(ownership.annual_running_cost_gbp)}</span>
          </div>
          <div className={`${CELL} items-center text-center`}>
            <span className={CELL_LABEL}>Ownership Cost Band</span>
            <span className={`text-2xl font-bold uppercase ${bandColor(ownership.ownership_band)}`}>{ownership.ownership_band}</span>
          </div>
          <div className={`${CELL} items-center text-center`}>
            <span className={CELL_LABEL}>Insurance Cost Band</span>
            <span className={`text-2xl font-bold uppercase ${bandColor(ownership.insurance_band)}`}>{ownership.insurance_band}</span>
          </div>
          <div className={`${CELL} items-center text-center`}>
            <span className={CELL_LABEL}>Repair Risk</span>
            <span className="text-2xl font-mono text-slate-300">{ownership.repair_risk_pct}%</span>
          </div>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-lg">
        <div className="px-6 py-4 border-b border-slate-800">
            <h3 className="text-base font-bold text-slate-200">5-Year Cost Breakdown</h3>
        </div>
        <div className="divide-y divide-slate-800">
          <div className="px-6 py-4 grid grid-cols-3 items-center gap-4">
            <div className="flex items-center gap-3 col-span-1">
              <Shield size={18} className="text-amber-500" />
              <span className="font-semibold text-slate-300">Depreciation</span>
            </div>
            <p className="text-sm text-slate-400 col-span-1">The estimated loss in the vehicle's value over 5 years.</p>
            <p className="text-right text-lg font-mono text-amber-400 col-span-1">{fmt(ownership.depreciation_5y_gbp)}</p>
          </div>
          
          <div className="px-6 py-4 grid grid-cols-3 items-center gap-4">
            <div className="flex items-center gap-3 col-span-1">
              <Wrench size={18} className="text-rose-500" />
              <span className="font-semibold text-slate-300">Repairs & Maintenance</span>
            </div>
            <p className="text-sm text-slate-400 col-span-1">An allowance for typical repairs and servicing for this model.</p>
            <p className="text-right text-lg font-mono text-rose-400 col-span-1">{fmt(ownership.repairs_5y_gbp)}</p>
          </div>

          <div className="px-6 py-4 grid grid-cols-3 items-center gap-4">
            <div className="flex items-center gap-3 col-span-1">
              <Info size={18} className="text-cyan-500" />
              <span className="font-semibold text-slate-300">Insurance</span>
            </div>
            <p className="text-sm text-slate-400 col-span-1">Estimated total insurance premiums based on driver and vehicle profile.</p>
            <p className="text-right text-lg font-mono text-cyan-400 col-span-1">{fmt(ownership.insurance_5y_gbp)}</p>
          </div>
        </div>
      </div>
      
      {ownership.notes && ownership.notes.length > 0 && (
        <div className="mt-6 bg-slate-900/50 border border-slate-800 rounded-lg p-5">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                <Info size={14} /> Model Notes
            </h3>
            <ul className="list-disc list-inside text-slate-400 text-sm space-y-1">
                {ownership.notes.map((note, i) => <li key={i}>{note}</li>)}
            </ul>
        </div>
      )}
    </div>
  );
}
