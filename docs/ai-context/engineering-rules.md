CareerPath – Engineering Rules   
Ты отвечаешь за инженерную реализацию проекта CareerPath.

Все технические решения должны быть:  
\- актуальными  
\- поддерживаемыми  
\- production-minded  
\- без лишней сложности  
\- без устаревших паттернов

\#\# 1\. Общие инженерные принципы

Приоритеты:  
1\. correctness  
2\. maintainability  
3\. observability  
4\. security  
5\. speed of MVP delivery

Нельзя:  
\- тащить ненужные технологии  
\- использовать устаревшие паттерны  
\- переусложнять MVP  
\- строить микросервисы на старте  
\- оставлять ключевую бизнес-логику внутри route handlers  
\- писать большие неструктурированные файлы без доменной границы

Нужно:  
\- modular monolith  
\- bounded contexts  
\- predictable architecture  
\- typed code  
\- migration-first database workflow  
\- observability from day one  
\- tests for critical business logic

\#\# 2\. Обязательный стек

Backend:  
\- Python 3.13  
\- FastAPI  
\- Pydantic v2  
\- SQLAlchemy 2.x  
\- Alembic  
\- PostgreSQL 16+  
\- Redis  
\- pytest  
\- httpx  
\- ruff  
\- mypy или pyright

Frontend:  
\- Next.js App Router  
\- React 19  
\- TypeScript strict mode  
\- Tailwind CSS  
\- shadcn/ui  
\- React Hook Form \+ Zod при необходимости  
\- next-intl или зрелая i18n library  
\- Playwright для критичных e2e

Infra / DX:  
\- Docker  
\- docker-compose  
\- .env.example  
\- seed scripts  
\- OpenAPI docs  
\- README с run instructions

\#\# 3\. Правила по библиотекам и версиям

Использовать только актуальные стабильные линии библиотек.

Правила:  
\- FastAPI: актуальная стабильная линия  
\- Pydantic: только v2  
\- SQLAlchemy: только 2.x style  
\- Alembic: актуальная стабильная ветка  
\- Next.js: только App Router  
\- React: актуальная stable line  
\- primary auth не строить на beta auth stack на фронте  
\- backend auth должен жить в FastAPI

Если в lock/install виден более новый patch-релиз в той же стабильной ветке — допустимо использовать его, если это не ломает совместимость.

\#\# 4\. Структура проекта

Предпочтительная структура:

/apps  
  /api  
  /web

/packages  
  /ui  
  /config

/infrastructure  
  docker-compose.yml  
  env examples  
  proxy config if needed

/docs  
  architecture.md  
  api.md  
  domain-model.md  
  adr/

Если packages пока не нужны — не плодить их искусственно.

\#\# 5\. Архитектурный стиль

Использовать modular monolith.

Bounded contexts:  
1\. Identity & Access  
2\. Student Profile  
3\. Assessment / Test Engine  
4\. Recommendation Engine  
5\. Career Content  
6\. Favorites & Dashboard  
7\. Admin & Audit  
8\. Analytics Events

Каждый контекст должен иметь:  
\- models  
\- schemas  
\- services  
\- repositories or persistence layer  
\- routers/controllers  
\- tests

Нельзя смешивать всё в один “utils/service.py”.

\#\# 6\. Backend rules

\#\#\# FastAPI  
Использовать:  
\- APIRouter по модулям  
\- Depends для dependency injection  
\- lifespan/startup patterns корректно  
\- request/response schemas через Pydantic  
\- бизнес-логику в services  
\- repositories/persistence отдельно от API слоя

\#\#\# Security  
\- JWT access \+ refresh flow  
\- rate limiting на login  
\- secure password hashing  
\- account deletion flow  
\- RBAC  
\- sensitive fields redaction in logs

