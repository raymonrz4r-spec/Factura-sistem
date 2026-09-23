@echo off
title Sistema de Facturacion - Sublimacion POS
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] No se encontro el entorno virtual en .venv.
    echo Creando entorno virtual...
    python -m venv .venv
    call .venv\Scripts\activate
    pip install -r requirements.txt
)

echo Iniciando Sistema de Facturacion...
start "" ".venv\Scripts\pythonw.exe" main.py
exit
