/**
 * aitema|RIS - Admin Layout
 * Wraps all admin pages with sidebar navigation and auth check.
 */

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      {/* Admin Sidebar */}
      <aside className="w-64 bg-gray-900 text-gray-300 flex-shrink-0">
        <div className="p-4 border-b border-gray-700">
          <h2 className="text-white font-bold text-lg">Verwaltung</h2>
          <p className="text-xs text-gray-500 mt-1">aitema|RIS Admin</p>
        </div>
        <nav aria-label="Admin-Navigation" className="p-2">
          <ul className="space-y-1">
            <li>
              <a
                href="/admin"
                className="block px-3 py-2 rounded-md text-sm hover:bg-gray-800 hover:text-white"
              >
                Dashboard
              </a>
            </li>
            <li>
              <a
                href="/admin/meetings"
                className="block px-3 py-2 rounded-md text-sm hover:bg-gray-800 hover:text-white"
              >
                Sitzungen verwalten
              </a>
            </li>
            <li>
              <a
                href="/admin/papers"
                className="block px-3 py-2 rounded-md text-sm hover:bg-gray-800 hover:text-white"
              >
                Vorlagen verwalten
              </a>
            </li>
            <li>
              <a
                href="/admin/organizations"
                className="block px-3 py-2 rounded-md text-sm hover:bg-gray-800 hover:text-white"
              >
                Gremien verwalten
              </a>
            </li>
            <li>
              <a
                href="/admin/persons"
                className="block px-3 py-2 rounded-md text-sm hover:bg-gray-800 hover:text-white"
              >
                Personen verwalten
              </a>
            </li>
            <li className="pt-2 mt-2 border-t border-gray-700">
              <a
                href="/admin/workflows"
                className="block px-3 py-2 rounded-md text-sm hover:bg-gray-800 hover:text-white"
              >
                Workflows
              </a>
            </li>
            <li>
              <a
                href="/admin/templates"
                className="block px-3 py-2 rounded-md text-sm hover:bg-gray-800 hover:text-white"
              >
                Vorlagen-Templates
              </a>
            </li>
            <li className="pt-2 mt-2 border-t border-gray-700">
              <a
                href="/admin/tenants"
                className="block px-3 py-2 rounded-md text-sm hover:bg-gray-800 hover:text-white"
              >
                Mandanten
              </a>
            </li>
            <li>
              <a
                href="/admin/settings"
                className="block px-3 py-2 rounded-md text-sm hover:bg-gray-800 hover:text-white"
              >
                Einstellungen
              </a>
            </li>
          </ul>
        </nav>
      </aside>

      {/* Admin Content */}
      <div className="flex-1 bg-gray-100 p-8">{children}</div>
    </div>
  );
}
