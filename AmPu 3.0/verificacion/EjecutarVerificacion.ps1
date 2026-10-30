#Requires -Version 5.1
<#
.SYNOPSIS
    Batería de verificación de AmPu 3.0: cálculo, rendimiento, interfaz y accesibilidad.

.DESCRIPTION
    Ejecuta las pruebas del proyecto y los scripts de verificación de esta carpeta,
    guarda todos los JSON/logs/capturas en una carpeta con marca de tiempo y genera
    REPORTE.md + resumen.json + reporte.zip para analizar.

    No modifica el código ni los datos del usuario. Escribe solo en
    .\verificacion\salidas\<fecha>\ y, si se pide -Instalar, en .\.venv.

.PARAMETER Perfil
    rapido       ~5-10 min: humo de cálculo, pytest sin cobertura y UI offscreen.
    completo     Todo lo anterior + cobertura, SciPy, UI nativa si hay escritorio.
    visual       Capturas en 3 temas, zoom, contraste, accesibilidad y WebEngine.
    rendimiento  Benchmarks del núcleo a escala completa + tiempos de UI.
    calculo      Pruebas numéricas exhaustivas + cobertura + cotejo con SciPy.

.PARAMETER Python
    Intérprete a usar. Por omisión: .\.venv\Scripts\python.exe, luego py/python del PATH.

.PARAMETER Instalar
    Crea .\.venv y ejecuta pip install -r requirements.txt (requiere Internet una vez).

.PARAMETER Interfaz
    native | offscreen | ambas. "native" es la prueba visual real (necesita escritorio).

.PARAMETER Empaquetar
    Añade scripts\build_exe.py --gui-self-test (lento; requiere PyInstaller y escritorio).

.PARAMETER Salida
    Carpeta base alternativa para los resultados.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File ".\verificacion\EjecutarVerificacion.ps1" -Perfil completo -Instalar

