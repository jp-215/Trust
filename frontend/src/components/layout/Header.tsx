import Link from 'next/link';

function ShieldLogo() {
  return (
    <svg
      width="28"
      height="28"
      viewBox="0 0 24 24"
      fill="none"
      stroke="#0E7C66"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M12 2l8 4v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6z" />
      <path d="M9 12l2 2 4-4" />
    </svg>
  );
}

export function Header() {
  return (
    <header className="bg-white border-b border-line">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-8">
        <Link href="/" className="flex items-center gap-2.5">
          <ShieldLogo />
          <span className="font-display text-2xl font-bold tracking-tight">
            Trust
          </span>
        </Link>
        <nav aria-label="Primary" className="flex gap-6 text-sm font-medium">
          <Link href="/" className="text-ink hover:text-accent-deep">
            Trending
          </Link>
          <Link
            href="/#stories"
            className="text-ink-muted hover:text-accent-deep"
          >
            Stories
          </Link>
          <Link
            href="/#outlets"
            className="text-ink-muted hover:text-accent-deep"
          >
            Outlets
          </Link>
        </nav>
      </div>
    </header>
  );
}
