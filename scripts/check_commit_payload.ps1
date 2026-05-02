[CmdletBinding()]
param(
    [string]$RepoPath = ".",
    [double]$WarnMiB = 50,
    [double]$BlockMiB = 100,
    [int]$Top = 20
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Format-MiB {
    param(
        [int64]$Bytes
    )

    if ($Bytes -ge 10MB) {
        return ("{0:N1}" -f ($Bytes / 1MB))
    }

    if ($Bytes -ge 1MB) {
        return ("{0:N2}" -f ($Bytes / 1MB))
    }

    return ("{0:N3}" -f ($Bytes / 1MB))
}

$resolvedRepoPath = (Resolve-Path -LiteralPath $RepoPath).Path
$gitRoot = git -C $resolvedRepoPath rev-parse --show-toplevel 2>$null
if ($LASTEXITCODE -ne 0) {
    throw "The target path is not inside a Git repository: $resolvedRepoPath"
}

$nullSeparatedPaths = git -C $gitRoot diff --cached --name-only --diff-filter=ACMR -z
if ($LASTEXITCODE -ne 0) {
    throw "Failed to read the staged file list from Git."
}

$stagedPaths = $nullSeparatedPaths -split "`0" | Where-Object { $_ }
if (-not $stagedPaths) {
    Write-Host "No staged added or modified files to inspect."
    exit 0
}

$warnBytes = [int64]($WarnMiB * 1MB)
$blockBytes = [int64]($BlockMiB * 1MB)

$items = @(foreach ($relativePath in $stagedPaths) {
    $indexEntry = git -C $gitRoot ls-files -s -- "$relativePath"
    if ($LASTEXITCODE -ne 0 -or -not $indexEntry) {
        Write-Warning "Skipping $relativePath because its staged blob could not be resolved."
        continue
    }

    $firstEntry = ($indexEntry -split "\r?\n" | Where-Object { $_ } | Select-Object -First 1)
    if ($firstEntry -notmatch '^\d+\s+([0-9a-f]{40})\s+\d+\t(.+)$') {
        Write-Warning "Skipping $relativePath because its index entry format was unexpected."
        continue
    }

    $blobSha = $Matches[1]
    $indexPath = $Matches[2]
    $blobSizeText = git -C $gitRoot cat-file -s $blobSha
    if ($LASTEXITCODE -ne 0 -or -not $blobSizeText) {
        Write-Warning "Skipping $indexPath because its blob size could not be read."
        continue
    }

    $blobSizeBytes = [int64]($blobSizeText.Trim())
    $status = if ($blobSizeBytes -ge $blockBytes) {
        "BLOCK"
    }
    elseif ($blobSizeBytes -ge $warnBytes) {
        "WARN"
    }
    else {
        "OK"
    }

    [PSCustomObject]@{
        Status    = $status
        SizeMiB   = Format-MiB -Bytes $blobSizeBytes
        SizeBytes = $blobSizeBytes
        Path      = $indexPath
    }
})

if (-not $items) {
    Write-Warning "No staged payload entries could be inspected."
    exit 1
}

$totalBytes = [int64](($items | Measure-Object -Property SizeBytes -Sum).Sum)
$totalMiB = Format-MiB -Bytes $totalBytes
$warnItems = @($items | Where-Object { $_.Status -eq "WARN" })
$blockItems = @($items | Where-Object { $_.Status -eq "BLOCK" })

Write-Host ("Staged files checked: {0}" -f $items.Count)
Write-Host ("Total staged payload: {0} MiB" -f $totalMiB)
Write-Host ("Thresholds: warn at {0} MiB, block at {1} MiB" -f $WarnMiB, $BlockMiB)
Write-Host ""

$items |
    Sort-Object -Property SizeBytes -Descending |
    Select-Object -First $Top Status, SizeMiB, Path |
    Format-Table -AutoSize

if ($warnItems) {
    Write-Host ""
    Write-Warning ("{0} staged file(s) reached the review threshold." -f $warnItems.Count)
    $warnItems |
        Sort-Object -Property SizeBytes -Descending |
        Select-Object Status, SizeMiB, Path |
        Format-Table -AutoSize
}

if ($blockItems) {
    Write-Host ""
    Write-Host ("Blocking threshold reached for {0} staged file(s). Remove them from the commit, compress them, or move them to Git LFS / Releases before pushing." -f $blockItems.Count)
    exit 1
}

Write-Host ""
Write-Host "Staged payload is within the configured thresholds."
