import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  BookOpen,
  PlayCircle,
  ShieldCheck,
  Download,
  ChevronRight,
} from "lucide-react";
import { cn } from "../../lib/utils";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/knowledge", label: "Knowledge Packs", icon: BookOpen },
  { to: "/generate", label: "Generate", icon: PlayCircle },
  { to: "/validate", label: "Validate", icon: ShieldCheck },
  { to: "/export", label: "Export", icon: Download },
];

export default function Sidebar() {
  return (
    <aside className="flex w-60 flex-col border-r border-surface-800/80 bg-surface-900/50 backdrop-blur">
      <div className="flex h-14 items-center gap-2.5 border-b border-surface-800/60 px-5">
        <div className="flex h-7 w-7 items-center justify-center rounded-md bg-gradient-to-br from-emerald-500 to-emerald-600 text-[10px] font-bold text-white shadow-lg shadow-emerald-500/20">
          C
        </div>
        <div className="leading-tight">
          <span className="font-display text-sm font-semibold text-surface-50">
            Compliance
          </span>
          <span className="font-display text-sm font-semibold text-emerald-400">
            AI
          </span>
        </div>
      </div>

      <nav className="flex-1 space-y-1 p-3">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              cn(
                "group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150",
                isActive
                  ? "bg-emerald-500/10 text-emerald-400 ring-1 ring-emerald-500/20"
                  : "text-surface-400 hover:bg-surface-800/60 hover:text-surface-200"
              )
            }
          >
            {({ isActive }) => (
              <>
                <item.icon className="h-4 w-4 flex-shrink-0" />
                <span>{item.label}</span>
                {isActive && (
                  <ChevronRight className="ml-auto h-3.5 w-3.5 text-emerald-400/60" />
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-surface-800/60 p-4">
        <div className="rounded-lg bg-surface-800/50 p-3 ring-1 ring-surface-700/50">
          <p className="text-[11px] font-medium uppercase tracking-wider text-surface-500">
            Standard
          </p>
          <p className="mt-1 text-sm font-medium text-surface-200">
            ISO/IEC 27001:2022
          </p>
          <p className="text-[11px] text-surface-500">93 controls loaded</p>
        </div>
      </div>
    </aside>
  );
}
