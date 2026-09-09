# The paper, on Windows without make. Same two steps as the Makefile, same order.
#
#   .\build.ps1              regenerate the tables, then build main.pdf
#   .\build.ps1 -TablesOnly  regenerate the tables and stop
#   .\build.ps1 -Clean       remove build artifacts and the generated tables

param(
    [switch]$TablesOnly,
    [switch]$Clean
)

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

# The sibling checkout's interpreter has reidbench's dependencies; fall back to whatever
# `python` resolves to, which is right for anyone who installed the package properly.
$venv = Join-Path $PSScriptRoot '..\reidbench\.venv\Scripts\python.exe'
$python = if (Test-Path $venv) { $venv } else { 'python' }

if ($Clean) {
    latexmk -C
    Remove-Item generated\*.tex -ErrorAction SilentlyContinue
    Write-Output 'cleaned'
    return
}

& $python tools\gen_tables.py
if ($LASTEXITCODE -ne 0) { throw 'table generation failed; not building a stale PDF' }

if ($TablesOnly) { return }

latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
