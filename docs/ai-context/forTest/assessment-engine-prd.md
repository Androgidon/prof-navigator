Нужно реализовать в существующем проекте CareerPath полноценный assessment engine для профориентационного тестирования школьников.

Работаем строго в режиме:
**assessment engine MVP implementation**
Без большого refactor unrelated parts of the product.

## Главная задача
Нужно построить модуль, который:
1. проводит профориентационный тест
2. строит профиль пользователя по 12 шкалам
3. сравнивает профиль с каталогом из 100 профессий
4. выдаёт топ-10–15 наиболее подходящих профессий
5. объясняет, почему они подходят
6. показывает, какие предметы и навыки стоит развивать

## Версии теста
Нужно поддержать 2 версии:
- `express_v1`
- `deep_v1`

### express_v1
- 42 вопроса / элементов (допустимо 38–48)
- 7–10 минут
- result: top-10 professions + short explanation

### deep_v1
- 100 элементов (допустимо 96–110)
- 18–30 минут
- result: top-10–15 professions + detailed explanation + stronger output

## 12 шкал профиля
Использовать такие dimensions:
- analytical
- technical
- creative
- social
- helping
- leadership
- structured
- exploratory
- detail
- verbal
- quantitative
- practical

Все scores должны рассчитываться в диапазоне 0–100.

## Источники сигнала
Для каждой шкалы использовать 4 источника:
- self-report / preference questions
- situational / forced-choice
- subjects + hobbies
- mini tasks / calibration

Рекомендуемая базовая модель:
- 40% self-report
- 20% situational/forced-choice
- 20% subjects+hobbies
- 20% tasks/calibration

## Структура express test
Блоки:
1. interests and task preferences — 8
2. subjects — 8
3. hobbies — 6
4. work style / environment — 8
5. behavioral situations — 6
6. mini cognitive tasks — 6

## Структура deep test
Блоки:
1. deep interests — 14
2. subject profile — 14
3. hobbies and real activities — 10
4. work style / environment — 12
5. behavioral situations — 12
6. motivation / priorities — 10
7. mini cognitive tasks — 12
8. consistency / cross-check — 8
9. strengths self-perception — 8

## Каталог профессий
Использовать первые 100 профессий, распределённые по 10 кластерам:
1. IT и цифровые технологии
2. Дизайн, креатив, медиа
3. Маркетинг, коммуникации, контент
4. Бизнес, управление, продажи
5. Финансы, аналитика, право
6. Образование, психология, помощь людям
7. Медицина, здоровье, бионауки
8. Инженерия, производство, строительство
9. Наука, исследования, экология
10. Логистика, операции, сервис, гос/соцсфера

## Profession matrix
Для каждой профессии нужно поддержать:
- target_profile (12 dimensions)
- dimension_weights
- critical_dimensions
- important_subjects
- hobby_signals
- preferred_environments

## Match logic
Для каждой profession:
1. считать similarity по каждой dimension
2. умножать на weights
3. нормализовать в base match
4. применять penalties по critical_dimensions
5. применять небольшие bonuses за subjects/hobbies/environment fit
6. выдавать final match score 0–100

## Confidence и consistency
Система должна считать:
- consistency score
- confidence level (high / medium / low)

## Backend domain model
Нужно реализовать сущности:
- AssessmentCatalog
- QuestionBank
- ProfessionCatalog
- ProfessionMatrix
- AssessmentSession
- AssessmentResult

## Recommended backend modules
Разбить логику на модули:
- assessment_catalog
- question_bank
- assessment_sessions
- assessment_scoring
- profession_catalog
- profession_matrix
- assessment_results

И сервисы:
- QuestionSelectionService
- AssessmentScoringService
- ProfessionMatchService
- ResultExplanationService

## API
Нужны endpoints:
- POST /assessments/start
- POST /assessments/{session_id}/answer
- POST /assessments/{session_id}/complete
- GET /assessments/results/{result_id}

## Result output
Result payload должен включать:
- profile_scores
- profile_summary
- top_strengths
- work_style
- recommendations
- next_steps
- confidence

## Recommendation entry
Для каждой recommended profession:
- slug
- title
- cluster
- match_score
- summary
- why_fit
- important_subjects
- first_steps

## Важные принципы
- система должна быть explainable
- scoring должен быть deterministic и testable
- content должен быть data-driven, а не захардкожен в UI
- express и deep должны использовать одну core model
- не делать personality quiz вместо assessment engine
- не выдавать “одну идеальную профессию”

## Что не делать
- не делать ML recommender на этом этапе
- не делать академически сложную psychometric platform
- не строить adaptive testing engine для MVP
- не refactor unrelated modules

## Этапы реализации
1. assessment domain scaffolding
2. question bank structure
3. profession catalog + matrix structure
4. express scoring pipeline
5. result generation
6. deep assessment support
7. richer explanation and confidence

## Перед кодом обязательно покажи
1. proposed repo/module structure
2. backend entities/schemas
3. storage strategy for question bank and matrix
4. scoring pipeline structure
5. express/deep assembly rules
6. result payload contract
7. phased implementation plan

Только после этого переходи к реализации.