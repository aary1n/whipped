import Link from 'next/link';
import { TrendingDown, ShieldAlert, Wrench } from 'lucide-react';

const features = [
  {
    icon: TrendingDown,
    title: 'Fair Price Band',
    desc: 'Statistical valuation from thousands of real UK listings. Know the fair range before you negotiate.',
  },
  {
    icon: ShieldAlert,
    title: 'Hidden Risk Detection',
    desc: 'Flags for high mileage, pricing anomalies, and mechanical risk factors that sellers won\'t mention.',
  },
  {
    icon: Wrench,
    title: '5-Year Ownership Forecast',
    desc: 'Insurance, depreciation, and repair costs projected forward so you know the true cost of ownership.',
  },
];

export default function HomePage() {
  return (
    <div className="max-w-[1000px] mx-auto px-6">
      {/* Hero */}
      <section className="pt-24 pb-20 text-center">
        <p className="text-teal-500 text-xs font-bold tracking-[0.3em] uppercase mb-4">Used Car Pricing Intelligence</p>
        <h1 className="text-4xl md:text-5xl font-bold text-slate-100 tracking-tight leading-tight">
          Know what a used car<br />is really worth
        </h1>
        <p className="mt-5 text-lg text-slate-400 max-w-[560px] mx-auto leading-relaxed">
          Whipped analyses thousands of UK listings to give you a fair price range, surface hidden risks, and forecast what you'll actually spend over five years.
        </p>
        <div className="mt-10 flex items-center justify-center gap-4">
          <Link
            href="/analyze"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-md bg-teal-600 hover:bg-teal-500 text-white text-sm font-semibold tracking-wide uppercase transition-colors shadow-lg shadow-teal-900/30"
          >
            Start Analysis
          </Link>
          <span className="text-xs text-slate-600 font-mono">98k+ listings indexed</span>
        </div>
      </section>

      {/* Feature cards */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-5 pb-24">
        {features.map(({ icon: Icon, title, desc }) => (
          <div key={title} className="bg-slate-900 border border-slate-800 rounded-lg p-6 flex flex-col gap-3">
            <div className="w-9 h-9 rounded-md bg-slate-800 flex items-center justify-center">
              <Icon size={18} className="text-teal-500" />
            </div>
            <h3 className="text-sm font-bold text-slate-200 tracking-wide">{title}</h3>
            <p className="text-sm text-slate-500 leading-relaxed">{desc}</p>
          </div>
        ))}
      </section>

      {/* Methodology */}
      <section className="border-t border-slate-800 py-16 text-center">
        <p className="text-[10px] font-bold text-slate-600 uppercase tracking-[0.3em] mb-3">Methodology</p>
        <p className="text-sm text-slate-500 max-w-[500px] mx-auto leading-relaxed">
          Comparables-based statistical pricing with a 4-tier cascade filter.
          KNN brand-tax model for cross-make analysis.
          Risk scoring from mileage, age, and market position.
          Insurance forecasting via trained neural network on synthetic UK quote data.
        </p>
      </section>
    </div>
  );
}
