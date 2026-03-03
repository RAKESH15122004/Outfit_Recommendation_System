# Run the backend server
# Usage: .\run.ps1
$env:PYTHONPATH = $PSScriptRoot
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
