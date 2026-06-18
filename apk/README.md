# Trend Cashout Android App

This project is a Kivy-based Android client that packages the scraper and cashout workflow into an APK.

## Repository layout
The GitHub repo should keep the backend, Android app, and deployment files at the repository root:

- `backend/` for the Render-hosted API
- `main.py` for the Android app entry point
- `buildozer.spec` for APK builds
- `render.yaml` for Render deployment
- `build_apk.sh` for WSL or Linux APK builds
- `.gitignore` to keep secrets and build outputs out of GitHub

## What it does
- Scrapes a URL and extracts links.
- Opens a cashout center for balance checks and cashout requests.
- Stores backend settings locally on the device.
- Sends cashout actions to your backend API so the APK does not need your Stripe secret key.

## Backend contract
The app expects these endpoints on your server:
- `GET /balance`
- `POST /cashout`

Optional header:
- `Authorization: Bearer <token>`

Example cashout JSON body:
```json
{
  "amount": "1499.00",
  "method": "standard",
  "description": "Trend Data Payout"
}
```

## Backend service
The matching backend lives in [backend](backend).

Run it locally with:
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

Then set the Android app settings to your backend URL, such as `http://10.0.2.2:8000` for an emulator or your LAN IP for a phone on the same network.

If you deploy the backend on Render, use the public Render URL here instead of a local address.

## Build the APK
You usually need Linux or WSL for Buildozer.

1. Install system packages:
   - `python3`, `python3-pip`, `python3-venv`
   - `git`
   - `openjdk-17-jdk`
   - `zip`, `unzip`
   - Android build dependencies required by Buildozer
2. Install Buildozer:
   - `pip install buildozer cython`
3. Build the app:
   - `buildozer -v android debug`
4. The APK is usually placed in `bin/`.

If you prefer a shortcut, run `build_apk.sh` from Linux or WSL.

## Full workflow
1. Start the backend with `backend/run_backend.sh` or `backend/run_backend.ps1`.
2. Set the Android app backend URL to `http://10.0.2.2:8000` for an emulator or your LAN IP on a phone.
3. Build the APK.
4. Install the APK on the Android device.
5. Open the app, save the backend URL and token, then use the cashout center.

## Notes
- Direct browser automation like Playwright is not part of the Android build.
- For protected travel sites, scrape from a backend service instead of the phone.
- Keep secret keys and bank details on the backend, not inside the APK.
