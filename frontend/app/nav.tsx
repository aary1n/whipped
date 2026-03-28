'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Activity } from 'lucide-react';

const links = [
  { href: '/', label: 'Home' },
  { href: '/analyze', label: 'Analyse' },
  { href: '/ownership', label: 'Ownership' },
  { href: '/market', label: 'Market' },
];

export function Nav() {
  const pathname = usePathname();

  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-[1400px] mx-auto px-6 h-14 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 text-slate-100 hover:text-teal-400 transition-colors">
          <Activity size={18} className="text-teal-500" />
          <span className="font-bold tracking-[0.15em] text-sm uppercase">Whipped</span>
        </Link>
        <nav className="flex items-center gap-1">
          {links.map(({ href, label }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={`px-3 py-1.5 rounded text-xs font-medium tracking-wide uppercase transition-colors ${
                  active
                    ? 'bg-slate-800 text-teal-400'
                    : 'text-slate-500 hover:text-slate-300 hover:bg-slate-900'
                }`}
              >
                {label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
