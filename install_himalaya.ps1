$ProgressPreference = 'SilentlyContinue'
$url = "https://github.com/pimalaya/himalaya/releases/download/v1.0.0/himalaya-windows-msvc.zip"
$zipPath = "$env:TEMP\himalaya.zip"
$extractPath = "c:\Users\anger\Desktop\JARVIS_Project\himalaya_bin"

Write-Host "Downloading Himalaya..."
Invoke-WebRequest -Uri $url -OutFile $zipPath

Write-Host "Extracting..."
Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

Write-Host "Done. Executable is at $extractPath\himalaya.exe"
