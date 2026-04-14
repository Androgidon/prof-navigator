from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy import select

from app.db.base import async_session
from app.loaders.assessment_seed_config import ASSESSMENT_CATALOG_SEED
from app.models.assessment_catalog import AssessmentCatalog
from app.models.profession_catalog import ProfessionCatalog
from app.models.profession_matrix import ProfessionMatrix
from app.models.question_bank import QuestionBank

DIMENSIONS = [
    "analytical",
    "technical",
    "creative",
    "social",
    "helping",
    "leadership",
    "structured",
    "exploratory",
    "detail",
    "verbal",
    "quantitative",
    "practical",
]


class SeedValidationError(ValueError):
    pass


@dataclass
class EntitySummary:
    inserted: int = 0
    updated: int = 0
    skipped: int = 0


class AssessmentSeedLoader:
    def __init__(self, root: Path) -> None:
        self.root = root

    def validate_paths(self) -> Dict[str, Path]:
        required = {
            "assessment_prd": self.root / "assessment-engine-prd.md",
            "profession_catalog": self.root / "careerpath-100-professions.csv",
            "profession_matrix": self.root / "careerpath-profession-matrix-filled.csv",
            "question_blueprint": self.root / "careerpath-question-bank-blueprint.md",
            "question_template": self.root / "careerpath-question-bank-template.csv",
        }
        missing = [name for name, path in required.items() if not path.exists()]
        if missing:
            raise FileNotFoundError(f"Missing seed files: {', '.join(missing)}")
        return required

    async def load(self) -> Dict[str, Any]:
        paths = self.validate_paths()
        catalog_rows, matrix_versions = self._assessment_seed_rows()
        question_rows = self._load_question_rows(paths["question_template"])
        profession_rows = self._load_profession_rows(paths["profession_catalog"])
        matrix_rows = self._load_matrix_rows(paths["profession_matrix"], matrix_versions)
        self._validate_cross_references(catalog_rows, question_rows, profession_rows, matrix_rows)

        async with async_session() as session:
            catalog_summary = await self._upsert_assessment_catalog(session, catalog_rows)
            profession_summary, profession_slug_to_id = await self._upsert_profession_catalog(session, profession_rows)
            matrix_summary = await self._upsert_profession_matrix(session, matrix_rows, profession_slug_to_id)
            question_summary = await self._upsert_question_bank(session, question_rows)
            await session.commit()

        report = {
            "assessment_versions_loaded": len(catalog_rows),
            "questions_loaded": len(question_rows),
            "professions_loaded": len(profession_rows),
            "matrix_rows_loaded": len(matrix_rows),
            "assessment_catalog": catalog_summary.__dict__,
            "question_bank": question_summary.__dict__,
            "profession_catalog": profession_summary.__dict__,
            "profession_matrix": matrix_summary.__dict__,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return report

    def _assessment_seed_rows(self) -> Tuple[List[Dict[str, Any]], Set[str]]:
        seen: Set[str] = set()
        matrix_versions: Set[str] = set()
        rows: List[Dict[str, Any]] = []
        for item in ASSESSMENT_CATALOG_SEED:
            slug = item["slug"]
            if slug in seen:
                raise SeedValidationError(f"Duplicate assessment slug in config: {slug}")
            seen.add(slug)
            matrix_version_slug = item["matrix_version_slug"]
            matrix_versions.add(matrix_version_slug)
            question_mix = dict(item["question_mix_config_json"])
            question_mix["matrix_version_slug"] = matrix_version_slug
            rows.append(
                {
                    "slug": slug,
                    "title": item["title"],
                    "description": item["description"],
                    "target_items_count": item["target_items_count"],
                    "min_items_count": item["min_items_count"],
                    "max_items_count": item["max_items_count"],
                    "expected_duration_min": item["expected_duration_min"],
                    "is_active": item["is_active"],
                    "version": item["version"],
                    "scoring_config_json": item["scoring_config_json"],
                    "question_mix_config_json": question_mix,
                }
            )
        return rows, matrix_versions

    def _load_question_rows(self, path: Path) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        seen_keys: Set[Tuple[str, str]] = set()
        for row in self._read_csv(path):
            key = (row["assessment_version_slug"], row["question_id"])
            if key in seen_keys:
                raise SeedValidationError(f"Duplicate question key: {key}")
            seen_keys.add(key)
            options_json = self._parse_json(row["options_json"], f"question options {key}")
            if not isinstance(options_json, list):
                raise SeedValidationError(f"options_json must be a list for question {key}")
            weights_json = self._parse_json(row["weights_by_dimension_json"], f"question weights {key}")
            self._validate_weights(weights_json, f"question {key}")
            secondary_dimensions = [d for d in row["secondary_dimensions"].split("|") if d]
            for dim in secondary_dimensions:
                self._ensure_dimension(dim, f"question secondary dimension {key}")
            self._ensure_dimension(row["primary_dimension"], f"question primary dimension {key}")
            boundary_metadata_raw = row.get("boundary_metadata_json", "")
            boundary_metadata_json = None
            if boundary_metadata_raw and str(boundary_metadata_raw).strip():
                boundary_metadata_json = self._parse_json(boundary_metadata_raw, f"question boundary metadata {key}")
                if not isinstance(boundary_metadata_json, dict):
                    raise SeedValidationError(f"boundary_metadata_json must be object for question {key}")

            rows.append(
                {
                    "question_id": row["question_id"],
                    "assessment_version_slug": row["assessment_version_slug"],
                    "block": row["block"],
                    "subblock": row["subblock"] or None,
                    "question_type": row["question_type"],
                    "text": row["text"],
                    "options_json": options_json,
                    "primary_dimension": row["primary_dimension"],
                    "secondary_dimensions": secondary_dimensions,
                    "weights_by_dimension_json": weights_json,
                    "consistency_pair_id": row["consistency_pair_id"] or None,
                    "difficulty": row["difficulty"] or None,
                    "is_required": self._parse_bool(row["is_required"]),
                    "active_in_scoring": self._parse_bool(row.get("active_in_scoring", "true")),
                    "experiment_tag": row.get("experiment_tag") or None,
                    "experiment_mode": row.get("experiment_mode") or None,
                    "boundary_metadata_json": boundary_metadata_json,
                    "order_hint": int(row["order_hint"]),
                    "status": row["status"],
                    "question_purpose": row["question_purpose"],
                    "notes": row["notes"] or None,
                }
            )
        return rows

    def _load_profession_rows(self, path: Path) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        seen_slug: Set[str] = set()
        seen_external_id: Set[int] = set()
        for row in self._read_csv(path):
            slug = row["slug"]
            external_id = int(row["id"])
            if slug in seen_slug:
                raise SeedValidationError(f"Duplicate profession slug: {slug}")
            if external_id in seen_external_id:
                raise SeedValidationError(f"Duplicate profession external_id: {external_id}")
            seen_slug.add(slug)
            seen_external_id.add(external_id)
            rows.append(
                {
                    "external_id": external_id,
                    "slug": slug,
                    "title": row["title_ru"],
                    "cluster": row["cluster"],
                    "summary": row["summary_ru"],
                    "status": "active",
                }
            )
        return rows

    def _load_matrix_rows(self, path: Path, matrix_versions: Set[str]) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        seen: Set[Tuple[str, str]] = set()
        matrix_version_slug = sorted(matrix_versions)[0]
        for row in self._read_csv(path):
            slug = row["slug"]
            key = (slug, matrix_version_slug)
            if key in seen:
                raise SeedValidationError(f"Duplicate matrix key: {key}")
            seen.add(key)
            target_profile_json: Dict[str, int] = {}
            weights_json: Dict[str, float] = {}
            for dim in DIMENSIONS:
                target_key = f"target_{dim}"
                weight_key = f"weight_{dim}"
                if target_key not in row or weight_key not in row:
                    raise SeedValidationError(f"Missing required dimensions in matrix row: {slug}")
                target_profile_json[dim] = int(row[target_key])
                weights_json[dim] = float(row[weight_key])
            self._validate_weights(weights_json, f"matrix row {slug}")
            rows.append(
                {
                    "slug": slug,
                    "version_slug": matrix_version_slug,
                    "target_profile_json": target_profile_json,
                    "dimension_weights_json": weights_json,
                    "critical_dimensions": self._split_pipe(row["critical_dimensions"]),
                    "important_subjects": self._split_pipe(row["important_subjects"]),
                    "hobby_signals": self._split_pipe(row["hobby_signals"]),
                    "preferred_environments": self._split_pipe(row["preferred_environments"]),
                    "why_fit_template": row["why_fit_template"],
                    "first_steps_template": self._split_pipe(row["first_steps_template"]),
                    "notes": row["notes"] or None,
                    "matrix_version": 1,
                }
            )
        return rows

    def _validate_cross_references(
        self,
        catalog_rows: List[Dict[str, Any]],
        question_rows: List[Dict[str, Any]],
        profession_rows: List[Dict[str, Any]],
        matrix_rows: List[Dict[str, Any]],
    ) -> None:
        assessment_slugs = {row["slug"] for row in catalog_rows}
        matrix_versions = {
            row["question_mix_config_json"]["matrix_version_slug"] for row in catalog_rows
        }
        profession_slugs = {row["slug"] for row in profession_rows}

        for row in question_rows:
            if row["assessment_version_slug"] not in assessment_slugs:
                raise SeedValidationError(
                    f"Broken version reference in question {row['question_id']}: {row['assessment_version_slug']}"
                )
        for row in matrix_rows:
            if row["slug"] not in profession_slugs:
                raise SeedValidationError(f"Missing profession reference in matrix: {row['slug']}")
            if row["version_slug"] not in matrix_versions:
                raise SeedValidationError(f"Broken matrix version reference: {row['version_slug']}")

    async def _upsert_assessment_catalog(self, session: Any, rows: List[Dict[str, Any]]) -> EntitySummary:
        summary = EntitySummary()
        for row in rows:
            existing = await session.scalar(select(AssessmentCatalog).where(AssessmentCatalog.slug == row["slug"]))
            if not existing:
                session.add(AssessmentCatalog(**row))
                summary.inserted += 1
                continue
            if self._assign_if_changed(existing, row):
                summary.updated += 1
            else:
                summary.skipped += 1
        return summary

    async def _upsert_profession_catalog(self, session: Any, rows: List[Dict[str, Any]]) -> Tuple[EntitySummary, Dict[str, Any]]:
        summary = EntitySummary()
        slug_to_id: Dict[str, Any] = {}
        for row in rows:
            existing = await session.scalar(select(ProfessionCatalog).where(ProfessionCatalog.slug == row["slug"]))
            if not existing:
                entity = ProfessionCatalog(**row)
                session.add(entity)
                await session.flush()
                slug_to_id[row["slug"]] = entity.id
                summary.inserted += 1
                continue
            slug_to_id[row["slug"]] = existing.id
            if self._assign_if_changed(existing, row):
                summary.updated += 1
            else:
                summary.skipped += 1
        return summary, slug_to_id

    async def _upsert_profession_matrix(self, session: Any, rows: List[Dict[str, Any]], slug_to_id: Dict[str, Any]) -> EntitySummary:
        summary = EntitySummary()
        for row in rows:
            profession_id = slug_to_id[row["slug"]]
            payload = dict(row)
            payload.pop("slug")
            payload["profession_id"] = profession_id
            existing = await session.scalar(
                select(ProfessionMatrix).where(
                    ProfessionMatrix.profession_id == profession_id,
                    ProfessionMatrix.version_slug == row["version_slug"],
                )
            )
            if not existing:
                session.add(ProfessionMatrix(**payload))
                summary.inserted += 1
                continue
            if self._assign_if_changed(existing, payload):
                summary.updated += 1
            else:
                summary.skipped += 1
        return summary

    async def _upsert_question_bank(self, session: Any, rows: List[Dict[str, Any]]) -> EntitySummary:
        summary = EntitySummary()
        for row in rows:
            existing = await session.scalar(
                select(QuestionBank).where(
                    QuestionBank.assessment_version_slug == row["assessment_version_slug"],
                    QuestionBank.question_id == row["question_id"],
                )
            )
            if not existing:
                session.add(QuestionBank(**row))
                summary.inserted += 1
                continue
            if self._assign_if_changed(existing, row):
                summary.updated += 1
            else:
                summary.skipped += 1
        return summary

    @staticmethod
    def _assign_if_changed(entity: Any, payload: Dict[str, Any]) -> bool:
        changed = False
        for key, value in payload.items():
            if getattr(entity, key) != value:
                setattr(entity, key, value)
                changed = True
        return changed

    @staticmethod
    def _read_csv(path: Path) -> List[Dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as fp:
            return list(csv.DictReader(fp))

    @staticmethod
    def _parse_json(raw: str, context: str) -> Any:
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SeedValidationError(f"Malformed JSON in {context}: {exc}") from exc

    @staticmethod
    def _split_pipe(raw: str) -> List[str]:
        if not raw:
            return []
        return [item.strip() for item in raw.split("|") if item.strip()]

    @staticmethod
    def _parse_bool(raw: str) -> bool:
        normalized = raw.strip().lower()
        if normalized in {"true", "1", "yes"}:
            return True
        if normalized in {"false", "0", "no"}:
            return False
        raise SeedValidationError(f"Invalid boolean value: {raw}")

    @staticmethod
    def _ensure_dimension(value: str, context: str) -> None:
        if value not in DIMENSIONS:
            raise SeedValidationError(f"Unknown dimension '{value}' in {context}")

    def _validate_weights(self, weights: Any, context: str) -> None:
        if not isinstance(weights, dict):
            raise SeedValidationError(f"Invalid weights structure in {context}: expected object")
        for key, value in weights.items():
            self._ensure_dimension(key, context)
            if not isinstance(value, (int, float)):
                raise SeedValidationError(f"Invalid weight value for '{key}' in {context}")