\#\#\# API  
\- версионировать API, например \`/api/v1\`  
\- использовать стабильные response contracts  
\- ошибки приводить к понятному формату  
\- OpenAPI должен быть чистым и полезным

\#\#\# Async/sync  
\- не смешивать хаотично sync и async  
\- если используешь async SQLAlchemy stack — использовать его последовательно  
\- если sync stack — не делать части приложения async “для красоты”

\#\# 7\. Data and persistence rules

Использовать PostgreSQL как основную БД.

Обязательные сущности:  
\- User  
\- RefreshToken или эквивалентная безопасная persistence-модель  
\- UserProfile  
\- Subject  
\- SubjectGrade  
\- Interest  
\- Test  
\- TestBlock  
\- TestQuestion  
\- TestAnswerOption  
\- TestSession  
\- TestResponse  
\- TestResult  
\- Profession  
\- ProfessionIndustry  
\- ProfessionSubjectRequirement  
\- ProfessionSkill  
\- ProfessionRelated  
\- ProfessionVector  
\- Recommendation  
\- RecommendationExplanationFactor  
\- UserFavorite  
\- RecommendationFeedback  
\- AdminAuditLog

\#\#\# SQLAlchemy rules  
\- typed ORM models  
\- declarative style 2.x  
\- миграции через Alembic с первого дня  
\- не хранить queryable сущности в opaque JSON без причины  
\- JSONB использовать только там, где это оправдано:  
  \- explanations  
  \- answer snapshots  
  \- analytics metadata

\#\#\# Recommendation persistence  
\- recommendation engine должен быть отдельно тестируемым  
\- profession\_vector должен иметь детерминированную структуру  
\- не привязывать MVP к pgvector без явной необходимости

\#\# 8\. Auth rules

Primary auth должен быть на backend.

Нужно:  
\- email/password auth  
\- refresh token flow  
\- current user endpoint  
\- logout / revoke refresh  
\- password reset flow architecture  
\- feature-flag-ready Google OAuth integration, если credentials недоступны

Не делать:  
\- критическую auth-архитектуру на beta frontend auth framework  
\- insecure localStorage-only auth flow  
\- смешанный хаос из cookies и bearer tokens без модели

\#\# 9\. Frontend rules

\#\#\# Next.js  
Использовать:  
\- App Router  
\- server components по умолчанию  
\- client components только для интерактивных сценариев  
\- route groups/layouts  
\- API base URL через env/config

\#\#\# Forms  
\- typed validation  
\- reusable form primitives  
\- clean error handling  
\- optimistic UX только там, где это действительно уместно

\#\#\# Data fetching  
\- не тянуть всё через client-side fetch без причины  
\- где возможно, использовать server-first rendering  
\- TanStack Query применять только там, где он реально нужен

\#\#\# UI state  
Для каждого пользовательского сценария учитывать:  
\- loading  
\- empty  
\- error  
\- success

\#\# 10\. Recommendation engine rules

Recommendation engine — ключевая бизнес-логика.

Нужно реализовать:  
\- нормализацию входных сигналов  
\- unified user vector  
\- profession vector  
\- cosine similarity  
\- weighted boosting  
\- regional relevance bonus  
\- score 0–100  
\- top 15 ranking  
\- explanation factors generation

Источник данных и веса:  
\- psychological test vector: 40%  
\- interest/activity answers: 25%  
\- grades: 15%  
\- profile interests: 10%  
\- regional relevance: 10%

Обязательно:  
\- pure service layer  
\- unit tests  
\- fixtures  
\- reproducible seed data  
\- human-readable explanation output

\#\# 11\. Test engine rules

Тест должен поддерживать:  
\- 30–35 вопросов  
\- блочную структуру  
\- прогресс  
\- возобновление  
\- immutable answers после submit  
\- расчёт итогового профиля

Типы вопросов:  
\- Likert  
\- single choice  
\- pair choice  
\- ranking

Не делать:  
\- тест как один giant JSON blob без модели  
\- хрупкую логику без persistence слоя

\#\# 12\. Admin rules

Admin — часть MVP.

Admin должен поддерживать:  
\- CRUD профессий  
\- CRUD вопросов теста  
\- CRUD profession vectors  
\- просмотр feedback  
\- список пользователей в безопасном объёме  
\- audit logging

Admin должен быть:  
\- role-protected  
\- утилитарным  
\- предсказуемым  
\- без лишних украшений

\#\# 13\. Observability and analytics

Нужно с первого дня:  
\- structured JSON logs  
\- request\_id / correlation\_id  
\- hooks для Sentry  
\- health endpoint  
\- readiness endpoint  
\- аналитические события

Минимальные события:  
\- signup\_started  
\- signup\_completed  
\- login\_completed  
\- profile\_started  
\- profile\_completed  
\- test\_started  
\- test\_question\_answered  
\- test\_paused  
\- test\_completed  
\- recommendations\_viewed  
\- profession\_card\_opened  
\- profession\_favorited  
\- recommendation\_feedback\_submitted  
\- dashboard\_viewed

\#\# 14\. Testing rules

Обязательно покрывать тестами:  
\- recommendation engine  
\- auth critical paths  
\- test session logic  
\- persistence-critical flows  
\- main API contracts  
\- critical UI flows e2e

Минимум:  
\- unit tests  
\- integration tests backend  
\- e2e smoke tests frontend

\#\# 15\. Code quality rules

Нужно:  
\- typed code  
\- linting  
\- formatting  
\- predictable naming  
\- short focused modules  
\- explicit config  
\- no dead abstractions

Не нужно:  
\- giant god classes  
\- giant files without structure  
\- over-engineered patterns  
\- premature generic frameworks inside app

\#\# 16\. Documentation rules

Создать и поддерживать:  
\- README.md  
\- docs/architecture.md  
\- docs/domain-model.md  
\- docs/api.md  
\- docs/adr/\* где есть важные инженерные решения  
\- env examples  
\- seed instructions

Документация должна быть краткой, но реально полезной.

\#\# 17\. AI-agent behavior rules

Когда реализуешь новую задачу:  
1\. сначала прочитай product context  
2\. затем engineering rules  
3\. затем design rules, если задача касается UI  
4\. затем task brief  
5\. определи impacted modules  
6\. не ломай существующую архитектуру  
7\. переиспользуй существующие компоненты и сервисы  
8\. добавь тесты и документацию, если это влияет на контракт или бизнес-логику

Если решение требует выбора:  
\- выбирай более простой и поддерживаемый вариант  
\- не добавляй новую библиотеку, если задача решается текущим стеком  
