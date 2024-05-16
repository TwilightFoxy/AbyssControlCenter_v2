@echo off

rem Проверяем наличие Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python не установлен, начинаю установку...
    rem Устанавливаем Python с помощью Chocolatey
    choco install python -y
    if %errorlevel% neq 0 (
        echo Не удалось установить Python. Пожалуйста, установите его вручную.
        pause
        exit /b 1
    )
    echo Python успешно установлен.
)

rem Запускаем Python скрипт
python main.py

rem Открываем командную строку
cmd
