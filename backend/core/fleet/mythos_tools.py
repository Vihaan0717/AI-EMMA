"""
MYTHOS Defensive Cybersecurity Tools
=====================================
12 sandboxed, read-only defensive tools for network diagnostics,
code analysis, file integrity, and system posture assessment.

All tools follow the Sentinel sandboxing pattern:
- asyncio.create_subprocess_exec (no shell=True)
- Strict input validation via regex
- Timeout enforcement on all subprocess calls
- No offensive/exploit capabilities

Architecture Pattern: Anthropic's "Tool Use" with clear namespacing
and token-efficient responses.
"""

import asyncio
import hashlib
import os
import platform
import re
import socket
import ssl
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, List
from pathlib import Path

logger = logging.getLogger("JARVIS.MythosTools")

# ──────────────────────────────────────────────────────────────────────
# INPUT VALIDATION (Shared sandbox boundary)
# ──────────────────────────────────────────────────────────────────────

def _validate_target(target: str) -> bool:
    """Validates hostnames, IPs, and domains. Blocks injection attempts."""
    pattern = re.compile(r"^[a-zA-Z0-9\-\.]+$")
    return bool(pattern.match(target)) and len(target) < 256

def _validate_path(path: str) -> bool:
    """Validates file paths. Blocks traversal attacks."""
    normalized = os.path.normpath(path)
    # Block any path that escapes user workspace
    forbidden = ["..", "\\\\", "//", "/etc", "/root", "C:\\Windows\\System32"]
    return not any(f in normalized for f in forbidden)

