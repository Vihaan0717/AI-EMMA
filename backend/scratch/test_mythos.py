"""
MYTHOS Agent — End-to-End Test Suite
=====================================
5 comprehensive tests validating all MYTHOS capabilities:
1. STRIDE Threat Model Assessment
2. Code Vulnerability Detection (OWASP)
3. Network Posture Analysis
4. Log Anomaly Detection
5. Incident Report Generation

Run: python -m pytest backend/scratch/test_mythos.py -v
  or: python backend/scratch/test_mythos.py  (standalone)
"""

import asyncio
import json
import sys
import os
import time
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.core.fleet.mythos_engine import MythosEngine, SEVERITY_MAP, STRIDE_CATEGORIES
from backend.core.fleet.mythos_tools import (
    check_password_strength,
    hash_file_integrity,
    _validate_target,
    _validate_path,
    MYTHOS_TOOL_REGISTRY,
)


# ──────────────────────────────────────────────────────────────────────
# TEST UTILITIES
# ──────────────────────────────────────────────────────────────────────

class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.checks = []
        self.output = None
        self.error = None
        self.duration_ms = 0

    def check(self, condition: bool, description: str):
        status = "PASS" if condition else "FAIL"
        self.checks.append({"status": status, "description": description})
        if not condition:
            self.passed = False

    def summary(self) -> str:
        total = len(self.checks)
        passed = sum(1 for c in self.checks if c["status"] == "PASS")
        status = "PASS" if self.passed else "FAIL"
        header = f"\n{'=' * 70}\n[{status}] TEST: {self.name} ({self.duration_ms:.0f}ms)\n{'=' * 70}"
        details = ""
        for c in self.checks:
            icon = "+" if c["status"] == "PASS" else "X"
            details += f"\n  [{icon}] {c['description']}"
        details += f"\n  Results: {passed}/{total} checks passed"
        return header + details


