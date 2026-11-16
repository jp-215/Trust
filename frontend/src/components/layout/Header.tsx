import Link from 'next/link';

export function Header() {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-baseline justify-between">
        <Link href="/" className="group">
          <h1 className="text-2xl font-bold">
            <span aria-hidden="true">🛡️</span> Trust
          </h1>
          <p className="text-sm text-gray-600 group-hover:text-gray-800">
            Cross-outlet fact checking from Databricks gold tables
          </p>
        </Link>
        <nav aria-label="Primary">
          <Link
            href="/"
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            Dashboard
          </Link>
        </nav>
      </div>
    </header>
  );
}
