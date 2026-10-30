# Común.ps1 - utilidades de la batería de verificación de AmPu 3.0
# Compatible con Windows PowerShell 5.1 y PowerShell 7+.
# Se carga con:  . "$PSScriptRoot\lib\Comun.ps1"

Set-StrictMode -Version 1.0

function Write-Titulo {
    param([Parameter(Mandatory)][string]$Texto)
    Write-Host ""
    Write-Host ("=" * 78) -ForegroundColor Cyan
    Write-Host $Texto -ForegroundColor Cyan
    Write-Host ("=" * 78) -ForegroundColor Cyan
}

function Write-Apartado {
    param([Parameter(Mandatory)][string]$Texto)
    Write-Host ""
    Write-Host ("-- " + $Texto + " " + ("-" * [Math]::Max(0, 70 - $Texto.Length))) -ForegroundColor DarkCyan
}

function Write-Ok {
    param([Parameter(Mandatory)][string]$Texto)
    Write-Host ("  [OK]     " + $Texto) -ForegroundColor Green
}

function Write-Aviso {
    param([Parameter(Mandatory)][string]$Texto)
    Write-Host ("  [AVISO]  " + $Texto) -ForegroundColor Yellow
}

function Write-ErrorPaso {
    param([Parameter(Mandatory)][string]$Texto)
    Write-Host ("  [ERROR]  " + $Texto) -ForegroundColor Red
}

function ConvertTo-ComandoTexto {
    param([string]$Ejecutable, [string[]]$Argumentos)
    $partes = @()
    foreach ($arg in $Argumentos) {
        if ($null -eq $arg) { continue }
        if ($arg -match '\s') { $partes += ('"' + $arg + '"') } else { $partes += $arg }
    }
    if ($partes.Count -eq 0) { return $Ejecutable }
    return ($Ejecutable + " " + ($partes -join " "))
}

function Resolve-PythonAmPu {
    <# Localiza el intérprete: -Python explícito, .venv del proyecto, py -3.12 o python. #>
    param(
        [string]$Raiz,
        [string]$Python
    )
    if ($Python) {
        if (Test-Path -LiteralPath $Python) { return (Resolve-Path -LiteralPath $Python).Path }
        $comando = Get-Command $Python -ErrorAction SilentlyContinue
        if ($comando) { return $comando.Source }
        throw "No se encontró el intérprete indicado en -Python: $Python"
    }
    $venv = Join-Path $Raiz ".venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $venv) { return $venv }
    $venvPosix = Join-Path $Raiz ".venv/bin/python"
    if (Test-Path -LiteralPath $venvPosix) { return $venvPosix }
    foreach ($candidato in @("py", "python3", "python")) {
        $comando = Get-Command $candidato -ErrorAction SilentlyContinue
        if ($comando) {
            if ($candidato -eq "py") {
                return $comando.Source
            }
            return $comando.Source
        }
    }
    throw "No se encontró Python. Instálalo (3.12+) o pasa -Python 'C:\ruta\python.exe'."
}

function Get-VersionPython {
    param([Parameter(Mandatory)][string]$Python)
    try {
        $texto = & $Python -c "import sys;print('%d.%d.%d' % sys.version_info[:3])" 2>$null
        return ($texto | Select-Object -First 1)
    } catch {
        return "desconocida"
    }
}

