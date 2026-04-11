"use client";

import { adminFetch } from "@/lib/admin-api";

type MatrixPreviewPanelProps = {
  cluster: string;
  profileScores: Record<string, number>;
  targetProfile: Record<string, number>;
  weights: Record<string, number>;
  criticalDimensions: string[];
  onResult: (result: {
    base_similarity: number;
    critical_penalty: number;
    strong_fit_effect: number;
    admissibility_effect: number;
    admissible: boolean;
    final_score: number;
  } | null, error: string | null) => void;
};

export function MatrixPreviewPanel({
  cluster,
  profileScores,
  targetProfile,
  weights,
  criticalDimensions,
  onResult,
}: MatrixPreviewPanelProps) {
  return (
    <div className="admin-editor-box">
      <div className="admin-editor-box-title">Preview</div>
      <button
        type="button"
        className="admin-btn admin-btn-primary"
        onClick={async () => {
          try {
            const result = await adminFetch<{
              base_similarity: number;
              critical_penalty: number;
              strong_fit_effect: number;
              admissibility_effect: number;
              admissible: boolean;
              final_score: number;
            }>("/admin/matrix/preview", {
              method: "POST",
              body: JSON.stringify({
                profile_scores: profileScores,
                target_profile_json: targetProfile,
                dimension_weights_json: weights,
                critical_dimensions: criticalDimensions,
                cluster,
              }),
            });
            onResult(result, null);
          } catch (err) {
            onResult(null, err instanceof Error ? err.message : "Preview error");
          }
        }}
      >
        Preview Match
      </button>
    </div>
  );
}
