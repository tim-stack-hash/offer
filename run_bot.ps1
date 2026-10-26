$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not $env:TELEGRAM_BOT_TOKEN) {
    Write-Host 'Please set TELEGRAM_BOT_TOKEN before running the bot.'
    Write-Host 'Example: $env:TELEGRAM_BOT_TOKEN = "123:ABC"'
    exit 1
}
if (-not $env:ADMIN_USER_IDS) {
    Write-Host 'Please set ADMIN_USER_IDS to your numeric Telegram user ID before running the bot.'
    Write-Host 'Example: $env:ADMIN_USER_IDS = "123456789"'
    Write-Host 'Multiple administrators: $env:ADMIN_USER_IDS = "123456789,987654321"'
    exit 1
}
& "$PSScriptRoot\.venv\Scripts\python.exe" "$PSScriptRoot\main.py"
