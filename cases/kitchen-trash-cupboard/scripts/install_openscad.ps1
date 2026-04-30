$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$tools = Join-Path $root 'tools'
$zipPath = Join-Path $tools 'OpenSCAD-2021.01-x86-64.zip'
$shaPath = Join-Path $tools 'OpenSCAD-2021.01-x86-64.zip.sha256'
$extractPath = Join-Path $tools 'OpenSCAD-2021.01-x86-64'

New-Item -ItemType Directory -Force -Path $tools | Out-Null
Invoke-WebRequest -Uri 'https://files.openscad.org/OpenSCAD-2021.01-x86-64.zip' -OutFile $zipPath
Invoke-WebRequest -Uri 'https://files.openscad.org/OpenSCAD-2021.01-x86-64.zip.sha256' -OutFile $shaPath

$expected = ((Get-Content -LiteralPath $shaPath -Raw) -split '\s+')[0].ToLowerInvariant()
$actual = (Get-FileHash -LiteralPath $zipPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($expected -ne $actual) {
    throw "OpenSCAD zip sha256 mismatch: expected $expected actual $actual"
}

if (Test-Path -LiteralPath $extractPath) {
    Remove-Item -LiteralPath $extractPath -Recurse -Force
}
Expand-Archive -LiteralPath $zipPath -DestinationPath $extractPath -Force

$exe = Get-ChildItem -LiteralPath $extractPath -Recurse -Filter 'openscad.exe' | Select-Object -First 1
if (-not $exe) {
    throw 'openscad.exe was not found after extraction'
}

& $exe.FullName --version
Write-Output $exe.FullName
