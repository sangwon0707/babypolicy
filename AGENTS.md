# Repository Guidelines

## Project Structure & Module Organization
- `frontend/`: Next.js (App Router) TypeScript UI, Tailwind CSS. Key routes under `app/` (e.g., `app/me`, `app/community`). Shared code in `components/`, `contexts/`, `lib/`.
- `backend/`: FastAPI app. Entrypoint `backend/main.py`; API routers in `backend/routers/` (auth, user, calendar, chat, community). Data access lives in `backend/crud.py`; schemas in `backend/schemas.py`.
- `data/`, `public/`, and logs are auxiliary assets; avoid committing secrets.

## Build, Test, and Development Commands
- Frontend
  - `cd frontend && npm install`
  - `npm run dev`: Start Next.js dev server (default on `http://localhost:3000`).
  - `npm run build && npm start`: Production build and run.
  - `npm run lint`: Run ESLint.
- Backend
  - `cd backend && pip install -r requirements.txt`
  - `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`: Start API (CORS expects `FRONTEND_URL`).

## Coding Style & Naming Conventions
- TypeScript/React: 2-space indent; functional components; hooks in `use*`; file names `kebab-case.tsx` under `app/` routes. Run `npm run lint` before PRs.
- Python: PEP 8; snake_case for functions/vars, PascalCase for classes; routers named by domain (e.g., `calendar.py`). Keep handlers thin; delegate to `crud.py`.
- API paths are prefixed (`/api/auth`, `/api/user`, `/api/calendar`, etc.).

## Testing Guidelines
- No formal unit test suite yet. Validate via:
  - Frontend: manual flows (login, /me calendar, community) and browser console for errors.
  - Backend: exercise endpoints with curl/Postman; check 2xx/4xx and response shapes.
- Add small, focused tests where frameworks are present; name tests after feature (e.g., `calendar_events.spec.ts` or `test_calendar.py`).

## Commit & Pull Request Guidelines
- Commits: imperative, concise subject (<=72 chars), scope where helpful.
  - Examples: `fix(me): show next 3 events`, `feat(calendar): add full list page`.
- PRs: include purpose, screenshots or logs, steps to reproduce/verify, and linked issues.
- Keep changes minimal and scoped; avoid unrelated refactors.

## Security & Configuration Tips
- Frontend config: `frontend/.env.local` (`NEXT_PUBLIC_API_URL`).
- Backend config: `backend/.env` (`SECRET_KEY`, `FRONTEND_URL`, DB creds). Never commit secrets; use examples when documenting.
