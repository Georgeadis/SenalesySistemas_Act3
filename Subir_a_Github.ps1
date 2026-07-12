<#
Subir_a_Github.ps1
Script de automatización para añadir, commitear, sincronizar (pull --rebase) y pushear a GitHub.
Uso:
  .\Subir_a_Github.ps1 -Message "Mi commit" [-Remote origin] [-Branch main] [-Force]
Notas:
  - No usa credenciales en claro; ejecuta desde una sesión con credenciales (token en Git credential manager).
  - Evita usar -Force salvo que entiendas las consecuencias.
#>
param(
    [string]$Message = "Auto: actualización",
    [string]$Remote = "origin",
    [string]$Branch = "main",
    [switch]$Force
)

function Fail([string]$msg, [int]$code=1) {
    Write-Error $msg
    exit $code
}

if (-not (Test-Path .git)) {
    Fail "No se encontró un repo git en el directorio actual."
}

Write-Host "Estado previo (resumen):"
git status --short

# Añadir cambios
Write-Host "Añadiendo cambios..."
git add -A
if ($LASTEXITCODE -ne 0) { Fail "git add falló." }

# Commit si hay cambios
$changes = git status --porcelain
if ($changes) {
    Write-Host "Creando commit: $Message"
    git commit -m "$Message"
    if ($LASTEXITCODE -ne 0) { Fail "git commit falló." }
} else {
    Write-Host "No hay cambios para commitear."
}

# Sincronizar con remoto
Write-Host "Obteniendo cambios remotos..."
git fetch $Remote
if ($LASTEXITCODE -ne 0) { Fail "git fetch falló." }

Write-Host "Intentando pull --rebase desde $Remote/$Branch..."
$pull = git pull --rebase $Remote $Branch 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Pull falló o hay conflictos. Mensaje de git:"
    Write-Host $pull
    Fail "Resuelve los conflictos manualmente y vuelve a ejecutar el script." 4
}

# Push
if ($Force) {
    Write-Host "Realizando push --force a $Remote/$Branch (peligroso)."
    git push --force $Remote $Branch
} else {
    Write-Host "Realizando push a $Remote/$Branch."
    git push $Remote $Branch
}

if ($LASTEXITCODE -ne 0) { Fail "git push falló." }

Write-Host "Operación completada correctamente."