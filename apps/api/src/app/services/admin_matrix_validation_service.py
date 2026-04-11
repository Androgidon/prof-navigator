from __future__ import annotations

from app.domains.assessment_scoring.profile_scoring_service import DIMENSIONS
from app.schemas.admin_matrix import MatrixValidationIssue, MatrixValidationResponse


class AdminMatrixValidationService:
    def validate(
        self,
        target_profile_json,
        dimension_weights_json,
        critical_dimensions,
        why_fit_template,
    ) -> MatrixValidationResponse:
        hard_errors: list[MatrixValidationIssue] = []
        warnings: list[MatrixValidationIssue] = []

        expected = set(DIMENSIONS)
        target_keys = set(target_profile_json.keys())
        weight_keys = set(dimension_weights_json.keys())

        missing_targets = sorted(expected - target_keys)
        missing_weights = sorted(expected - weight_keys)
        unknown_target_keys = sorted(target_keys - expected)
        unknown_weight_keys = sorted(weight_keys - expected)

        if missing_targets:
            hard_errors.append(
                MatrixValidationIssue(
                    severity="error",
                    code="missing_target_dimensions",
                    message=f"Missing target dimensions: {', '.join(missing_targets)}",
                )
            )
        if missing_weights:
            hard_errors.append(
                MatrixValidationIssue(
                    severity="error",
                    code="missing_weight_dimensions",
                    message=f"Missing weight dimensions: {', '.join(missing_weights)}",
                )
            )
        if unknown_target_keys:
            hard_errors.append(
                MatrixValidationIssue(
                    severity="error",
                    code="unknown_target_dimensions",
                    message=f"Unknown target dimensions: {', '.join(unknown_target_keys)}",
                )
            )
        if unknown_weight_keys:
            hard_errors.append(
                MatrixValidationIssue(
                    severity="error",
                    code="unknown_weight_dimensions",
                    message=f"Unknown weight dimensions: {', '.join(unknown_weight_keys)}",
                )
            )

        for key, value in target_profile_json.items():
            if not isinstance(value, (int, float)):
                hard_errors.append(
                    MatrixValidationIssue(
                        severity="error",
                        code="invalid_target_value_type",
                        message=f"target_profile_json[{key}] must be numeric",
                    )
                )
                continue
            if float(value) < 0 or float(value) > 100:
                hard_errors.append(
                    MatrixValidationIssue(
                        severity="error",
                        code="invalid_target_value_range",
                        message=f"target_profile_json[{key}] must be in range 0..100",
                    )
                )

        for key, value in dimension_weights_json.items():
            if not isinstance(value, (int, float)):
                hard_errors.append(
                    MatrixValidationIssue(
                        severity="error",
                        code="invalid_weight_value_type",
                        message=f"dimension_weights_json[{key}] must be numeric",
                    )
                )
                continue
            if float(value) < 0:
                hard_errors.append(
                    MatrixValidationIssue(
                        severity="error",
                        code="invalid_weight_value_range",
                        message=f"dimension_weights_json[{key}] must be >= 0",
                    )
                )

        invalid_critical = sorted(set(critical_dimensions) - expected)
        if invalid_critical:
            hard_errors.append(
                MatrixValidationIssue(
                    severity="error",
                    code="invalid_critical_dimensions",
                    message=f"critical_dimensions contains unknown values: {', '.join(invalid_critical)}",
                )
            )

        if not why_fit_template.strip():
            hard_errors.append(
                MatrixValidationIssue(
                    severity="error",
                    code="empty_why_fit_template",
                    message="why_fit_template must be non-empty",
                )
            )

        total_checks = 4
        completed_checks = 0
        if not missing_targets and not unknown_target_keys:
            completed_checks += 1
        if not missing_weights and not unknown_weight_keys:
            completed_checks += 1
        if not invalid_critical:
            completed_checks += 1
        if why_fit_template.strip():
            completed_checks += 1

        completeness_score = int(round((completed_checks / total_checks) * 100))

        if completeness_score < 100:
            warnings.append(
                MatrixValidationIssue(
                    severity="warning",
                    code="incomplete_matrix",
                    message=f"Matrix completeness is {completeness_score}%",
                )
            )

        return MatrixValidationResponse(
            valid=len(hard_errors) == 0,
            hard_errors=hard_errors,
            warnings=warnings,
            completeness_score=completeness_score,
        )
