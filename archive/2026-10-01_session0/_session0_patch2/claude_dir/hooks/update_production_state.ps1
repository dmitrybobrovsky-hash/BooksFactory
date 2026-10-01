# PostToolUse (Write|Edit) — дописывает смену статуса главы в production_state.md.
# PowerShell 5.1+. Ротация: записи старше 45 дней удаляются. 2026-10-01.
$ErrorActionPreference = 'Stop'
$production = @('outline-ready','material-draft','draft','review','clean','humanized','final')
try {
    [Console]::InputEncoding = [System.Text.Encoding]::UTF8
    $data = [Console]::In.ReadToEnd() | ConvertFrom-Json
    $filePath = $data.tool_input.file_path
    if (-not $filePath) { exit 0 }
    $root = $env:CLAUDE_PROJECT_DIR
    if (-not $root) { $root = (Get-Location).Path }
    if (-not [System.IO.Path]::IsPathRooted($filePath)) { $filePath = Join-Path $root $filePath }
    if (-not (Test-Path -LiteralPath $filePath -PathType Leaf)) { exit 0 }
    $head = (Get-Content -LiteralPath $filePath -Encoding UTF8 -TotalCount 40) -join "`n"
    $m = [regex]::Match($head, '(?m)^status:\s*["'']?([\w-]+)["'']?\s*$')
    if (-not $m.Success) { exit 0 }
    $status = $m.Groups[1].Value
    if ($production -notcontains $status) { exit 0 }

    $memory = Join-Path $root '.claude\memory\production_state.md'
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    $now = Get-Date
    $lines = @()
    if (Test-Path -LiteralPath $memory) {
        $cutoff = $now.AddDays(-45)
        foreach ($line in [System.IO.File]::ReadAllLines($memory, $utf8)) {
            $d = [regex]::Match($line, '^<!-- auto: (\d{4}-\d{2}-\d{2})')
            if ($d.Success -and ([datetime]::ParseExact($d.Groups[1].Value, 'yyyy-MM-dd', $null) -lt $cutoff)) { continue }
            $lines += $line
        }
    }
    $name = [System.IO.Path]::GetFileName($filePath)
    $lines += ''
    $lines += ("<!-- auto: {0} {1} -> {2} -->" -f $now.ToString('yyyy-MM-dd HH:mm'), $name, $status)
    [System.IO.File]::WriteAllLines($memory, [string[]]$lines, $utf8)
    exit 0
} catch { exit 0 }