def run_async(coro):
    """Runs an async function synchronously."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ──────────────────────────────────────────────────────────────────────
# TEST 1: STRIDE THREAT MODEL
# ──────────────────────────────────────────────────────────────────────

def test_stride_threat_model():
    """
    Given a web app architecture description, MYTHOS should produce
    all 6 STRIDE categories with threats, severities, and mitigations.
    """
    result = TestResult("STRIDE Threat Model Assessment")
    result.passed = True
    start = time.time()

    engine = MythosEngine(ai_engine=None)  # Uses fallback (no API needed)

    architecture = """
    Web Application Architecture:
    - Frontend: React SPA served via Nginx reverse proxy
    - Backend: Python FastAPI with JWT authentication
    - Database: PostgreSQL with user credentials table
    - API: RESTful endpoints for user CRUD operations
    - File Storage: AWS S3 for user uploads
    - Messaging: RabbitMQ for async task processing
    """

    assessment = run_async(engine.stride_assessment(architecture))

    result.output = assessment

    # Check structure
    result.check(assessment.get("type") == "STRIDE_ASSESSMENT", "Response type is STRIDE_ASSESSMENT")
    result.check("result" in assessment, "Contains 'result' field")
    result.check("timestamp" in assessment, "Contains UTC timestamp")
    result.check(assessment.get("signature") == "— MYTHOS // END TRANSMISSION", "Contains MYTHOS signature")

    # Check STRIDE coverage
    stride_result = assessment.get("result", {})
    threats = stride_result.get("threats", {})

    result.check("S" in threats, "Spoofing threat identified")
    result.check("T" in threats, "Tampering threat identified")
    result.check("R" in threats, "Repudiation threat identified")
    result.check("I" in threats, "Information Disclosure threat identified")
    result.check("D" in threats, "Denial of Service threat identified")
    result.check("E" in threats, "Elevation of Privilege threat identified")

    # Check each threat has required fields
    for key, threat in threats.items():
        result.check("threat" in threat, f"STRIDE[{key}] has 'threat' description")
        result.check("severity" in threat, f"STRIDE[{key}] has 'severity' rating")
        result.check("mitigation" in threat, f"STRIDE[{key}] has 'mitigation' recommendation")

    # Check overall risk assessment
    result.check("overall_risk" in stride_result, "Contains overall risk assessment")
    result.check(stride_result.get("overall_risk") in ("CRITICAL", "HIGH", "MEDIUM", "LOW"), "Overall risk is valid severity level")

    # Check reasoning/chain-of-thought
    result.check("reasoning" in stride_result, "Contains chain-of-thought reasoning")

    result.duration_ms = (time.time() - start) * 1000
    return result


# ──────────────────────────────────────────────────────────────────────
# TEST 2: CODE VULNERABILITY DETECTION
# ──────────────────────────────────────────────────────────────────────

def test_code_vulnerability_detection():
    """
    Given Python code with SQL injection + hardcoded secrets,
    MYTHOS should flag both with correct severity levels.
    """
    result = TestResult("Code Vulnerability Detection (OWASP)")
    result.passed = True
    start = time.time()

    engine = MythosEngine()

    # Deliberately vulnerable code
    vulnerable_code = '''
import sqlite3
import os
import pickle
import hashlib

# VULNERABILITY 1: Hardcoded secret
API_KEY = "sk-abc123-super-secret-key-do-not-share"
password = "admin123"

# VULNERABILITY 2: SQL Injection
def get_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE name = '{username}'")
    return cursor.fetchone()

# VULNERABILITY 3: Command injection
def run_report(report_name):
    os.system(f"generate_report {report_name}")

# VULNERABILITY 4: Insecure deserialization
def load_user_data(data):
    return pickle.loads(data)

# VULNERABILITY 5: Weak crypto
def hash_password(pwd):
    return hashlib.md5(pwd.encode()).hexdigest()

# VULNERABILITY 6: Debug mode
DEBUG = True
'''

    scan = engine.scan_code_security(vulnerable_code, filename="vulnerable_app.py")

    result.output = scan

    # Check structure
    result.check(scan.get("type") == "CODE_SCAN", "Response type is CODE_SCAN")
    result.check(scan.get("filename") == "vulnerable_app.py", "Correct filename reported")
    result.check("findings" in scan, "Contains findings list")
    result.check("severity_breakdown" in scan, "Contains severity breakdown")
    result.check(scan.get("signature") == "— MYTHOS // END TRANSMISSION", "Contains MYTHOS signature")

    # Check that vulnerabilities were detected
    findings = scan.get("findings", [])
    vuln_types = [f["vulnerability"] for f in findings]

    result.check("SQL_INJECTION" in vuln_types, "SQL Injection detected")
    result.check("HARDCODED_SECRETS" in vuln_types, "Hardcoded secrets detected")
    result.check("COMMAND_INJECTION" in vuln_types, "Command injection detected")
    result.check("INSECURE_DESERIALIZATION" in vuln_types, "Insecure deserialization detected")
    result.check("WEAK_CRYPTO" in vuln_types, "Weak cryptography detected")
    result.check("DEBUG_ENABLED" in vuln_types, "Debug mode detected")

    # Check severity classification
    result.check(scan.get("overall_risk") == "CRITICAL", "Overall risk is CRITICAL (SQL injection + secrets)")
    result.check(scan.get("total_findings", 0) >= 6, f"Found at least 6 vulnerabilities (got {scan.get('total_findings', 0)})")

    # Check OWASP mapping exists
    for f in findings[:3]:
        result.check("owasp" in f, f"Finding '{f.get('vulnerability')}' has OWASP mapping")
        result.check("fix" in f, f"Finding '{f.get('vulnerability')}' has fix recommendation")
        result.check("codename" in f, f"Finding '{f.get('vulnerability')}' has severity codename")

    # Check severity codenames
    critical_findings = [f for f in findings if f.get("severity") == "CRITICAL"]
    result.check(
        all(f.get("codename") == "HYDRA" for f in critical_findings),
        "All CRITICAL findings use HYDRA codename"
    )

    result.duration_ms = (time.time() - start) * 1000
    return result


# ──────────────────────────────────────────────────────────────────────
# TEST 3: NETWORK POSTURE ANALYSIS (Tool-level validation)
# ──────────────────────────────────────────────────────────────────────

def test_network_posture_tools():
    """
    Tests the defensive tools directly:
    - Password strength checker
    - File integrity hash
    - Input validation
    - Tool registry completeness
    """
    result = TestResult("Defensive Tools & Network Posture Validation")
    result.passed = True
    start = time.time()

    # Test 3a: Password strength checker
    weak_result = check_password_strength("123456")
    result.check(weak_result["strength"] == "CRITICAL", f"'123456' is CRITICAL strength (got: {weak_result['strength']})")
    result.check(not weak_result["checks"]["min_length_8"], "'123456' fails minimum length")
    result.check(not weak_result["checks"]["no_common_patterns"], "'123456' matches common pattern")

    strong_result = check_password_strength("Str0ng!P@ssw0rd#2026")
    result.check(strong_result["strength"] == "STRONG", f"Complex password is STRONG (got: {strong_result['strength']})")
    result.check(strong_result["checks"]["has_uppercase"], "Complex password has uppercase")
    result.check(strong_result["checks"]["has_special"], "Complex password has special chars")

    moderate_result = check_password_strength("HelloWorld123")
    result.check(moderate_result["strength"] in ("MODERATE", "STRONG"), f"'HelloWorld123' is MODERATE or STRONG (got: {moderate_result['strength']})")

    # Test 3b: Input validation (sandbox boundary)
    result.check(_validate_target("google.com"), "Valid domain passes validation")
    result.check(_validate_target("192.168.1.1"), "Valid IP passes validation")
    result.check(not _validate_target("google.com && rm -rf /"), "Command injection blocked")
    result.check(not _validate_target("target; cat /etc/passwd"), "Semicolon injection blocked")
    result.check(not _validate_target(""), "Empty string blocked")

    result.check(_validate_path("C:\\Users\\test\\file.txt"), "Valid Windows path passes")
    result.check(not _validate_path("../../etc/passwd"), "Path traversal blocked")

    # Test 3c: File integrity hash (on this test file itself)
    test_file_path = os.path.abspath(__file__)
    if os.path.exists(test_file_path):
        hash_result = run_async(hash_file_integrity(test_file_path))
        result.check(hash_result["status"] == "OK", "File integrity hash succeeds on test file")
        result.check(len(hash_result.get("sha256", "")) == 64, "SHA-256 hash is 64 characters")
        result.check(hash_result.get("file_size_bytes", 0) > 0, "File size is reported")

    # Test 3d: Tool registry completeness
    result.check(len(MYTHOS_TOOL_REGISTRY) == 12, f"Tool registry has 12 tools (got: {len(MYTHOS_TOOL_REGISTRY)})")

    expected_tools = [
        "check_open_ports", "check_active_connections", "analyze_dns_records",
        "check_ssl_certificate", "scan_file_permissions", "hash_file_integrity",
        "check_running_processes", "check_firewall_rules", "parse_event_logs",
        "analyze_http_headers", "whois_lookup", "check_password_strength"
    ]
    for tool_name in expected_tools:
        result.check(tool_name in MYTHOS_TOOL_REGISTRY, f"Tool '{tool_name}' registered")

    # Check tool metadata
    for name, meta in MYTHOS_TOOL_REGISTRY.items():
        result.check("fn" in meta, f"Tool '{name}' has function reference")
        result.check("category" in meta, f"Tool '{name}' has category")
        result.check(meta["category"] in ("network", "filesystem", "system", "web", "policy"),
                     f"Tool '{name}' category is valid: {meta.get('category')}")

    result.output = {
        "weak_password": weak_result,
        "strong_password": strong_result,
        "tool_registry_count": len(MYTHOS_TOOL_REGISTRY),
    }

    result.duration_ms = (time.time() - start) * 1000
    return result


# ──────────────────────────────────────────────────────────────────────
# TEST 4: LOG ANOMALY DETECTION
# ──────────────────────────────────────────────────────────────────────

def test_log_anomaly_detection():
    """
    Given fabricated auth logs with brute-force pattern,
    MYTHOS should detect the anomaly.
    """
    result = TestResult("Log Anomaly Detection")
    result.passed = True
    start = time.time()

    engine = MythosEngine()

    # Fabricated security logs with multiple attack patterns
    fake_logs = """
