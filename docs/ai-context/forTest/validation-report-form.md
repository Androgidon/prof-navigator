Нужно вернуть результат массовой synthetic validation в строгом формате отчёта.

## Формат отчёта обязателен

---

# 1. Executive Summary

Кратко покажи:

- сколько профилей прогнано: `50`
- сколько дали product-sane результат
- success rate в %
- partial mismatch count
- strong mismatch count
- какие 3 кластера чаще всего доминировали
- какие 3 кластера чаще всего выступали fallback
- общий вердикт:
  - good
  - medium / needs tuning
  - poor / requires major recalibration

---

# 2. Validation Table (50 profiles)

Для каждого профиля верни таблицу в таком формате:

| # | Profile Name | Group | Intended Strong Dimensions | Expected Top Clusters | Actual Top Clusters | Top-5 Professions | Confidence | Verdict | Notes |
|---|--------------|-------|----------------------------|----------------------|--------------------|------------------|------------|---------|-------|

### Требования к колонкам:
- **Profile Name** — короткое имя synthetic profile
- **Group** — analytical/technical, creative, helping и т.д.
- **Intended Strong Dimensions** — 3–5 ожидаемых сильных измерений
- **Expected Top Clusters** — какие кластеры должны быть в топе
- **Actual Top Clusters** — какие кластеры реально попали в топ
- **Top-5 Professions** — реальные top-5 профессий
- **Confidence** — score + level
- **Verdict**:
  - `OK`
  - `Partial mismatch`
  - `Strong mismatch`
- **Notes** — короткое объяснение, если есть mismatch

---

# 3. Cluster Distribution Summary

Отдельным блоком покажи:

## 3.1 Top-3 cluster frequency
Таблица:

| Cluster | Count in Top-3 | % of profiles |
|--------|-----------------|---------------|

## 3.2 Top-5 cluster frequency
Таблица:

| Cluster | Count in Top-5 | % of profiles |
|--------|-----------------|---------------|

## 3.3 Fallback cluster detection
Покажи:
- какие кластеры слишком часто попадают в top-3 / top-5
- какие кластеры оказываются в рекомендациях там, где их не ожидали
- какие кластеры выглядят как generic fallback families

---

# 4. Dimension Behavior Summary

Покажи по dimension-level диагностике:

| Dimension | Intended Behavior | Observed Behavior | Verdict | Notes |
|----------|-------------------|------------------|---------|------|

Нужно оценить:
- какие dimensions недооцениваются
- какие переоцениваются
- какие dimensions “сжимаются”
- какие слишком легко становятся доминирующими
- какие плохо различаются друг от друга

Особенно обрати внимание на:
- helping
- social
- verbal
- technical
- analytical
- structured
- detail
- quantitative
- practical
- exploratory

---

# 5. Confidence Quality Summary

Покажи отдельно:

- сколько результатов получили `high`
- сколько `medium`
- сколько `low`
- были ли случаи, где confidence высокое, а рекомендации выглядят слабыми
- были ли случаи, где confidence слишком низкое при хорошем попадании

Таблица:

| Case Type | Count | Notes |
|-----------|------|-------|
| High confidence + good fit |  |  |
| High confidence + weak fit |  |  |
| Medium confidence + good fit |  |  |
| Low confidence + ambiguous fit |  |  |

---

# 6. Root Cause Analysis

Нужен отдельный аналитический блок:

## 6.1 Scoring issues
Где current scoring logic даёт искажения.

## 6.2 Question bank issues
Какие профили плохо различаются из-за вопросов.

## 6.3 Matrix issues
Какие profession clusters or rows слишком широкие / слишком слабые / слишком жёсткие.

## 6.4 Confidence issues
Где confidence formula misleading.

---

# 7. Tuning Recommendations

Нужно не просто сказать “нужно улучшить”, а дать структурированный план.

Раздели рекомендации на 4 блока:

## 7.1 High priority
Что нужно менять в первую очередь.

## 7.2 Medium priority
Что улучшит качество, но не критично.

## 7.3 Low priority
Что можно делать позже.

## 7.4 Do not change yet
Что пока трогать не стоит, чтобы не сломать уже работающие части.

---

# 8. Final Verdict

В конце дай короткое заключение в формате:

### Current quality level
- Good / Medium / Weak

### Estimated readiness
- ready for pilot
- pilot only after recalibration
- not ready yet

### Main blockers
- 3–5 ключевых блокеров

### Recommended next step
- tuning scoring
- tuning matrix
- question bank rewrite
- confidence recalibration
- or “acceptable as MVP”

---

## Дополнительные требования

### 1. Никакой воды
Нужен компактный, аналитический, полезный отчёт.

### 2. Не смешивать симптомы и причины
Нужно явно разделять:
- observed mismatch
- likely root cause

### 3. Не делать random tuning до отчёта
Сначала validation.
Потом выводы.
Потом tuning recommendations.

### 4. Если используются synthetic answer generation rules
Кратко опиши их в начале отчёта.

### 5. Если по каким-то профилям есть спорная граница
Например helping vs marketing,
обозначь это как `acceptable boundary case`, а не как явную ошибку, если это действительно borderline.