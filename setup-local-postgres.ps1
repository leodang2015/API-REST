param(
    [string]$HostName = "localhost",
    [int]$Port = 5432,
    [string]$SuperUser = "postgres",
    [string]$AppUser = "biblioteca",
    [string]$AppPassword = "biblioteca",
    [string]$DatabaseName = "biblioteca"
)

$ErrorActionPreference = "Stop"

function Invoke-Psql {
    param([string[]]$Arguments)
    & psql @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "psql finalizó con el código $LASTEXITCODE"
    }
}

if (-not (Get-Command psql -ErrorAction SilentlyContinue)) {
    throw "No se encontró psql en PATH. Instala PostgreSQL y abre una terminal donde psql esté disponible."
}

if (-not $env:PGPASSWORD) {
    throw "Define la contraseña del usuario administrador antes de ejecutar: `$env:PGPASSWORD = 'tu-password'"
}

$escapedPassword = $AppPassword.Replace("'", "''")
$connection = @("-h", $HostName, "-p", $Port.ToString(), "-U", $SuperUser, "-d", "postgres", "-v", "ON_ERROR_STOP=1")

Invoke-Psql ($connection + @("-c", "DO `$`$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$AppUser') THEN CREATE ROLE `"$AppUser`" LOGIN PASSWORD '$escapedPassword'; ELSE ALTER ROLE `"$AppUser`" WITH LOGIN PASSWORD '$escapedPassword'; END IF; END `$`$;"))

$databaseExists = & psql @connection -tAc "SELECT 1 FROM pg_database WHERE datname = '$DatabaseName'"
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo consultar la existencia de la base $DatabaseName"
}
if ($databaseExists -ne "1") {
    Invoke-Psql ($connection + @("-c", "CREATE DATABASE `"$DatabaseName`" OWNER `"$AppUser`";"))
}

Invoke-Psql @("-h", $HostName, "-p", $Port.ToString(), "-U", $SuperUser, "-d", $DatabaseName, "-v", "ON_ERROR_STOP=1", "-c", "GRANT ALL ON SCHEMA public TO `"$AppUser`";")

Write-Host "PostgreSQL local configurado: $DatabaseName"
