import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";

export default function AppLayout() {
  return (
    <div className="flex h-screen bg-surface-950">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <div className="bg-grid min-h-full">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
