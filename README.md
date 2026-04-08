# CareerPath MVP

## Структура
- `apps/api` — backend на FastAPI
- `apps/web` — frontend на Next.js App Router
- `infrastructure` — `docker-compose` окружение (Postgres + Redis)
- `docs` — продуктовые/технические контексты
- `packages` — общие UI/Config утилиты

## Быстрый запуск
1. Скопировать `.env.example` в `.env`, задать секреты/пароли и, при необходимости, ассеты.
2. Запуск `docker compose -f infrastructure/docker-compose.yml up --build` поднимет PostgreSQL, Redis, backend и frontend.
3. API доступен на `http://localhost:8000`, интерфейс — `http://localhost:3000`, админка пока stub.

## Backend
- Перейти в `apps/api`, установить зависимости `pip install .`
- Запуск `python -m app.main` или `uvicorn app.main:app --reload`
- Миграции: `alembic upgrade head`, сиды (скрипт `python -m app.scripts.seed`) подготавливают subjects/interests/professions.

## Frontend
- Перейти в `apps/web`, установить `npm install`, запуск `npm run dev` или `npm run build && npm run start`.
- Страницы: `/register`, `/test`, `/results`, `/dashboard`, данные подтягиваются из `NEXT_PUBLIC_API_URL`.

## Документация
- Контекст продукта, инженерии и дизайна — `docs/ai-context`
- PRD (Word) — `docs/product/CareerPath_PRD_v1.0.docx`
## Следующие шаги
- Реализация frontend flows и интеграция с рекомендательным API.
- Observability: structured logs, request_id, health/readiness, metrics, CI.
