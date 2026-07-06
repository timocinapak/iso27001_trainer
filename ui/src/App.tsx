import { Routes, Route, Navigate } from "react-router-dom";
import AppLayout from "./components/layout/AppLayout";
import DashboardPage from "./components/dashboard/DashboardPage";
import KnowledgePage from "./components/knowledge/KnowledgePage";
import PackDetail from "./components/knowledge/PackDetail";
import GenerationPage from "./components/generation/GenerationPage";
import ValidationPage from "./components/validation/ValidationPage";
import ExportPage from "./components/export/ExportPage";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/knowledge" element={<KnowledgePage />} />
        <Route path="/knowledge/:standard" element={<PackDetail />} />
        <Route path="/generate" element={<GenerationPage />} />
        <Route path="/validate" element={<ValidationPage />} />
        <Route path="/export" element={<ExportPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
