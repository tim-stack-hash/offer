@echo off
cd /d "%~dp0"
if "%TELEGRAM_BOT_TOKEN%"=="" (
    echo Please set TELEGRAM_BOT_TOKEN before running the bot.
    echo Example: set TELEGRAM_BOT_TOKEN=123:ABC
    exit /b 1
)
if "%ADMIN_USER_IDS%"=="" (
    echo Please set ADMIN_USER_IDS to your numeric Telegram user ID before running the bot.
    echo Example: set ADMIN_USER_IDS=123456789
    echo Multiple administrators: set ADMIN_USER_IDS=123456789,987654321
    exit /b 1
)
"%~dp0.venv\Scripts\python.exe" "%~dp0main.py"