.EXAMPLE
    pwsh -File ".\verificacion\EjecutarVerificacion.ps1" -Perfil visual -Interfaz native -AbrirReporte

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File ".\verificacion\EjecutarVerificacion.ps1" -Perfil rapido -SinConsolidar
#>
[CmdletBinding()]
param(
    [ValidateSet('rapido', 'completo', 'visual', 'rendimiento', 'calculo')]
    [string]$Perfil = 'completo',

    [string]$Python = '',

    [switch]$Instalar,

    [ValidateSet('native', 'offscreen', 'ambas')]
    [string]$Interfaz = 'ambas',

    [switch]$Empaquetar,

    [string]$Salida = '',

    [string]$Etiqueta = '',

    [int]$Repeticiones = 5,

    [int]$TimeoutGui = 45,

    [switch]$SinConsolidar,

    [switch]$SinZip,

    [switch]$AbrirReporte
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$Raiz = Split-Path -Parent $PSScriptRoot
$Pruebas = Join-Path $PSScriptRoot 'pruebas'
. (Join-Path $PSScriptRoot 'lib\Comun.ps1')

# Salida UTF-8: evita que los acentos se rompan dentro de los logs.
try {
    [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
    $OutputEncoding = New-Object System.Text.UTF8Encoding($false)
} catch { }

$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONPATH = (Join-Path $Raiz 'src')
$env:MPLBACKEND = 'Agg'

$marca = Get-Date -Format 'yyyyMMdd-HHmmss'
if ([string]::IsNullOrWhiteSpace($Salida)) {
    $nombreCarpeta = $marca
    if (-not [string]::IsNullOrWhiteSpace($Etiqueta)) { $nombreCarpeta = $marca + '-' + $Etiqueta }
    $Destino = Join-Path $PSScriptRoot ('salidas\' + $nombreCarpeta)
} else {
    $Destino = $Salida
}
$Datos = Join-Path $Destino 'datos'
$Logs = Join-Path $Destino 'logs'
$Capturas = Join-Path $Destino 'capturas'
$Exportaciones = Join-Path $Destino 'exportaciones'
foreach ($carpeta in @($Destino, $Datos, $Logs, $Capturas, $Exportaciones)) {
    if (-not (Test-Path -LiteralPath $carpeta)) {
        New-Item -ItemType Directory -Path $carpeta -Force | Out-Null
    }
}

$Pasos = New-Object System.Collections.Generic.List[object]

function Merge-Entorno {
    param([hashtable]$Base, [hashtable]$Extra)
    $resultado = @{}
    foreach ($clave in $Base.Keys) { $resultado[$clave] = $Base[$clave] }
    if ($null -ne $Extra) {
        foreach ($clave in $Extra.Keys) { $resultado[$clave] = $Extra[$clave] }
    }
    return $resultado
}

function Add-Paso {
    param($Paso)
    $script:Pasos.Add($Paso) | Out-Null
    Save-PasosJson -Pasos $script:Pasos -Ruta (Join-Path $Destino 'pasos.json')
}

Write-Titulo "Verificación de AmPu 3.0 · perfil '$Perfil'"
Write-Host ("Proyecto : " + $Raiz)
Write-Host ("Salida   : " + $Destino)
Write-Host ("PowerShell: " + $PSVersionTable.PSVersion.ToString())

# ---------------------------------------------------------------- intérprete
$PyBase = Resolve-PythonAmPu -Raiz $Raiz -Python $Python
Write-Host ("Python   : " + $PyBase + " (versión " + (Get-VersionPython -Python $PyBase) + ")")

if ($Instalar) {
    Write-Apartado "Instalación del entorno virtual"
    $venv = Join-Path $Raiz '.venv'
    if (-not (Test-Path -LiteralPath $venv)) {
        # Con el lanzador "py" se pide explícitamente 3.12 para no heredar otra versión.
        $argsVenv = @('-m', 'venv', '.venv')
        if ((Split-Path -Leaf $PyBase) -like 'py*.exe') {
            & $PyBase -3.12 --version *> $null
            if ($LASTEXITCODE -eq 0) { $argsVenv = @('-3.12', '-m', 'venv', '.venv') }
        }
        Add-Paso (Invoke-PasoExterno -Nombre 'Crear entorno virtual .venv' -Ejecutable $PyBase `
            -Argumentos $argsVenv -Directorio $Raiz `
            -Log (Join-Path $Logs 'instalacion_venv.log') -TimeoutSegundos 300)
    }
    $PyVenv = Join-Path $Raiz '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $PyVenv)) { $PyVenv = Join-Path $Raiz '.venv/bin/python' }
    if (-not (Test-Path -LiteralPath $PyVenv)) {
        throw "No se pudo crear .venv. Revisa el log instalacion_venv.log."
    }
    $Py = $PyVenv
    Add-Paso (Invoke-PasoExterno -Nombre 'Actualizar pip dentro de .venv' `
        -Ejecutable $Py -Argumentos @('-m', 'pip', 'install', '--upgrade', 'pip') `
        -Directorio $Raiz -Log (Join-Path $Logs 'instalacion_pip.log') `
        -Variables @{ PYTHONPATH = $null } -TimeoutSegundos 900)
    Add-Paso (Invoke-PasoExterno -Nombre 'Instalar AmPu 3.0 y extras de desarrollo' `
        -Ejecutable $Py -Argumentos @('-m', 'pip', 'install', '-r', 'requirements.txt') `
        -Directorio $Raiz -Log (Join-Path $Logs 'instalacion_requisitos.log') `
        -TimeoutSegundos 1800)
} else {
    $Py = Resolve-PythonAmPu -Raiz $Raiz -Python $Python
}

$versionPy = Get-VersionPython -Python $Py
$partes = $versionPy.Split('.')
if ($partes.Count -ge 2 -and ([int]$partes[0] -lt 3 -or ([int]$partes[0] -eq 3 -and [int]$partes[1] -lt 12))) {
    Write-Aviso "AmPu 3.0 requiere Python 3.12 o posterior; se detectó $versionPy. Los resultados pueden no ser válidos."
}

$Base = @{
    PYTHONUTF8           = '1'
    PYTHONIOENCODING     = 'utf-8'
    PYTHONPATH           = (Join-Path $Raiz 'src')
    MPLBACKEND           = 'Agg'
    QTWEBENGINE_DISABLE_SANDBOX = '1'
}
$Offscreen = @{ QT_QPA_PLATFORM = 'offscreen' }
$Nativo = @{ QT_QPA_PLATFORM = $null }

function Invoke-Py {
    param(
        [Parameter(Mandatory)][string]$Nombre,
        [Parameter(Mandatory)][string[]]$Argumentos,
        [hashtable]$Variables = @{},
        [int]$TimeoutSegundos = 1800,
        [Parameter(Mandatory)][string]$Log
    )
    $paso = Invoke-PasoExterno -Nombre $Nombre -Ejecutable $Py -Argumentos $Argumentos `
        -Directorio $Raiz -Variables (Merge-Entorno $Base $Variables) `
        -TimeoutSegundos $TimeoutSegundos -Log (Join-Path $Logs $Log)
    Add-Paso $paso
    return $paso
}

function Test-InterfazNativa {
    if ($Interfaz -eq 'offscreen') { return $false }
    if ($env:OS -eq 'Windows_NT' -or $env:SESSIONNAME -or $env:DISPLAY -or $env:WAYLAND_DISPLAY) { return $true }
    return ($Interfaz -eq 'native')
}

$quiereNativo = Test-InterfazNativa
$haceCalculo = $Perfil -in @('rapido', 'completo', 'calculo')
$haceRendimiento = $Perfil -in @('completo', 'rendimiento')
$haceVisual = $Perfil -in @('completo', 'visual')
$hacePytest = $Perfil -in @('rapido', 'completo', 'calculo')
$haceCobertura = $Perfil -in @('completo', 'calculo')

Write-Host ""
Write-Host "Plan:" -ForegroundColor White
Write-Host ("  entorno y versión .......... siempre")
Write-Host ("  verify-resources ........... siempre")
Write-Host ("  pytest ..................... " + $(if ($hacePytest) { "sí" } else { "no" }) + $(if ($haceCobertura) { " (con cobertura)" } else { "" }))
Write-Host ("  contraste con SciPy ........ " + $(if ($Perfil -ne 'visual') { "sí" } else { "no" }))
Write-Host ("  pruebas de cálculo ......... " + $(if ($haceCalculo) { "sí" } else { "no" }))
Write-Host ("  rendimiento del núcleo ..... " + $(if ($haceRendimiento) { "sí" } else { "no" }))
Write-Host ("  interfaz offscreen ......... sí")
Write-Host ("  interfaz nativa ............ " + $(if ($quiereNativo) { "sí" } else { "no" }))
Write-Host ("  autoprueba QtWebEngine ..... " + $(if ($quiereNativo -and $Perfil -in @('completo', 'visual')) { "sí" } else { "no" }))
Write-Host ("  empaquetado PyInstaller .... " + $(if ($Empaquetar) { "sí" } else { "no" }))

# --------------------------------------------------------------- 1. entorno
Write-Apartado "1. Huella del equipo"
$argsEntorno = @((Join-Path $Pruebas 'recolectar_entorno.py'), '--salida', (Join-Path $Datos 'entorno.json'))
$varsEntorno = $Offscreen
if ($quiereNativo) {
    $argsEntorno += '--gui'
    $varsEntorno = $Nativo  # leer DPI, escala y tema reales del escritorio
}
Invoke-Py -Nombre 'Recolectar entorno (SO, versiones, pantallas, commit)' `
    -Argumentos $argsEntorno -Variables $varsEntorno -TimeoutSegundos 300 `
    -Log 'entorno.log' | Out-Null

# ------------------------------------------------------ 2. versión y recursos
Write-Apartado "2. Versión y recursos empaquetados"
Invoke-Py -Nombre 'Versión de AmPu' -Argumentos @('-m', 'ampu', '--version') `
    -TimeoutSegundos 120 -Log 'version.log' | Out-Null
Invoke-Py -Nombre 'Verificar recursos y exportadores (--verify-resources)' `
    -Argumentos @('-m', 'ampu', '--verify-resources') -TimeoutSegundos 600 `
    -Log 'verify_resources.log' | Out-Null

# ----------------------------------------------------------- 3. suite pytest
if ($hacePytest) {
    Write-Apartado "3. Suite automática (pytest)"
    $argsPytest = @('-m', 'pytest', '-p', 'no:cacheprovider', '--junitxml=' + (Join-Path $Datos 'junit.xml'))
    if ($haceCobertura) {
        $argsPytest += @('--cov=ampu.core', '--cov-branch', '--cov-report=term-missing',
                         '--cov-report=xml:' + (Join-Path $Datos 'coverage.xml'))
    }
    Invoke-Py -Nombre 'Ejecutar pytest' -Argumentos $argsPytest -TimeoutSegundos 3600 `
        -Log 'pytest.log' | Out-Null
}

# ----------------------------------------------------------- 4. validar SciPy
if ($Perfil -ne 'visual') {
    Write-Apartado "4. Cotejo independiente contra SciPy"
    Invoke-Py -Nombre 'Comparar 26 distribuciones con SciPy' `
        -Argumentos @((Join-Path $Raiz 'scripts\validar_contra_scipy.py'),
                      '--salida', (Join-Path $Datos 'scipy.json')) `
        -TimeoutSegundos 900 -Log 'scipy.log' | Out-Null
}

# ------------------------------------------------------- 5. pruebas de cálculo
if ($haceCalculo) {
    Write-Apartado "5. Pruebas de cálculo"
    $argsCalculo = @((Join-Path $Pruebas 'pruebas_calculo.py'), '--salida', (Join-Path $Datos 'calculo.json'))
    if ($Perfil -eq 'rapido') { $argsCalculo += '--rapido' }
    Invoke-Py -Nombre 'Comprobar 26 distribuciones, muestreo, inferencia, simulación y exportadores' `
        -Argumentos $argsCalculo -TimeoutSegundos 3600 -Log 'calculo.log' | Out-Null
}

# ------------------------------------------------------------- 6. rendimiento
if ($haceRendimiento) {
    Write-Apartado "6. Rendimiento del núcleo"
    $escala = 'normal'
    $reps = $Repeticiones
    if ($Perfil -eq 'rendimiento') { $escala = 'completa'; $reps = [Math]::Max(10, $Repeticiones) }
    Invoke-Py -Nombre ("Benchmark del núcleo (escala " + $escala + ", " + $reps + " repeticiones)") `
        -Argumentos @((Join-Path $Pruebas 'benchmark_calculo.py'),
                      '--salida', (Join-Path $Datos 'rendimiento.json'),
                      '--escala', $escala, '--repeticiones', [string]$reps) `
        -TimeoutSegundos 5400 -Log 'rendimiento.log' | Out-Null
}

# --------------------------------------------------------- 7. interfaz offscreen
Write-Apartado "7. Interfaz en raster offscreen"
Invoke-Py -Nombre 'UI offscreen: vistas, temas, contraste, exportaciones y sesión' `
    -Argumentos @((Join-Path $Pruebas 'benchmark_ui.py'),
                  '--plataforma', 'offscreen', '--sin-teoria',
                  '--salida', (Join-Path $Datos 'ui_offscreen.json'),
                  '--capturas', (Join-Path $Capturas 'offscreen'),
                  '--exportaciones', (Join-Path $Exportaciones 'offscreen'),
                  '--timeout', [string]$TimeoutGui) `
    -Variables $Offscreen -TimeoutSegundos 1800 -Log 'ui_offscreen.log' | Out-Null

# ------------------------------------------------------------ 8. interfaz nativa
if ($quiereNativo) {
    Write-Apartado "8. Interfaz nativa (prueba visual real)"
    $argsUi = @((Join-Path $Pruebas 'benchmark_ui.py'),
                '--plataforma', 'native',
                '--salida', (Join-Path $Datos 'ui_nativo.json'),
                '--capturas', $Capturas,
                '--exportaciones', (Join-Path $Exportaciones 'nativo'),
                '--timeout', [string]$TimeoutGui)
    if ($haceVisual) { $argsUi += @('--zoom', '1.5', '2.0') }
    if (Test-Path -LiteralPath (Join-Path $Datos 'linea_base_ui.json')) {
        $argsUi += @('--linea-base', (Join-Path $Datos 'linea_base_ui.json'))
    }
    Invoke-Py -Nombre 'UI nativa: capturas por tema/vista, contraste, accesibilidad y WebEngine' `
        -Argumentos $argsUi -Variables $Nativo -TimeoutSegundos 2400 -Log 'ui_nativo.log' | Out-Null
}

# ------------------------------------------------------- 9. autoprueba estricta
if ($quiereNativo -and $Perfil -in @('completo', 'visual')) {
    Write-Apartado "9. Autoprueba estricta de QtWebEngine"
    Invoke-Py -Nombre 'Autoprueba --self-test con captura de teoría' `
        -Argumentos @('-m', 'ampu', '--self-test',
                      '--capture-theory', (Join-Path $Capturas 'teoria_selftest.png')) `
        -Variables $Nativo -TimeoutSegundos 900 -Log 'self_test.log' | Out-Null
}

# ------------------------------------------------------------- 10. empaquetado
if ($Empaquetar) {
    Write-Apartado "10. Empaquetado PyInstaller"
    $argsBuild = @((Join-Path $Raiz 'scripts\build_exe.py'), '--gui-self-test')
    Invoke-Py -Nombre 'Construir ejecutable y verificar el binario con interfaz' `
        -Argumentos $argsBuild -TimeoutSegundos 5400 -Log 'empaquetado.log' | Out-Null
}

# ------------------------------------------------------------- 11. consolidar
Write-Apartado "11. Consolidar reporte"
if ($SinConsolidar) {
    Write-Aviso "Se omitió la consolidación (-SinConsolidar). Los JSON están en $Datos"
} else {
    $argsReporte = @((Join-Path $Pruebas 'consolidar_reporte.py'), '--carpeta', $Destino)
    if ($SinZip) { $argsReporte += '--sin-zip' }
    Invoke-Py -Nombre 'Generar REPORTE.md, resumen.json y paquete ZIP' `
        -Argumentos $argsReporte -TimeoutSegundos 900 -Log 'consolidacion.log' | Out-Null
}

# ---------------------------------------------------------------- resumen final
Show-TablaPasos -Pasos $Pasos

$fallidos = @($Pasos | Where-Object { $_.estado -ne 'OK' })
$reporte = Join-Path $Destino 'REPORTE.md'
Write-Titulo "Fin de la verificación"
Write-Host ("Carpeta  : " + $Destino)
if (Test-Path -LiteralPath $reporte) {
    Write-Host ("Reporte  : " + $reporte)
    Write-Host ("Resumen  : " + (Join-Path $Destino 'resumen.json'))
}
Write-Host ("Capturas : " + $Capturas)
Write-Host ("Logs     : " + $Logs)
if ($fallidos.Count -gt 0) {
    Write-ErrorPaso ("Pasos con incidencias: " + $fallidos.Count)
    foreach ($paso in $fallidos) {
        Write-Host ("  - " + $paso.nombre + " [" + $paso.estado + ", código " + $paso.codigo + "] · " + $paso.log) -ForegroundColor Red
    }
} else {
    Write-Ok "Todos los pasos terminaron correctamente."
}

if ($AbrirReporte -and (Test-Path -LiteralPath $reporte)) {
    try {
        if ($env:OS -eq 'Windows_NT') { Start-Process -FilePath $reporte }
        elseif ($env:OS -eq 'darwin') { & open $reporte }
        else { & xdg-open $reporte | Out-Null }
    } catch {
        Write-Aviso "No se pudo abrir el reporte automáticamente: $($_.Exception.Message)"
    }
}

if ($fallidos.Count -gt 0) { exit 1 } else { exit 0 }
