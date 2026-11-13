# Pass arguments verbatim to the shared standard-library Python entrypoint.
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$RuntimeArguments = $args
$MinMinor = 11
$MaxMinor = 14
$RuntimePath = Join-Path $PSScriptRoot 'codex_seo.py'

function Find-CompatiblePython {
    param([string]$Executable, [string[]]$PrefixArguments = @())
    try {
        $command = Get-Command -Name $Executable -CommandType Application -ErrorAction Stop | Select-Object -First 1
        $probeArguments = @($PrefixArguments) + @('-c', 'import sys; print("%d.%d" % sys.version_info[:2])')
        $versionOutput = & $command.Source @probeArguments 2>$null
        $probeExitCode = $LASTEXITCODE
        $version = ($versionOutput -join '').Trim()
        if ($probeExitCode -eq 0 -and $version -match '^3\.(\d+)$' -and
            [int]$Matches[1] -ge $MinMinor -and [int]$Matches[1] -le $MaxMinor) {
            return [PSCustomObject]@{Executable = $command.Source; PrefixArguments = @($PrefixArguments)}
        }
    } catch {
        # A missing/unsupported interpreter is a candidate failure, not setup.
    }
    return $null
}

$selected = $null
if ($env:CODEX_SEO_PYTHON) {
    $selected = Find-CompatiblePython -Executable $env:CODEX_SEO_PYTHON
    if ($null -eq $selected) {
        [Console]::Error.WriteLine("CODEX_SEO_PYTHON must name a Python 3.$MinMinor to 3.$MaxMinor executable.")
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
    [Console]::Error.WriteLine("Codex SEO needs Python 3.$MinMinor to 3.$MaxMinor. Set CODEX_SEO_PYTHON to a supported interpreter.")
    exit 2
}

$launchArguments = @($selected.PrefixArguments) + @($RuntimePath) + @($RuntimeArguments)
& $selected.Executable @launchArguments
exit $LASTEXITCODE
