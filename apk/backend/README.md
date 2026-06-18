# Trend Cashout Backend

This service provides the API used by the Android app for balance checks and cashouts.

## Endpoints
- `GET /health`
- `GET /balance`
- `POST /cashout`

## Environment variables
Copy `.env.example` to your own environment and set:
- `STRIPE_SECRET_KEY`
- `STRIPE_CURRENCY`
- `APP_API_TOKEN`

## Run locally
Install dependencies and start the server:
```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Deploy on Render
1. Push this project to a Git repository.
2. In Render, create a new Web Service from the repo or use the repo-level `render.yaml`.
3. Set the runtime environment variables:
	- `STRIPE_SECRET_KEY`
	- `STRIPE_CURRENCY`
	- `APP_API_TOKEN`
4. Render will build from `backend/` and start the service with Uvicorn.
5. Copy the public Render URL into the Android app's backend settings.

## Example request
```bash
curl -H "Authorization: Bearer your_token" http://127.0.0.1:8000/balance
```

## Important
Keep the Stripe secret key on this backend only. The APK should use the backend URL and API token, not your Stripe credentials.
