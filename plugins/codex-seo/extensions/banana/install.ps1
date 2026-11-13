# Codex extension activation is project-scoped and defaults to a dry run.
[CmdletBinding()]
param(
    [string]$Project = (Get-Location).Path,
    [switch]$Apply,
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
$PluginRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$PythonArgs = @()
if ($env:CODEX_SEO_PYTHON) {
    $PythonExe = $env:CODEX_SEO_PYTHON
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PythonExe = 'python3'
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonExe = 'python'
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $PythonExe = 'py'
    $PythonArgs = @('-3')
} else {
    throw 'Python 3.11 or newer is required. Set CODEX_SEO_PYTHON to its executable.'
}
$InstallArgs = @((Join-Path $PluginRoot 'install-codex.py'), '--extension', 'banana', '--project', $Project)
if ($Apply -and $DryRun) { throw 'Choose either -Apply or -DryRun.' }
if ($Apply) { $InstallArgs += '--apply' } else { $InstallArgs += '--dry-run' }
& $PythonExe @PythonArgs @InstallArgs
exit $LASTEXITCODE
