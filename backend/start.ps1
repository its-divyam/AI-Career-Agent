$port = 8001
$procs = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
         Select-Object -ExpandProperty OwningProcess -Unique
if ($procs) {
    foreach ($p in $procs) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue }
    Write-Host "Killed processes on port $port"
    Start-Sleep -Seconds 2
}
Write-Host "Starting server on http://localhost:$port ..."
& "C:\Users\Divyam Garg\Desktop\AI career agent\venv\Scripts\python.exe" -m uvicorn app.main:app --reload --port $port
