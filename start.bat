@echo off
echo Starting ZentrumHub Documentation Assistant API...
echo.
echo Swagger UI will be available at: http://localhost:8000/docs
echo ReDoc will be available at: http://localhost:8000/redoc
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