def _utc_timestamp() -> str:
    """Returns current UTC timestamp in military format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ──────────────────────────────────────────────────────────────────────
# TOOL 1: PORT ENUMERATION
# ──────────────────────────────────────────────────────────────────────

async def check_open_ports(target: str, scan_type: str = "quick", timeout: int = 60) -> Dict:
    """
    Wraps Sentinel's nmap for port enumeration.
    Scan types: quick (top 100), stealth (SYN), ping (sweep).
    """
    if not _validate_target(target):
        return {"status": "BLOCKED", "reason": f"Invalid target format: {target}", "timestamp": _utc_timestamp()}

    ALLOWED_SCANS = {
        "quick": ["-F", "-T4"],
        "stealth": ["-sS", "-T3"],
        "ping": ["-sn"],
    }
    if scan_type not in ALLOWED_SCANS:
        return {"status": "ERROR", "reason": f"Scan type '{scan_type}' not permitted", "timestamp": _utc_timestamp()}

    cmd = ["nmap"] + ALLOWED_SCANS[scan_type] + [target]
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        if process.returncode == 0:
            return {"status": "OK", "output": stdout.decode("utf-8").strip(), "timestamp": _utc_timestamp()}
        return {"status": "ERROR", "output": stderr.decode("utf-8").strip(), "timestamp": _utc_timestamp()}
    except asyncio.TimeoutError:
        process.kill()
        return {"status": "TIMEOUT", "reason": f"Scan exceeded {timeout}s", "timestamp": _utc_timestamp()}
    except FileNotFoundError:
        return {"status": "ERROR", "reason": "nmap not found in PATH", "timestamp": _utc_timestamp()}
    except Exception as e:
        return {"status": "ERROR", "reason": str(e), "timestamp": _utc_timestamp()}


# ──────────────────────────────────────────────────────────────────────
# TOOL 2: ACTIVE CONNECTIONS
# ──────────────────────────────────────────────────────────────────────

async def check_active_connections(timeout: int = 15) -> Dict:
    """Retrieves active network connections via netstat."""
    is_windows = platform.system() == "Windows"
    cmd = ["netstat", "-ano"] if is_windows else ["netstat", "-tuln"]
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        if process.returncode == 0:
            lines = stdout.decode("utf-8").strip().split("\n")
            # Parse into structured data
            connections = []
            for line in lines[4:]:  # Skip header lines
                parts = line.split()
                if len(parts) >= 4:
                    connections.append({
                        "protocol": parts[0],
                        "local_address": parts[1],
                        "foreign_address": parts[2],
                        "state": parts[3] if len(parts) > 3 else "N/A",
                        "pid": parts[4] if len(parts) > 4 else "N/A"
                    })
            return {
                "status": "OK",
                "total_connections": len(connections),
                "connections": connections[:50],  # Cap to prevent token overflow
                "timestamp": _utc_timestamp()
            }
        return {"status": "ERROR", "output": stderr.decode("utf-8").strip(), "timestamp": _utc_timestamp()}
    except asyncio.TimeoutError:
        return {"status": "TIMEOUT", "timestamp": _utc_timestamp()}
    except Exception as e:
        return {"status": "ERROR", "reason": str(e), "timestamp": _utc_timestamp()}


# ──────────────────────────────────────────────────────────────────────
# TOOL 3: DNS RECORDS
# ──────────────────────────────────────────────────────────────────────

async def analyze_dns_records(domain: str, timeout: int = 10) -> Dict:
    """DNS lookup for domain security analysis using nslookup."""
    if not _validate_target(domain):
        return {"status": "BLOCKED", "reason": f"Invalid domain: {domain}", "timestamp": _utc_timestamp()}

    cmd = ["nslookup", domain]
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        output = stdout.decode("utf-8").strip()
        return {"status": "OK", "output": output, "domain": domain, "timestamp": _utc_timestamp()}
    except asyncio.TimeoutError:
        return {"status": "TIMEOUT", "domain": domain, "timestamp": _utc_timestamp()}
    except Exception as e:
        return {"status": "ERROR", "reason": str(e), "timestamp": _utc_timestamp()}


# ──────────────────────────────────────────────────────────────────────
# TOOL 4: SSL/TLS CERTIFICATE CHECK
# ──────────────────────────────────────────────────────────────────────

async def check_ssl_certificate(hostname: str, port: int = 443) -> Dict:
    """TLS/SSL certificate validation and expiry check."""
    if not _validate_target(hostname):
        return {"status": "BLOCKED", "reason": f"Invalid hostname: {hostname}", "timestamp": _utc_timestamp()}

    try:
        ctx = ssl.create_default_context()
        loop = asyncio.get_event_loop()

        def _get_cert():
            with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
                s.settimeout(10)
                s.connect((hostname, port))
                return s.getpeercert()

        cert = await loop.run_in_executor(None, _get_cert)

        # Parse certificate details
        subject = dict(x[0] for x in cert.get("subject", ()))
        issuer = dict(x[0] for x in cert.get("issuer", ()))
        not_after = cert.get("notAfter", "Unknown")
        not_before = cert.get("notBefore", "Unknown")
        san = [entry[1] for entry in cert.get("subjectAltName", ())]

        return {
            "status": "OK",
            "hostname": hostname,
            "subject_cn": subject.get("commonName", "N/A"),
            "issuer_cn": issuer.get("commonName", "N/A"),
            "issuer_org": issuer.get("organizationName", "N/A"),
            "valid_from": not_before,
            "valid_until": not_after,
            "san_domains": san[:10],
            "serial_number": cert.get("serialNumber", "N/A"),
            "timestamp": _utc_timestamp()
        }
    except ssl.SSLCertVerificationError as e:
        return {"status": "CERT_INVALID", "hostname": hostname, "reason": str(e), "timestamp": _utc_timestamp()}
    except Exception as e:
        return {"status": "ERROR", "hostname": hostname, "reason": str(e), "timestamp": _utc_timestamp()}


# ──────────────────────────────────────────────────────────────────────
# TOOL 5: FILE PERMISSIONS AUDIT
# ──────────────────────────────────────────────────────────────────────

async def scan_file_permissions(directory: str, timeout: int = 15) -> Dict:
    """Filesystem permission audit for a given directory."""
    if not _validate_path(directory):
        return {"status": "BLOCKED", "reason": "Path validation failed", "timestamp": _utc_timestamp()}

    if not os.path.isdir(directory):
        return {"status": "ERROR", "reason": f"Directory not found: {directory}", "timestamp": _utc_timestamp()}

    is_windows = platform.system() == "Windows"
    if is_windows:
        cmd = ["icacls", directory]
    else:
        cmd = ["ls", "-la", directory]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        output = stdout.decode("utf-8").strip()
        return {
            "status": "OK",
            "directory": directory,
            "permissions_output": output[:3000],  # Cap token length
            "timestamp": _utc_timestamp()
        }
    except Exception as e:
        return {"status": "ERROR", "reason": str(e), "timestamp": _utc_timestamp()}


# ──────────────────────────────────────────────────────────────────────
# TOOL 6: FILE INTEGRITY (HASH)
# ──────────────────────────────────────────────────────────────────────

async def hash_file_integrity(file_path: str, expected_hash: Optional[str] = None) -> Dict:
    """SHA-256 hash verification for file integrity checking."""
    if not _validate_path(file_path):
        return {"status": "BLOCKED", "reason": "Path validation failed", "timestamp": _utc_timestamp()}

    if not os.path.isfile(file_path):
        return {"status": "ERROR", "reason": f"File not found: {file_path}", "timestamp": _utc_timestamp()}

    try:
        loop = asyncio.get_event_loop()

        def _compute_hash():
            sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()

        computed_hash = await loop.run_in_executor(None, _compute_hash)
        file_size = os.path.getsize(file_path)

        result = {
            "status": "OK",
            "file": file_path,
            "sha256": computed_hash,
            "file_size_bytes": file_size,
            "timestamp": _utc_timestamp()
        }

        if expected_hash:
            match = computed_hash.lower() == expected_hash.lower()
            result["integrity_check"] = "PASS" if match else "FAIL"
            result["expected_hash"] = expected_hash

        return result
    except Exception as e:
        return {"status": "ERROR", "reason": str(e), "timestamp": _utc_timestamp()}


# ──────────────────────────────────────────────────────────────────────
# TOOL 7: RUNNING PROCESSES
# ──────────────────────────────────────────────────────────────────────

async def check_running_processes(timeout: int = 15) -> Dict:
    """Process enumeration for suspicious activity detection."""
    is_windows = platform.system() == "Windows"
    if is_windows:
        cmd = ["tasklist", "/FO", "CSV", "/NH"]
    else:
        cmd = ["ps", "aux"]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        output = stdout.decode("utf-8").strip()

        # Parse CSV format (Windows) into structured data
        processes = []
        for line in output.split("\n")[:100]:  # Cap at 100 processes
            if is_windows:
                parts = line.strip().strip('"').split('","')
                if len(parts) >= 5:
                    processes.append({
                        "name": parts[0].strip('"'),
                        "pid": parts[1].strip('"'),
                        "session": parts[2].strip('"'),
                        "memory": parts[4].strip('"') if len(parts) > 4 else "N/A"
                    })
            else:
                parts = line.split(None, 10)
                if len(parts) >= 11:
                    processes.append({
                        "user": parts[0],
                        "pid": parts[1],
                        "cpu": parts[2],
                        "mem": parts[3],
                        "command": parts[10]
                    })

        return {
            "status": "OK",
            "total_processes": len(processes),
            "processes": processes,
            "timestamp": _utc_timestamp()
        }
    except Exception as e:
        return {"status": "ERROR", "reason": str(e), "timestamp": _utc_timestamp()}


# ──────────────────────────────────────────────────────────────────────
# TOOL 8: WINDOWS EVENT LOGS
# ──────────────────────────────────────────────────────────────────────

async def parse_event_logs(log_name: str = "Security", max_events: int = 50, timeout: int = 20) -> Dict:
    """Windows Event Log parsing for security events."""
    if platform.system() != "Windows":
        return {"status": "SKIPPED", "reason": "Windows-only tool", "timestamp": _utc_timestamp()}

    # Validate log name to prevent injection
    allowed_logs = ["Security", "System", "Application"]
    if log_name not in allowed_logs:
        return {"status": "BLOCKED", "reason": f"Log '{log_name}' not in allowed list", "timestamp": _utc_timestamp()}

    cmd = [
        "powershell", "-NoProfile", "-Command",
        f"Get-EventLog -LogName {log_name} -Newest {max_events} | Select-Object TimeGenerated,EntryType,Source,EventID,Message | ConvertTo-Json -Depth 2"
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        output = stdout.decode("utf-8").strip()

        import json
        try:
            events = json.loads(output) if output else []
        except Exception:
            events = output[:3000]

        return {
            "status": "OK",
            "log_name": log_name,
            "events_retrieved": max_events,
            "events": events,
            "timestamp": _utc_timestamp()
        }
    except asyncio.TimeoutError:
        return {"status": "TIMEOUT", "timestamp": _utc_timestamp()}
    except Exception as e:
        return {"status": "ERROR", "reason": str(e), "timestamp": _utc_timestamp()}


# ──────────────────────────────────────────────────────────────────────
# TOOL 9: FIREWALL RULES
# ──────────────────────────────────────────────────────────────────────

async def check_firewall_rules(direction: str = "Inbound", timeout: int = 15) -> Dict:
    """Windows Firewall rule enumeration."""
    if platform.system() != "Windows":
        return {"status": "SKIPPED", "reason": "Windows-only tool", "timestamp": _utc_timestamp()}

    if direction not in ("Inbound", "Outbound"):
        return {"status": "BLOCKED", "reason": "Direction must be Inbound or Outbound", "timestamp": _utc_timestamp()}

    cmd = [
        "powershell", "-NoProfile", "-Command",
        f"Get-NetFirewallRule -Direction {direction} -Enabled True | Select-Object -First 30 DisplayName,Action,Profile | ConvertTo-Json"
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        output = stdout.decode("utf-8").strip()

        import json
        try:
            rules = json.loads(output) if output else []
        except Exception:
            rules = output[:3000]

        return {
            "status": "OK",
            "direction": direction,
            "rules": rules,
            "timestamp": _utc_timestamp()
        }
    except Exception as e:
        return {"status": "ERROR", "reason": str(e), "timestamp": _utc_timestamp()}


# ──────────────────────────────────────────────────────────────────────
# TOOL 10: HTTP SECURITY HEADERS
# ──────────────────────────────────────────────────────────────────────

async def analyze_http_headers(url: str, timeout: int = 10) -> Dict:
    """HTTP security header analysis (CSP, HSTS, X-Frame-Options, etc.)."""
    if not _validate_target(url.replace("https://", "").replace("http://", "").split("/")[0]):
        return {"status": "BLOCKED", "reason": f"Invalid URL: {url}", "timestamp": _utc_timestamp()}

    # Use curl for header-only fetch (no body download)
    clean_url = url if url.startswith("http") else f"https://{url}"
    cmd = ["curl", "-sI", "--max-time", str(timeout), clean_url]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout + 5)
        headers_raw = stdout.decode("utf-8").strip()

        # Parse headers
        headers = {}
        for line in headers_raw.split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                headers[key.strip().lower()] = val.strip()

        # Security header checklist
        security_headers = {
            "strict-transport-security": headers.get("strict-transport-security", "MISSING"),
            "content-security-policy": headers.get("content-security-policy", "MISSING"),
            "x-frame-options": headers.get("x-frame-options", "MISSING"),
            "x-content-type-options": headers.get("x-content-type-options", "MISSING"),
            "x-xss-protection": headers.get("x-xss-protection", "MISSING"),
            "referrer-policy": headers.get("referrer-policy", "MISSING"),
            "permissions-policy": headers.get("permissions-policy", "MISSING"),
        }

        missing = [k for k, v in security_headers.items() if v == "MISSING"]
        grade = "A" if len(missing) == 0 else "B" if len(missing) <= 2 else "C" if len(missing) <= 4 else "F"

        return {
            "status": "OK",
            "url": clean_url,
            "security_headers": security_headers,
            "missing_headers": missing,
            "grade": grade,
            "timestamp": _utc_timestamp()
        }
    except Exception as e:
        return {"status": "ERROR", "reason": str(e), "timestamp": _utc_timestamp()}


# ──────────────────────────────────────────────────────────────────────
# TOOL 11: WHOIS LOOKUP
# ──────────────────────────────────────────────────────────────────────

async def whois_lookup(domain: str, timeout: int = 10) -> Dict:
    """Domain registration and ownership lookup."""
    if not _validate_target(domain):
        return {"status": "BLOCKED", "reason": f"Invalid domain: {domain}", "timestamp": _utc_timestamp()}

    is_windows = platform.system() == "Windows"
    cmd = ["whois", domain] if not is_windows else ["powershell", "-NoProfile", "-Command", f"nslookup -type=SOA {domain}"]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        output = stdout.decode("utf-8").strip()
        return {
            "status": "OK",
            "domain": domain,
            "whois_data": output[:3000],
            "timestamp": _utc_timestamp()
        }
    except Exception as e:
        return {"status": "ERROR", "reason": str(e), "timestamp": _utc_timestamp()}


# ──────────────────────────────────────────────────────────────────────
# TOOL 12: PASSWORD STRENGTH CHECKER
# ──────────────────────────────────────────────────────────────────────

def check_password_strength(password: str) -> Dict:
    """
    Password policy compliance checker.
    Does NOT store or log the password — only analyzes pattern strength.
    """
    checks = {
        "min_length_8": len(password) >= 8,
        "min_length_12": len(password) >= 12,
        "has_uppercase": bool(re.search(r"[A-Z]", password)),
        "has_lowercase": bool(re.search(r"[a-z]", password)),
        "has_digit": bool(re.search(r"\d", password)),
        "has_special": bool(re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", password)),
        "no_common_patterns": not bool(re.search(r"(123|abc|password|qwerty|admin|letmein)", password.lower())),
    }

    score = sum(checks.values())
    if score >= 7:
        strength = "STRONG"
    elif score >= 5:
        strength = "MODERATE"
    elif score >= 3:
        strength = "WEAK"
    else:
        strength = "CRITICAL"

    failed = [k for k, v in checks.items() if not v]

    return {
        "status": "OK",
        "strength": strength,
        "score": f"{score}/7",
        "checks": checks,
        "failed_checks": failed,
        "timestamp": _utc_timestamp()
    }


# ──────────────────────────────────────────────────────────────────────
# TOOL REGISTRY (for engine integration)
# ──────────────────────────────────────────────────────────────────────

MYTHOS_TOOL_REGISTRY = {
    "check_open_ports": {"fn": check_open_ports, "async": True, "category": "network"},
    "check_active_connections": {"fn": check_active_connections, "async": True, "category": "network"},
    "analyze_dns_records": {"fn": analyze_dns_records, "async": True, "category": "network"},
    "check_ssl_certificate": {"fn": check_ssl_certificate, "async": True, "category": "network"},
    "scan_file_permissions": {"fn": scan_file_permissions, "async": True, "category": "filesystem"},
    "hash_file_integrity": {"fn": hash_file_integrity, "async": True, "category": "filesystem"},
    "check_running_processes": {"fn": check_running_processes, "async": True, "category": "system"},
    "check_firewall_rules": {"fn": check_firewall_rules, "async": True, "category": "system"},
    "parse_event_logs": {"fn": parse_event_logs, "async": True, "category": "system"},
    "analyze_http_headers": {"fn": analyze_http_headers, "async": True, "category": "web"},
    "whois_lookup": {"fn": whois_lookup, "async": True, "category": "web"},
    "check_password_strength": {"fn": check_password_strength, "async": False, "category": "policy"},
}
