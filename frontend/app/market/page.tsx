'use client';

import React from 'react';
import { useVerdict } from '../lib/verdict-context';
import Link from 'next/link';
import { fmt, recColor, bandColor } from '../lib/shared';

const UPPER = new Set(['vw', 'bmw', 'mg', 'ds', 'gmc', 'ram']);
const titleCase = (s: string) =>
  s.split(' ').map(w => UPPER.has(w.toLowerCase()) ? w.toUpperCase() : w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(' ');

export default function MarketPage() {
  const { verdict, formState } = useVerdict();

  if (!verdict) {
    return (
      <div className="max-w-3xl mx-auto text-center py-20">
        <h2 className="text-2xl font-bold text-slate-300 mb-2">No analysis found.</h2>
        <p className="text-slate-500 mb-6">
          Please run a valuation on the analysis page to see market context.
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

  const { comparables, brand_tax } = verdict;

  return (
    <div className="max-w-7xl mx-auto p-4 sm:p-6">
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-slate-100 tracking-tight">Market Context</h1>
        <p className="text-lg text-slate-400 mt-2">
          How the {formState.year} {formState.make} {formState.model} stacks up against similar vehicles.
        </p>
      </header>

      {/* Brand Tax Section */}
      {brand_tax && (
        <section className="mb-8 bg-slate-900 border border-slate-800 rounded-lg p-6">
            <h2 className="text-xl font-bold text-slate-200 mb-4">Brand Tax Analysis</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                    <p className="text-sm text-slate-500 mb-1">This vehicle vs mechanically similar cars:</p>
                    <p className={`text-4xl font-mono ${recColor(brand_tax.is_good_deal ? 'Potential buy' : 'Avoid')}`}>
                        {fmt(brand_tax.brand_tax_gbp)}
                    </p>
                    <p className={`text-sm font-semibold ${recColor(brand_tax.is_good_deal ? 'Potential buy' : 'Avoid')}`}>
                        {brand_tax.is_good_deal ? 'Good Value' : 'Poor Value'}
                    </p>
                </div>
                <div>
                    <p className="text-sm text-slate-500 mb-1">Average price for this performance</p>
                    <p className="text-2xl font-mono text-slate-300">{fmt(brand_tax.avg_twin_price_gbp)}</p>
                </div>
                <div className="md:col-span-3">
                    <p className="text-sm text-slate-500 mb-3">Recommendations:</p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                        {brand_tax.recommendations
                          .filter((r, i, arr) => arr.findIndex(a => a.make === r.make && a.model === r.model) === i)
                          .map((r, i) => (
                          <div key={i} className="bg-slate-950 border border-slate-800 rounded-md px-4 py-3 flex items-center justify-between gap-3">
                            <div>
                              <p className="text-sm font-semibold text-teal-400">{titleCase(`${r.make} ${r.model}`)}</p>
                              <p className="text-xs text-slate-500">{r.year}</p>
                            </div>
                            <div className="text-right">
                              <p className="text-sm font-mono text-slate-300">{fmt(r.price_gbp)}</p>
                              <p className={`text-xs font-mono ${r.brand_tax_gbp > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                                {r.brand_tax_gbp > 0 ? '+' : ''}{fmt(r.brand_tax_gbp)} tax
                              </p>
                            </div>
                          </div>
                        ))}
                    </div>
                </div>
            </div>
        </section>
      )}

      {/* Market Comparables Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-800">
          <h2 className="text-base font-bold text-slate-200 uppercase tracking-widest">Market Comparables</h2>
        </div>
        <div className="overflow-auto">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-slate-950/50 text-[10px] uppercase tracking-wider text-slate-500 font-bold sticky top-0">
              <tr>
                <th className="px-5 py-3">Vehicle</th>
                <th className="px-5 py-3">Year</th>
                <th className="px-5 py-3">Mileage</th>
                <th className="px-5 py-3">Engine / Trans</th>
                <th className="px-5 py-3 text-right">Listed Price</th>
                <th className="px-5 py-3 text-right">Spread vs Subject</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono text-slate-300">
              {comparables.map((comp, idx) => {
                const spread = formState.price_gbp - comp.price_gbp;
                return (
                  <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-5 py-3">{comp.make} {comp.model}</td>
                    <td className="px-5 py-3">{comp.year}</td>
                    <td className="px-5 py-3">{comp.mileage_miles.toLocaleString()} mi</td>
                    <td className="px-5 py-3">{comp.engine_size_l}L {comp.fuel_type.charAt(0)} / {comp.transmission}</td>
                    <td className="px-5 py-3 text-right text-slate-100">{fmt(comp.price_gbp)}</td>
                    <td className={`px-5 py-3 text-right ${spread > 0 ? 'text-rose-500' : 'text-emerald-500'}`}>
                      {spread > 0 ? '+' : ''}{fmt(spread)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        {comparables.length === 0 && (
            <div className="p-10 text-center text-slate-600 font-mono">No direct comparables found for this specific search.</div>
        )}
      </div>
    </div>
  );
}
