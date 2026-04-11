from __future__ import annotations


class ResultExplanationService:
    def build_top_strengths(self, profile_scores: dict[str, int], starter_dataset_limited: bool):
        sorted_dims = sorted(profile_scores.items(), key=lambda item: (-item[1], item[0]))
        strengths = []
        for name, score in sorted_dims[:3]:
            strengths.append(
                {
                    "dimension": name,
                    "score": score,
                    "preliminary": starter_dataset_limited,
                }
            )
        return strengths

    def build_work_style(self, profile_scores: dict[str, int], starter_dataset_limited: bool):
        axes = {
            "structured_vs_exploratory": profile_scores.get("structured", 50)
            - profile_scores.get("exploratory", 50),
            "social_vs_analytical": profile_scores.get("social", 50)
            - profile_scores.get("analytical", 50),
        }
        return {
            "axes": axes,
            "preliminary": starter_dataset_limited,
            "message": "Preliminary work style signal from starter question set."
            if starter_dataset_limited
            else "Work style extracted from assessment evidence.",
        }

    def build_next_steps(self, starter_dataset_limited: bool):
        return {
            "starter_dataset_limited": starter_dataset_limited,
            "actions": [
                "Complete a fuller question bank for stronger recommendations.",
                "Review top strengths with a mentor or counselor.",
                "Try one practical first step from top professions.",
            ],
        }
