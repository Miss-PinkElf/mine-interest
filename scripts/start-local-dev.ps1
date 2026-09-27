# 在 Windows PowerShell 中同时启动本地前后端；按 Ctrl+C 停止本次启动的进程。
param(
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5173
)

$ErrorActionPreference = 'Stop'

# 本地开发服务只监听回环地址，不对局域网开放。
$DevHost = '127.0.0.1'
# 端口被占用时，最多向后寻找的端口数量。
$MaxPortShift = 20
# 启动探测的间隔，单位为毫秒。
$HealthPollIntervalMs = 250
# 后端健康检查的最多尝试次数。
$BackendHealthAttempts = 40
# 前端页面检查的最多尝试次数。
$FrontendHealthAttempts = 60
# 子进程存活检查的间隔，单位为秒。
$ProcessPollIntervalSeconds = 1

$RootDir = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $RootDir 'backend'
$FrontendDir = Join-Path $RootDir 'frontend'
$PythonExe = Join-Path $BackendDir '.venv/Scripts/python.exe'
$ViteCmd = Join-Path $FrontendDir 'node_modules/.bin/vite.cmd'
$LogDir = Join-Path $RootDir '.dev-logs'
$BackendLog = Join-Path $LogDir 'backend.log'
$BackendErrorLog = Join-Path $LogDir 'backend-error.log'
$FrontendLog = Join-Path $LogDir 'frontend.log'
$FrontendErrorLog = Join-Path $LogDir 'frontend-error.log'

# 检查目标端口能否在本地回环地址绑定。
function Test-PortAvailable {
    param([int]$Port)

    $listener = [System.Net.Sockets.TcpListener]::new(
        [System.Net.IPAddress]::Parse($DevHost), $Port
    )
    try {
        $listener.Start()
        return $true
    } catch [System.Net.Sockets.SocketException] {
        return $false
    } finally {
        $listener.Stop()
    }
}

# 从首选端口开始寻找空闲端口，保留已分配给另一服务的端口。
function Find-AvailablePort {
    param([int]$PreferredPort, [int]$ReservedPort = 0)

    for ($offset = 0; $offset -le $MaxPortShift; $offset++) {
        $candidate = $PreferredPort + $offset
        if ($candidate -le 65535 -and $candidate -ne $ReservedPort -and (Test-PortAvailable $candidate)) {
            return $candidate
        }
    }
    throw "端口 $PreferredPort 起连续 $($MaxPortShift + 1) 个端口均不可用。"
}

# 等待指定 URL 可访问，同时检查启动进程是否提前退出。
function Wait-ForUrl {
    param([string]$Url, [System.Diagnostics.Process]$Process, [int]$Attempts)

    for ($attempt = 0; $attempt -lt $Attempts; $attempt++) {
        if ($Process.HasExited) {
            throw "服务进程提前退出：$Url"
        }
        try {
            $response = Invoke-WebRequest -Uri $Url -TimeoutSec 2
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400) {
                return
            }
        } catch {
            # 启动期间的连接失败和 HTTP 超时都由外层次数限制处理。
        }
        Start-Sleep -Milliseconds $HealthPollIntervalMs
    }
    throw "等待服务超时：$Url"
}

# 只结束本脚本启动的进程树，避免影响原本占用端口的程序。
function Stop-StartedProcess {
    param([System.Diagnostics.Process]$Process)

    if ($null -eq $Process -or $Process.HasExited) {
        return
    }
    & taskkill.exe /PID $Process.Id /T /F *> $null
}

if (-not (Test-Path $PythonExe)) {
    throw '缺少 backend/.venv/Scripts/python.exe，请先在 backend 中创建并安装虚拟环境。'
}
if (-not (Test-Path $ViteCmd)) {
    throw '缺少 frontend/node_modules，请先在 frontend 中运行 npm install。'
}

$selectedBackendPort = Find-AvailablePort $BackendPort
$selectedFrontendPort = Find-AvailablePort $FrontendPort $selectedBackendPort
$backendUrl = "http://${DevHost}:${selectedBackendPort}"
$frontendUrl = "http://${DevHost}:${selectedFrontendPort}"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

$backendProcess = $null
$frontendProcess = $null
try {
    Write-Host "启动后端：$backendUrl"
    $backendProcess = Start-Process -FilePath $PythonExe `
        -ArgumentList @('-m', 'uvicorn', 'app.main:app', '--host', $DevHost, '--port', $selectedBackendPort) `
        -WorkingDirectory $BackendDir -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $BackendLog -RedirectStandardError $BackendErrorLog
    Wait-ForUrl "$backendUrl/api/health" $backendProcess $BackendHealthAttempts

    # Vite 读取这两个环境变量，以便使用实际端口并代理到实际后端。
    $env:BACKEND_TARGET = $backendUrl
    $env:FRONTEND_PORT = [string]$selectedFrontendPort
    Write-Host "启动前端：$frontendUrl"
    $frontendProcess = Start-Process -FilePath $env:ComSpec `
        -ArgumentList @('/d', '/s', '/c', 'npm run dev') `
        -WorkingDirectory $FrontendDir -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $FrontendLog -RedirectStandardError $FrontendErrorLog
    Wait-ForUrl $frontendUrl $frontendProcess $FrontendHealthAttempts

    Write-Host "前端工作台：$frontendUrl"
    Write-Host "后端健康检查：$backendUrl/api/health"
    Write-Host "日志：$LogDir"
    Write-Host '按 Ctrl+C 停止前后端。'
    while (-not $backendProcess.HasExited -and -not $frontendProcess.HasExited) {
        Start-Sleep -Seconds $ProcessPollIntervalSeconds
    }
    throw '前端或后端进程已退出，请查看日志。'
} finally {
    Stop-StartedProcess $frontendProcess
    Stop-StartedProcess $backendProcess
    Write-Host '本次启动的服务已停止。'
}
