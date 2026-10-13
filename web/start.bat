@echo off
cd /d "%~dp0.."
python -m drawing_compare serve --host 127.0.0.1 --port 8765
