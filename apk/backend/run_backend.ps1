$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
python -m pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