2026-06-10 02:14:01 [AUTH] Login successful for user 'admin' from 192.168.1.10
2026-06-10 02:15:33 [AUTH] Failed login attempt for user 'admin' from 10.0.0.55
2026-06-10 02:15:35 [AUTH] Failed login attempt for user 'admin' from 10.0.0.55
2026-06-10 02:15:36 [AUTH] Failed login attempt for user 'admin' from 10.0.0.55
2026-06-10 02:15:38 [AUTH] Failed login attempt for user 'root' from 10.0.0.55
2026-06-10 02:15:39 [AUTH] Failed login attempt for user 'root' from 10.0.0.55
2026-06-10 02:15:41 [AUTH] Failed login attempt for user 'root' from 10.0.0.55
2026-06-10 02:15:42 [AUTH] Failed login attempt for user 'admin' from 10.0.0.55
2026-06-10 02:15:44 [AUTH] Failed login attempt for user 'admin' from 10.0.0.55
2026-06-10 02:15:45 [AUTH] Failed login attempt for user 'admin' from 10.0.0.55
2026-06-10 02:15:47 [AUTH] Failed login attempt for user 'admin' from 10.0.0.55
2026-06-10 02:15:48 [AUTH] Failed login attempt for user 'admin' from 10.0.0.55
2026-06-10 02:16:01 [SYS] Suspicious unauthorized privilege escalation attempt detected
2026-06-10 02:17:00 [NET] Large transfer detected - possible data exfiltration to 203.0.113.42
2026-06-10 03:30:15 [AUTH] Login successful for user 'backup_svc' from 10.0.0.99
2026-06-10 08:00:01 [AUTH] Login successful for user 'admin' from 192.168.1.10
"""

    analysis = engine.parse_security_logs(fake_logs)

    result.output = analysis

    # Check structure
    result.check(analysis.get("type") == "LOG_ANALYSIS", "Response type is LOG_ANALYSIS")
    result.check("anomalies" in analysis, "Contains anomalies list")
    result.check("total_anomalies" in analysis, "Contains total anomaly count")
    result.check(analysis.get("signature") == "— MYTHOS // END TRANSMISSION", "Contains MYTHOS signature")

    # Check anomaly detection
    anomalies = analysis.get("anomalies", [])
    anomaly_types = [a["type"] for a in anomalies]

    result.check("BRUTE_FORCE_ATTEMPT" in anomaly_types, "Brute-force attack pattern detected")
    result.check("PRIVILEGE_ESCALATION_ATTEMPT" in anomaly_types, "Privilege escalation attempt detected")
    result.check("DATA_EXFILTRATION_INDICATOR" in anomaly_types, "Data exfiltration indicator detected")
    result.check("OFF_HOURS_ACTIVITY" in anomaly_types, "Off-hours activity detected")

    # Check brute-force details
    brute_force = [a for a in anomalies if a["type"] == "BRUTE_FORCE_ATTEMPT"]
    if brute_force:
        bf = brute_force[0]
        result.check(bf.get("source") == "10.0.0.55", f"Brute-force source IP identified (got: {bf.get('source')})")
        result.check(bf.get("count", 0) >= 10, f"Detected >=10 failed attempts (got: {bf.get('count', 0)})")
        result.check(bf.get("severity") == "CRITICAL", "Brute-force severity is CRITICAL (>=10 attempts)")
        result.check(bf.get("codename") == "HYDRA", "Brute-force codename is HYDRA")
        result.check("T1110" in bf.get("mitre", ""), "MITRE ATT&CK T1110 mapped")

    # Check overall risk
    result.check(analysis.get("overall_risk") == "CRITICAL", "Overall risk is CRITICAL")

    result.duration_ms = (time.time() - start) * 1000
    return result


# ──────────────────────────────────────────────────────────────────────
# TEST 5: INCIDENT REPORT GENERATION
# ──────────────────────────────────────────────────────────────────────

def test_incident_report_generation():
    """
    Given a set of findings, MYTHOS produces a structured incident report
    with MITRE ATT&CK mapping.
    """
    result = TestResult("Incident Report Generation")
    result.passed = True
    start = time.time()

    engine = MythosEngine(ai_engine=None)

    # Sample findings from various analysis types
    findings = [
        {
            "type": "SQL_INJECTION",
            "severity": "CRITICAL",
            "detail": "Unsanitized user input in database query on line 42",
            "mitigation": "Use parameterized queries",
            "mitre": "T1190 — Exploit Public-Facing Application"
        },
        {
            "type": "BRUTE_FORCE_ATTEMPT",
            "severity": "CRITICAL",
            "detail": "15 failed login attempts from IP 10.0.0.55 in 2 minutes",
            "mitigation": "Implement account lockout and rate limiting",
            "mitre": "T1110 — Brute Force"
        },
        {
            "type": "HARDCODED_SECRETS",
            "severity": "CRITICAL",
            "detail": "API key exposed in source code: config.py line 12",
            "mitigation": "Move to environment variables, rotate key immediately",
            "mitre": "T1552 — Unsecured Credentials"
        },
        {
            "type": "SUSPICIOUS_PORT",
            "severity": "HIGH",
            "detail": "Connection to port 4444 (common reverse shell port)",
            "mitigation": "Investigate process and block port in firewall",
            "mitre": "T1571 — Non-Standard Port"
        },
        {
            "type": "WEAK_CRYPTO",
            "severity": "MEDIUM",
            "detail": "MD5 used for password hashing",
            "mitigation": "Migrate to bcrypt or argon2",
            "mitre": "T1110.002 — Password Cracking"
        },
    ]

    report = run_async(engine.generate_incident_report(findings, context="Monthly security audit of NEXUS-X fleet"))

    result.output = report

    # Check structure
    result.check(report.get("type") == "INCIDENT_REPORT", "Response type is INCIDENT_REPORT")
    result.check("executive_summary" in report, "Contains executive summary")
    result.check("severity_breakdown" in report, "Contains severity breakdown")
    result.check("mitre_tactics" in report, "Contains MITRE tactics list")
    result.check("findings" in report, "Contains findings list")
    result.check(report.get("signature") == "— MYTHOS // END TRANSMISSION", "Contains MYTHOS signature")

    # Check severity breakdown
    breakdown = report.get("severity_breakdown", {})
    result.check(breakdown.get("CRITICAL") == 3, f"3 CRITICAL findings counted (got: {breakdown.get('CRITICAL')})")
    result.check(breakdown.get("HIGH") == 1, f"1 HIGH finding counted (got: {breakdown.get('HIGH')})")
    result.check(breakdown.get("MEDIUM") == 1, f"1 MEDIUM finding counted (got: {breakdown.get('MEDIUM')})")

    # Check MITRE tactics are extracted
    mitre = report.get("mitre_tactics", [])
    result.check(len(mitre) >= 4, f"At least 4 MITRE tactics mapped (got: {len(mitre)})")
    result.check(any("T1110" in t for t in mitre), "T1110 (Brute Force) in MITRE tactics")
    result.check(any("T1190" in t for t in mitre), "T1190 (Exploit Public-Facing App) in MITRE tactics")

    # Check executive summary content
    exec_sum = report.get("executive_summary", "")
    result.check("HYDRA" in exec_sum, "Executive summary contains HYDRA classification")
    result.check("MYTHOS" in exec_sum, "Executive summary contains MYTHOS branding")
    result.check("END TRANSMISSION" in exec_sum, "Executive summary contains sign-off")
    result.check("MITRE" in exec_sum, "Executive summary references MITRE ATT&CK")

    # Check total findings
    result.check(report.get("total_findings") == 5, f"Total findings is 5 (got: {report.get('total_findings')})")

    result.duration_ms = (time.time() - start) * 1000
    return result


# ──────────────────────────────────────────────────────────────────────
# TEST RUNNER
# ──────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 70)
    print("  MYTHOS AGENT — COMPREHENSIVE TEST SUITE")
    print("  Defensive Cyber Intelligence Analyst for NEXUS-X")
    print("=" * 70)

    tests = [
        test_stride_threat_model,
        test_code_vulnerability_detection,
        test_network_posture_tools,
        test_log_anomaly_detection,
        test_incident_report_generation,
    ]

    results = []
    total_start = time.time()

    for test_fn in tests:
        try:
            result = test_fn()
            results.append(result)
            print(result.summary())
        except Exception as e:
            failed = TestResult(test_fn.__name__)
            failed.passed = False
            failed.error = str(e)
            failed.check(False, f"Test crashed: {e}")
            results.append(failed)
            print(failed.summary())

    total_duration = (time.time() - total_start) * 1000

    # Final Summary
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    all_checks = sum(len(r.checks) for r in results)
    passed_checks = sum(sum(1 for c in r.checks if c["status"] == "PASS") for r in results)

    print("\n" + "=" * 70)
    print(f"  FINAL RESULTS: {passed}/{total} tests passed | {passed_checks}/{all_checks} checks passed")
    print(f"  Total Duration: {total_duration:.0f}ms")
    print("=" * 70)

    # Print detailed output for key tests
    print("\n" + "-" * 70)
    print("  SAMPLE OUTPUT: STRIDE Assessment")
    print("-" * 70)
    stride_result = results[0].output
    if stride_result and "result" in stride_result:
        threats = stride_result["result"].get("threats", {})
        for key in "STRIDE":
            threat = threats.get(key, {})
            severity = threat.get("severity", "N/A")
            codename = SEVERITY_MAP.get(severity, {}).get("codename", "N/A")
            print(f"  [{key}] [{codename}] {threat.get('threat', 'N/A')[:80]}")
        print(f"  Overall Risk: {stride_result['result'].get('overall_risk', 'N/A')}")
        print(f"  Confidence: {stride_result['result'].get('confidence', 'N/A')}%")

    print("\n" + "-" * 70)
    print("  SAMPLE OUTPUT: Code Scan Findings")
    print("-" * 70)
    code_result = results[1].output
    if code_result:
        for f in code_result.get("findings", [])[:6]:
            codename = f.get("codename", "?")
            print(f"  [{codename}] {f['vulnerability']} — Line {f.get('line', '?')}: {f.get('owasp', '')}")
        print(f"  Overall Risk: {code_result.get('overall_risk', 'N/A')} ({code_result.get('overall_codename', '')})")

    print("\n" + "-" * 70)
    print("  SAMPLE OUTPUT: Log Anomaly Detection")
    print("-" * 70)
    log_result = results[3].output
    if log_result:
        for a in log_result.get("anomalies", []):
            print(f"  [{a.get('codename', '?')}] {a['type']}: {a.get('detail', '')[:70]}")
        print(f"  Overall Risk: {log_result.get('overall_risk', 'N/A')}")

    print("\n" + "-" * 70)
    print("  SAMPLE OUTPUT: Incident Report (Executive Summary)")
    print("-" * 70)
    report_result = results[4].output
    if report_result:
        exec_sum = report_result.get("executive_summary", "")
        # Print first 20 lines
        for line in exec_sum.split("\n")[:20]:
            print(f"  {line}")

    print("\n" + "=" * 70)
    print("  — MYTHOS // END TRANSMISSION")
    print("=" * 70)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
