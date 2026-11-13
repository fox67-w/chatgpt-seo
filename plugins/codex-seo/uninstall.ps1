# Remove only installer-owned discovery files. Package/data are retained.
[CmdletBinding()]
param(
    [string]$Project = (Get-Location).Path,
    [switch]$Apply,
    [switch]$DryRun,
    [string[]]$Extension = @(),
    [string]$Python = $env:CODEX_SEO_PYTHON
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$parameters = @{} + $PSBoundParameters
$parameters['Remove'] = $true
& (Join-Path $PSScriptRoot 'install.ps1') @parameters
exit $LASTEXITCODE
