# GitHub Layout for Render

Use this exact repository layout at the root of your GitHub repo:

```text
/
├─ backend/
│  ├─ app.py
│  ├─ requirements.txt
│  ├─ README.md
│  ├─ run_backend.sh
│  ├─ run_backend.ps1
│  └─ .env.example
├─ main.py
├─ buildozer.spec
├─ build_apk.sh
├─ requirements.txt
├─ render.yaml
├─ README.md
└─ .gitignore
```

## What goes where
- `backend/` contains the FastAPI service that Render deploys.
- `main.py` is the Android app entry point.
- `buildozer.spec` is the Android build config.
- `render.yaml` tells Render how to build and start the backend.
- `README.md` explains how to run both parts.
- `.gitignore` keeps caches, build outputs, and secrets out of GitHub.

## Push flow
1. Put this whole folder into a Git repo.
2. Commit the files.
3. Push to GitHub.
4. Connect the GitHub repo to Render.
