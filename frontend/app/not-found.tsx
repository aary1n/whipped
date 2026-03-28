import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="max-w-3xl mx-auto text-center py-20">
      <h2 className="text-2xl font-bold text-slate-300 mb-2">Page not found</h2>
      <p className="text-slate-500 mb-6">The page you're looking for doesn't exist.</p>
      <Link
        href="/"
        className="inline-flex items-center gap-2 px-5 py-2.5 rounded-md bg-teal-600 hover:bg-teal-500 text-white text-sm font-semibold tracking-wide uppercase transition-colors"
      >
        Go Home
      </Link>
    </div>
  );
}
