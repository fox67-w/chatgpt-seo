# Codex SEO project installer. Defaults to a read-only plan.
[CmdletBinding()]
param(
    [string]$Project = (Get-Location).Path,
    [switch]$Apply,
    [switch]$DryRun,
    [switch]$Remove,
    [string[]]$Extension = @(),
    [string]$Python = $env:CODEX_SEO_PYTHON
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$MinMinor = 11
$MaxMinor = 14

function Find-CompatiblePython {
    param([string]$Executable, [string[]]$PrefixArguments = @())
    try {
        $command = Get-Command -Name $Executable -CommandType Application -ErrorAction Stop | Select-Object -First 1
        if ($command.Source -match '[\\/]Microsoft[\\/]WindowsApps[\\/]') {
            return $null  # App execution aliases can open the Store instead of Python.
        }
        $probeArguments = @($PrefixArguments) + @('-c', 'import sys; print("%d.%d" % sys.version_info[:2])')
        $versionOutput = & $command.Source @probeArguments 2>$null
        $probeExitCode = $LASTEXITCODE
        $version = ($versionOutput -join '').Trim()
        if ($probeExitCode -eq 0 -and $version -match '^3\.(\d+)$' -and
            [int]$Matches[1] -ge $MinMinor -and [int]$Matches[1] -le $MaxMinor) {
            return [PSCustomObject]@{Executable = $command.Source; PrefixArguments = @($PrefixArguments)}
        }
    } catch {
        # Missing or unsupported defaults do not prevent versioned fallbacks.
    }
    return $null
}

$selected = $null
if ($Python) {
    $selected = Find-CompatiblePython -Executable $Python
    if ($null -eq $selected) {
        [Console]::Error.WriteLine("-Python or CODEX_SEO_PYTHON must name a Python 3.$MinMinor to 3.$MaxMinor executable.")
        exit 2
    }
} else {
    $candidates = @(
        @{Executable = 'py'; Prefix = @('-3')},
        @{Executable = 'python3'; Prefix = @()},
        @{Executable = 'python'; Prefix = @()}
    )
    for ($minor = $MaxMinor; $minor -ge $MinMinor; $minor--) {
        $candidates += @{Executable = 'py'; Prefix = @("-3.$minor")}
        $candidates += @{Executable = "python3.$minor"; Prefix = @()}
    }
    foreach ($candidate in $candidates) {
        $selected = Find-CompatiblePython -Executable $candidate.Executable -PrefixArguments $candidate.Prefix
        if ($null -ne $selected) { break }
    }
}
if ($null -eq $selected) {
    [Console]::Error.WriteLine("Codex SEO needs Python 3.$MinMinor to 3.$MaxMinor. Use -Python or CODEX_SEO_PYTHON.")
    exit 2
}
$installArgs = @('--project', $Project)
if ($Apply) { $installArgs += '--apply' }
if ($DryRun) { $installArgs += '--dry-run' }
if ($Remove) { $installArgs += '--remove' }
foreach ($name in $Extension) { $installArgs += @('--extension', $name) }
$launchArgs = @($selected.PrefixArguments) + @((Join-Path $PSScriptRoot 'install-codex.py')) + @($installArgs)
& $selected.Executable @launchArgs
exit $LASTEXITCODE
