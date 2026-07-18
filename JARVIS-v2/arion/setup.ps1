Write-Host "Setting up ARION Environment on Windows..."

# Check Python
if (!(Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Host "Python not found. Please install Python 3.10+"
    exit 1
}

# Check Node.js
if (!(Get-Command "npm" -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js (npm) not found. Please install Node.js"
    exit 1
}

Write-Host "1. Installing Python dependencies..."
python -m pip install -r requirements.txt

Write-Host "2. Installing Node.js dependencies..."
cd whatsapp
npm install
cd ..

Write-Host "3. Note: Ollama needs to be installed manually from ollama.com"
Write-Host "Once installed in another terminal run: ollama run llama3:8b"

Write-Host "Setup Complete. Run 'python main.py' to start ARION."
