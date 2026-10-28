# Запуск бота в Windows PowerShell. Настройки берутся из .env в корне проекта
# или из переменных окружения; при ошибке бот сам подскажет, чего не хватает.
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
& '.\.venv\Scripts\python.exe' -m bot
