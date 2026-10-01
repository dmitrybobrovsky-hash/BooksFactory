# PreToolUse (Write|Edit) — блокирует правку глав со статусом `final`.
# PowerShell 5.1+ (есть на любом Windows, установка не нужна). 2026-10-01.
# Fail-open: любая ошибка разбора -> exit 0; блок (exit 2) только при явном `final`.
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = 'Stop'
try {
    [Console]::InputEncoding = [System.Text.Encoding]::UTF8
    $raw = [Console]::In.ReadToEnd()
    $data = $raw | ConvertFrom-Json
    $filePath = $data.tool_input.file_path
    if (-not $filePath) { exit 0 }
    $root = $env:CLAUDE_PROJECT_DIR
    if (-not $root) { $root = (Get-Location).Path }
    if (-not [System.IO.Path]::IsPathRooted($filePath)) { $filePath = Join-Path $root $filePath }
    if (-not (Test-Path -LiteralPath $filePath -PathType Leaf)) { exit 0 }
    $head = (Get-Content -LiteralPath $filePath -Encoding UTF8 -TotalCount 40) -join "`n"
    $m = [regex]::Match($head, '(?m)^status:\s*["'']?([\w-]+)["'']?\s*$')
    if (-not $m.Success) { exit 0 }
    if ($m.Groups[1].Value -eq 'final') {
        [Console]::Error.WriteLine("BLOCK: Глава имеет статус 'final'. Редактирование запрещено без явного подтверждения автора.")
        exit 2
    }
    exit 0
} catch { exit 0 }
