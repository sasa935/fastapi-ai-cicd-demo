import { NavLink, Outlet } from "react-router-dom";

export function Layout() {
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `px-3 py-2 rounded-md text-sm font-medium ${
      isActive
        ? "bg-slate-900 text-white"
        : "text-slate-700 hover:bg-slate-200"
    }`;

  return (
    <div className="min-h-full">
      <header className="border-b border-slate-200 bg-white">
        <nav className="mx-auto max-w-5xl flex items-center justify-between px-4 py-3">
          <h1 className="text-lg font-semibold tracking-tight">
            🔗 Shortlink
          </h1>
          <div className="flex gap-2">
            <NavLink to="/" end className={linkClass}>
              Create
            </NavLink>
            <NavLink to="/links" className={linkClass}>
              My Links
            </NavLink>
          </div>
        </nav>
      </header>
      <main className="mx-auto max-w-5xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
