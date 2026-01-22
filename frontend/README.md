# Frontend (Vue 3)

This folder contains the Vue 3 + TypeScript frontend for API Models Connect.

## Requirements

- Node.js 18+

## Install

```bash
cd frontend
npm install
```

## Configure API Origin

By default the frontend calls the backend at `http://127.0.0.1:8000`.

Optionally override via:

- `frontend/.env.development` (`VITE_API_ORIGIN=...`)
- or an environment variable: `VITE_API_ORIGIN`

## Run (Dev)

```bash
cd frontend
npm run dev
```

Frontend: `http://127.0.0.1:5173`

## Build

```bash
cd frontend
npm run build
```

## Routes

- `/`: landing (product intro + quick run section)
- `/run`: focused Task Runner (upload images -> pick model -> run)
- `/dashboard`, `/models`, `/prompts`, `/history`, `/settings`: console modules

## Design System Notes

- Global styles: `frontend/src/style.css` (glassmorphism / light)
- Generated references: `frontend/design-system/api-models-connect/`

