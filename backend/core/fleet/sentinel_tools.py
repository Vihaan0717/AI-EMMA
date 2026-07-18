import asyncio
import re
import platform
import logging

logger = logging.getLogger("JARVIS.SentinelTools")

# 1. THE SANDBOX (Strictly allowed commands and flags)
ALLOWED_SCANS = {
    "quick": ["-F", "-T4"],             # Fast scan for top 100 ports
    "stealth": ["-sS", "-T3"],          # SYN stealth scan
    "ping": ["-sn"],                    # Ping sweep (no port scan)
    "os_detect": ["-O", "--osscan-limit"] # OS detection
}

def is_valid_ip_or_domain(target: str) -> bool:
    """Basic regex to prevent command injection (e.g., 'localhost && rm -rf /')"""
    pattern = re.compile(r"^([a-zA-Z0-9\-\.]+)$")
    return bool(pattern.match(target))

async def execute_nmap_scan(target: str, scan_type: str = "quick", timeout: int = 60) -> str:
    """
    Executes a sandboxed nmap scan asynchronously.
    """
    if not is_valid_ip_or_domain(target):
        return f"[SECURITY BLOCK] Invalid target format: {target}"
    
    if scan_type not in ALLOWED_SCANS:
        return f"[ERROR] Scan type '{scan_type}' not in allowed list."

    # Build the safe command list
    cmd = ["nmap"] + ALLOWED_SCANS[scan_type] + [target]
    
    try:
        # Launch the process asynchronously WITHOUT shell=True
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait for the command to finish, with a strict timeout
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        
        if process.returncode == 0:
            return stdout.decode('utf-8').strip()
        else:
            return f"[ERROR] Nmap failed: {stderr.decode('utf-8').strip()}"
            
    except asyncio.TimeoutError:
        process.kill()
        return f"[TIMEOUT] Nmap scan on {target} exceeded {timeout} seconds and was killed."
    except FileNotFoundError:
        return "[ERROR] Nmap executable not found. Is it installed and in your system PATH?"
    except Exception as e:
        return f"[SYSTEM ERROR] {str(e)}"

async def execute_netstat(timeout: int = 15) -> str:
    """
    Retrieves active network connections asynchronously.
    """
    is_windows = platform.system() == "Windows"
    cmd = ["netstat", "-ano"] if is_windows else ["netstat", "-tuln"]
    
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        
        if process.returncode == 0:
            return stdout.decode('utf-8').strip()
        else:
            return f"[ERROR] Netstat failed: {stderr.decode('utf-8').strip()}"
            
    except asyncio.TimeoutError:
        process.kill()
        return "[TIMEOUT] Netstat command hung."
