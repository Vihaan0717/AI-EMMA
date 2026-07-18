# NEXUS-X A10 Cognitive Sandbox Setup Script
# Run this to initialize the isolated 'Brain Lab' environment.

Write-Host "🌌 Initializing NEXUS-X A10 Cognitive Sandbox..." -ForegroundColor Cyan

# 1. Install Sandbox CLI
if (!(Get-Command sbx -ErrorAction SilentlyContinue)) {
    Write-Host "📥 Installing Sandbox CLI (sbx)..." -ForegroundColor Yellow
    winget install -h Docker.sbx
} else {
    Write-Host "✅ Sandbox CLI (sbx) already installed." -ForegroundColor Green
}

# 2. Create Brain Lab Folder
$SandboxPath = "NexusX_Sandbox"
if (!(Test-Path $SandboxPath)) {
    Write-Host "📁 Creating Brain Lab folder: $SandboxPath" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $SandboxPath
}

# 3. Launch the Isolated Environment
Write-Host "🚀 Launching Isolated Environment: nexus-brain" -ForegroundColor Cyan
Write-Host "Note: This will open a safe container for Telugu processing tools." -ForegroundColor Gray
# sbx run --name nexus-brain shell
