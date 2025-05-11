@echo off
echo Sending positive review...
curl -X POST http://127.0.0.1:5000/predict ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"This movie was absolutely fantastic! I loved it.\"}"

echo.
echo Sending negative review...
curl -X POST http://127.0.0.1:5000/predict ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"This movie was terrible and a complete waste of time.\"}"

pause