function Invoke-PasoExterno {
    <#
    Ejecuta un proceso externo con entorno controlado y tiempo límite.
    Devuelve un objeto resumen; nunca lanza por un código de salida distinto de cero,
    para que el reporte conserve la evidencia de todos los pasos.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Nombre,
        [Parameter(Mandatory)][string]$Ejecutable,
        [string[]]$Argumentos = @(),
        [string]$Directorio = (Get-Location).Path,
        [hashtable]$Variables = @{},
        [int]$TimeoutSegundos = 1800,
        [Parameter(Mandatory)][string]$Log
    )

    $comando = ConvertTo-ComandoTexto -Ejecutable $Ejecutable -Argumentos $Argumentos
    Write-Host ""
    Write-Host (">> " + $Nombre) -ForegroundColor White
    Write-Host ("   " + $comando) -ForegroundColor DarkGray

    # Un único objeto como argumento: evita que PowerShell aplane el arreglo de argumentos.
    $bloque = {
        param($paquete)
        Set-Location -LiteralPath $paquete.Directorio
        # Las variables viajan como cadenas "CLAVE=VALOR" o "CLAVE" (para borrarlas):
        # así sobreviven a la serialización de Start-Job en PowerShell 5.1 y 7.
        foreach ($par in @($paquete.Variables)) {
            $textoPar = [string]$par
            $indice = $textoPar.IndexOf('=')
            if ($indice -lt 1) {
                Remove-Item -Path ("env:" + $textoPar) -ErrorAction SilentlyContinue
            } else {
                $clave = $textoPar.Substring(0, $indice)
                $valor = $textoPar.Substring($indice + 1)
                Set-Item -Path ("env:" + $clave) -Value $valor -Force
            }
        }
        $exe = $paquete.Ejecutable
        $argumentos = $paquete.Argumentos
        $salida = & $exe @argumentos 2>&1 | Out-String
        [pscustomobject]@{ Codigo = $LASTEXITCODE; Salida = $salida }
    }

    $inicio = Get-Date
    $cronometro = [System.Diagnostics.Stopwatch]::StartNew()
    $estado = "OK"
    $codigo = 0
    $texto = ""

    $pares = @()
    foreach ($clave in $Variables.Keys) {
        $valor = $Variables[$clave]
        if ($null -eq $valor) {
            $pares += [string]$clave
        } else {
            $pares += ([string]$clave + '=' + [string]$valor)
        }
    }
    $paquete = @{
        Ejecutable  = $Ejecutable
        Argumentos  = @($Argumentos)
        Directorio  = $Directorio
        Variables   = @($pares)
    }
    $trabajo = Start-Job -ScriptBlock $bloque -ArgumentList $paquete
    try {
        $completado = Wait-Job -Job $trabajo -Timeout $TimeoutSegundos
        if ($null -eq $completado) {
            $estado = "TIMEOUT"
            $codigo = -1
            Stop-Job -Job $trabajo -ErrorAction SilentlyContinue
            $texto = "El paso superó el límite de $TimeoutSegundos s y se detuvo." + [Environment]::NewLine
        } else {
            $resultado = Receive-Job -Job $trabajo
            if ($resultado -is [System.Array]) {
                $resultado = $resultado | Select-Object -Last 1
            }
            if ($null -ne $resultado) {
                $propCodigo = $resultado.PSObject.Properties['Codigo']
                $propSalida = $resultado.PSObject.Properties['Salida']
                if ($null -ne $propCodigo) { $codigo = [int]$propCodigo.Value }
                if ($null -ne $propSalida) { $texto = [string]$propSalida.Value }
            }
            if ($codigo -ne 0) { $estado = "FALLA" }
        }
    } catch {
        $estado = "FALLA"
        $codigo = -2
        $texto = "Excepción al ejecutar el paso: " + $_.Exception.Message
    } finally {
        $cronometro.Stop()
        Remove-Job -Job $trabajo -Force -ErrorAction SilentlyContinue
    }

    $contenido = @()
    $contenido += ("# " + $Nombre)
    $contenido += ("# comando: " + $comando)
    $contenido += ("# estado: " + $estado + " (código " + $codigo + ")")
    $contenido += ("# duración: " + [Math]::Round($cronometro.Elapsed.TotalSeconds, 1) + " s")
    $contenido += ""
    $contenido += $texto
    Set-Content -LiteralPath $Log -Value $contenido -Encoding UTF8

    $lineas = ($texto -split "`r?`n") | Where-Object { $_.Trim().Length -gt 0 }
    $resumen = ($lineas | Select-Object -Last 6) -join " | "
    if ($resumen.Length -gt 500) { $resumen = $resumen.Substring(0, 500) + "..." }

    if ($estado -eq "OK") {
        Write-Ok ("$Nombre (" + [Math]::Round($cronometro.Elapsed.TotalSeconds, 1) + " s)")
    } elseif ($estado -eq "TIMEOUT") {
        Write-ErrorPaso ("$Nombre agotó el tiempo límite de $TimeoutSegundos s")
    } else {
        Write-ErrorPaso ("$Nombre terminó con código $codigo (" + [Math]::Round($cronometro.Elapsed.TotalSeconds, 1) + " s)")
    }
    foreach ($linea in ($lineas | Select-Object -Last 4)) {
        Write-Host ("   " + $linea) -ForegroundColor DarkGray
    }

    return [pscustomobject]@{
        nombre        = $Nombre
        comando       = $comando
        estado        = $estado
        codigo        = $codigo
        duracion_s    = [Math]::Round($cronometro.Elapsed.TotalSeconds, 1)
        inicio        = $inicio.ToString("o")
        log           = $Log
        resumen_salida = $resumen
    }
}

function Save-PasosJson {
    param(
        [Parameter(Mandatory)]$Pasos,
        [Parameter(Mandatory)][string]$Ruta
    )
    $lista = @()
    foreach ($paso in $Pasos) { $lista += $paso }
    if ($lista.Count -eq 0) {
        Set-Content -LiteralPath $Ruta -Value '[]' -Encoding UTF8
    } else {
        $json = ConvertTo-Json -InputObject $lista -Depth 5
        if ($json -notmatch '^\s*\[') { $json = '[' + $json + ']' }
        Set-Content -LiteralPath $Ruta -Value $json -Encoding UTF8
    }
}

function Show-TablaPasos {
    param([Parameter(Mandatory)]$Pasos)
    Write-Titulo "Resumen de pasos"
    $filas = @()
    foreach ($paso in $Pasos) {
        $filas += [pscustomobject]@{
            Paso     = $paso.nombre
            Estado   = $paso.estado
            Codigo   = $paso.codigo
            Segundos = $paso.duracion_s
        }
    }
    $filas | Format-Table -AutoSize | Out-String -Width 200 | Write-Host
}
