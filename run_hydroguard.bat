@echo off
cd /d C:\Users\harsh\OneDrive\Documents\harsha\Project\HYDROGUARD

call .venv\Scripts\activate.bat

python -m backend.app.ingestion.weather.citywide >> logs\hydroguard_refresh.log 2>&1