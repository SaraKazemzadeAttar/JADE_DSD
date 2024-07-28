@echo off
start cmd /k ".\python-3.11.6.amd64\python.exe .\dev\cntl.py"
start cmd /c "start "" "http://localhost:5000/login.html""
