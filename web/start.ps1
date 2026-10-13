$ErrorActionPreference = "Stop"
$webRoot = $PSScriptRoot
$projectRoot = Split-Path -Parent $webRoot
Set-Location -LiteralPath $projectRoot
python -m drawing_compare serve --host 127.0.0.1 --port 8765
