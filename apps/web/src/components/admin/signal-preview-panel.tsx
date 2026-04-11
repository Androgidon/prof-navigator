"use client";

import { useState } from "react";
import { adminFetch } from "@/lib/admin-api";

type SignalPreviewPanelProps = {
  questionType: string;
  optionsJson: Array<{ key: string; label: string; weights_by_dimension?: Record<string, number> }>;
  weightsByDimension: Record<string, number>;
};

export function SignalPreviewPanel({ questionType, optionsJson, weightsByDimension }: SignalPreviewPanelProps) {
  const [answer, setAnswer] = useState("{}");
  const [signals, setSignals] = useState<Record<string, { score: number; relevance: number }>>({});
  const [notes, setNotes] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const runPreview = async () => {
    setLoading(true);
    setError(null);
    try {
      const parsed = JSON.parse(answer || "{}");
      const result = await adminFetch<{ signals: Record<string, { score: number; relevance: number }>; notes: string[] }>(
        "/admin/questions/preview-signal",
        {
          method: "POST",
          body: JSON.stringify({
            question_type: questionType,
            options_json: optionsJson,
            weights_by_dimension_json: weightsByDimension,
            answer: parsed,
          }),
        }
      );
      setSignals(result.signals || {});
      setNotes(result.notes || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Preview failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-preview-card">
      <h3>Signal Preview</h3>
      <p className="admin-help">Введите sample answer JSON, например {"{\"value\": 80}"} или {"{\"key\": \"a\"}"}.</p>
      <textarea className="admin-textarea" value={answer} onChange={(e) => setAnswer(e.target.value)} rows={4} />
      <button type="button" className="admin-btn admin-btn-primary" onClick={runPreview} disabled={loading}>
        {loading ? "Проверка..." : "Preview Signal"}
      </button>
      {error && <div className="admin-error">{error}</div>}
      {Object.keys(signals).length > 0 && (
        <div className="admin-signal-table">
          {Object.entries(signals).map(([dim, value]) => (
            <div key={dim} className="admin-signal-row">
              <strong>{dim}</strong>
              <span>score: {value.score.toFixed(1)}</span>
              <span>relevance: {value.relevance.toFixed(2)}</span>
            </div>
          ))}
        </div>
      )}
      {notes.length > 0 && <div className="admin-help">{notes.join("; ")}</div>}
    </div>
  );
}
