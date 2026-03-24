# skladprobot miniapp

## Env vars (Vercel)
- `JWT_SECRET` — random long secret
- `TELEGRAM_BOT_TOKEN` — bot token (for initData validation)
- `POSTGRES_URL` / `POSTGRES_URL_NON_POOLING` — Vercel Postgres

## Setup
1. Create Vercel Postgres database in the project.
2. Add env vars above.
3. Deploy.

## Local dev
```
cd miniapp
npm install
npm run dev
```
