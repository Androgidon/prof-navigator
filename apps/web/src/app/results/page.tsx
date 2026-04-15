import { Suspense } from "react";
import ResultsPageClient from "./results-page-client";

export const dynamic = "force-dynamic";

export default function ResultsPage() {
  return (
    <Suspense fallback={<div className="loading-state">Загружаем результаты...</div>}>
      <ResultsPageClient />
    </Suspense>
  );
}
